import requests
import json
import time
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from statistics import mean
import csv
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

try:
    from tqdm import tqdm
except ImportError:
    print("提示: 安装 tqdm 库以获得进度条显示: pip install tqdm")
    def tqdm(iterable, **kwargs):
        return iterable

# API 配置
API_BASE_URL = "https://api2.openreview.net/notes"
LIMIT = 1000  # 每页评论数量
MAX_WORKERS = 50  # 最大线程数
INITIAL_DELAY = 0.1  # 初始请求延迟（秒）

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_BACKOFF_FACTOR = 0.5  # 退避因子
RETRY_STATUS_FORCELIST = [500, 502, 503, 504, 429]  # 需要重试的状态码

# 请求头
HEADERS = {
    "Accept": "application/json,text/*;q=0.99",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Referer": "https://openreview.net/",
    "Origin": "https://openreview.net"
}

@dataclass
class PaperRatingInfo:
    """论文评分信息"""
    paper_id: str
    ratings: List[int]
    min_rating: Optional[int]
    max_rating: Optional[int]
    avg_rating: Optional[float]
    reviewer_count: int

class RatingExtractor:
    """从评论中提取评分的工具类"""

    # 评分模式
    RATING_PATTERNS = [
        r'Rating:\s*(\d+)',
        r'评分[:：]\s*(\d+)',
        r'rating[:：]\s*(\d+)',
        r'(\d+)\s*/\s*10',
        r'(\d+)\s*out\s*of\s*10',
        r'Overall\s*Rating[:：]\s*(\d+)',
        r'Overall[:：]\s*(\d+)',
        r'Recommendation[:：]\s*(\d+)',
    ]

    @staticmethod
    def extract_rating_from_text(text: str) -> Optional[int]:
        """从文本中提取评分"""
        if not text:
            return None

        for pattern in RatingExtractor.RATING_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    rating = int(matches[0])
                    # 确保评分在合理范围内 (1-10)
                    if 1 <= rating <= 10:
                        return rating
                except ValueError:
                    continue

        # 特殊处理: 直接查找 1-10 的数字
        numbers = re.findall(r'\b([1-9]|10)\b', text)
        if numbers and len(numbers) == 1:
            try:
                return int(numbers[0])
            except ValueError:
                pass

        return None

class ICLR26RatingCrawler:
    """ICLR 2026 评论和评分爬虫"""

    def __init__(self, max_workers: int = MAX_WORKERS, delay: float = INITIAL_DELAY):
        """
        初始化爬虫

        Args:
            max_workers: 最大线程数
            delay: API请求延迟时间（秒）
        """
        self.max_workers = max_workers
        self.delay = delay
        self.rating_extractor = RatingExtractor()
        self.lock = threading.Lock()
        self.results = []
        self.failed_papers = []

        # 设置重试策略
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=RETRY_STATUS_FORCELIST,
            allowed_methods=["GET"]
        )

        # 创建会话并配置重试
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch_paper_comments(self, paper_id: str) -> Optional[Dict]:
        """
        获取论文的所有评论（带重试机制）

        Args:
            paper_id: 论文ID

        Returns:
            API响应数据或None
        """
        params = {
            "count": "true",
            "details": "writable,signatures,invitation,presentation,tags",
            "domain": "ICLR.cc/2026/Conference",
            "forum": paper_id,
            "limit": LIMIT,
            "trash": "true"
        }

        url = f"{API_BASE_URL}?{requests.compat.urlencode(params)}"

        try:
            # 使用配置了重试的会话
            response = self.session.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取论文 {paper_id} 评论失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ 解析论文 {paper_id} 响应JSON失败: {e}")
            return None
        except Exception as e:
            print(f"❌ 获取论文 {paper_id} 时发生未知错误: {e}")
            return None

    def extract_ratings_from_comments(self, comments_data: Dict) -> List[int]:
        """
        从评论数据中提取评分

        Args:
            comments_data: 评论数据

        Returns:
            评分列表
        """
        ratings = []
        notes = comments_data.get("notes", [])

        for note in notes:
            # 获取评论内容
            content = note.get("content", {})

            # 直接提取rating字段 (标准ICLR评分格式)
            rating_field = content.get("rating", {})
            if isinstance(rating_field, dict):
                rating_value = rating_field.get("value")
            else:
                rating_value = rating_field

            # ICLR评分是0-10的整数
            if rating_value is not None and isinstance(rating_value, int) and 0 <= rating_value <= 10:
                ratings.append(rating_value)

        return ratings

    def process_single_paper(self, paper_id: str, max_retries: int = 3) -> Optional[PaperRatingInfo]:
        """
        处理单篇论文（带重试机制）

        Args:
            paper_id: 论文ID
            max_retries: 最大重试次数

        Returns:
            论文评分信息或None
        """
        for attempt in range(max_retries):
            try:
                # 获取评论数据
                comments_data = self.fetch_paper_comments(paper_id)
                if not comments_data:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 0.5  # 指数退避
                        print(f"⚠️  论文 {paper_id} 第 {attempt + 1} 次尝试失败，等待 {wait_time:.1f} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return None

                # 提取评分
                ratings = self.extract_ratings_from_comments(comments_data)

                if not ratings:
                    return PaperRatingInfo(
                        paper_id=paper_id,
                        ratings=[],
                        min_rating=None,
                        max_rating=None,
                        avg_rating=None,
                        reviewer_count=0
                    )

                # 计算统计信息
                return PaperRatingInfo(
                    paper_id=paper_id,
                    ratings=ratings,
                    min_rating=min(ratings),
                    max_rating=max(ratings),
                    avg_rating=round(mean(ratings), 2),
                    reviewer_count=len(ratings)
                )

            except Exception as e:
                print(f"❌ 处理论文 {paper_id} 第 {attempt + 1} 次尝试时出错: {e}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 0.5  # 指数退避
                    print(f"   等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"   论文 {paper_id} 处理失败，已重试 {max_retries} 次")
                    return None

        return None

    def process_papers_batch(self, paper_ids: List[str]) -> List[PaperRatingInfo]:
        """
        批量处理论文（多线程）

        Args:
            paper_ids: 论文ID列表

        Returns:
            论文评分信息列表
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_paper = {
                executor.submit(self.process_single_paper, paper_id): paper_id
                for paper_id in paper_ids
            }

            # 处理完成的任务
            for future in tqdm(as_completed(future_to_paper), total=len(paper_ids), desc="处理进度"):
                paper_id = future_to_paper[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    else:
                        self.failed_papers.append(paper_id)
                except Exception as e:
                    print(f"❌ 处理论文 {paper_id} 时出错: {e}")
                    self.failed_papers.append(paper_id)

                # 控制请求频率
                time.sleep(self.delay)

        return results

    def save_results(self, results: List[PaperRatingInfo], output_file: str = "iclr26_ratings.json"):
        """
        保存结果到文件

        Args:
            results: 论文评分信息列表
            output_file: 输出文件名
        """
        # 转换为字典格式
        data = []
        for result in results:
            data.append({
                "paper_id": result.paper_id,
                "ratings": result.ratings,
                "min_rating": result.min_rating,
                "max_rating": result.max_rating,
                "avg_rating": result.avg_rating,
                "reviewer_count": result.reviewer_count
            })

        # 保存为JSON
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 JSON 文件已保存: {output_file}")
            print(f"   总计: {len(results)} 篇论文的评分信息")
        except Exception as e:
            print(f"❌ 保存JSON文件失败: {e}")

        # 保存为CSV
        csv_file = output_file.replace(".json", ".csv")
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["paper_id", "ratings", "min_rating", "max_rating", "avg_rating", "reviewer_count"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for item in data:
                    row = item.copy()
                    row["ratings"] = "; ".join(map(str, row["ratings"]))
                    writer.writerow(row)

            print(f"💾 CSV 文件已保存: {csv_file}")
        except Exception as e:
            print(f"❌ 保存CSV文件失败: {e}")

    def load_paper_ids_from_json(self, json_file: str) -> List[str]:
        """
        从JSON文件加载论文ID列表

        Args:
            json_file: JSON文件路径

        Returns:
            论文ID列表
        """
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                papers = json.load(f)

            paper_ids = []
            for paper in papers:
                paper_id = paper.get("paper_id")
                if paper_id:
                    paper_ids.append(paper_id)

            print(f"📄 从 {json_file} 加载了 {len(paper_ids)} 个论文ID")
            return paper_ids

        except Exception as e:
            print(f"❌ 加载论文ID失败: {e}")
            return []

    def run(self, paper_ids: List[str], output_file: str = "iclr26_ratings.json"):
        """
        运行爬虫

        Args:
            paper_ids: 论文ID列表
            output_file: 输出文件名
        """
        if not paper_ids:
            print("⚠️ 没有论文ID需要处理")
            return

        print("=" * 60)
        print(" ICLR 2026 Ratings Crawler")
        print("=" * 60)
        print(f"待处理论文数量: {len(paper_ids)}")
        print(f"线程数: {self.max_workers}")
        print(f"输出文件: {output_file}")
        print("-" * 60)
        print("⏳ 开始获取评论和评分...")

        # 处理论文
        start_time = time.time()
        results = self.process_papers_batch(paper_ids)
        end_time = time.time()

        print("-" * 60)
        print(f"✅ 处理完成!")
        print(f"   - 成功: {len(results)} 篇论文")
        print(f"   - 失败: {len(self.failed_papers)} 篇论文")
        print(f"   - 耗时: {end_time - start_time:.2f} 秒")

        if results:
            # 保存结果
            self.save_results(results, output_file)

            # 显示统计信息
            self.show_statistics(results)

        if self.failed_papers:
            print(f"⚠️  失败的论文ID: {self.failed_papers[:10]}...")  # 只显示前10个

    def show_statistics(self, results: List[PaperRatingInfo]):
        """
        显示统计信息

        Args:
            results: 论文评分信息列表
        """
        print("-" * 60)
        print("📊 统计信息:")

        # 有评分的论文数量
        papers_with_ratings = [r for r in results if r.ratings]
        print(f"   - 有评分的论文: {len(papers_with_ratings)} / {len(results)}")

        if papers_with_ratings:
            # 评分分布
            all_ratings = []
            for result in papers_with_ratings:
                all_ratings.extend(result.ratings)

            if all_ratings:
                print(f"   - 总评分数量: {len(all_ratings)}")
                print(f"   - 平均评分: {mean(all_ratings):.2f}")
                print(f"   - 最低评分: {min(all_ratings)}")
                print(f"   - 最高评分: {max(all_ratings)}")

                # 评分分布
                rating_counts = {}
                for rating in all_ratings:
                    rating_counts[rating] = rating_counts.get(rating, 0) + 1

                print(f"   - 评分分布:")
                for rating in sorted(rating_counts.keys()):
                    count = rating_counts[rating]
                    percentage = (count / len(all_ratings)) * 100
                    print(f"     {rating}分: {count} ({percentage:.1f}%)")

def main():
    """主函数"""
    try:
        # 创建爬虫实例
        crawler = ICLR26RatingCrawler(max_workers=MAX_WORKERS, delay=INITIAL_DELAY)

        # 从已有的论文数据文件加载论文ID
        paper_ids = crawler.load_paper_ids_from_json("iclr26_all_papers.json")

        if not paper_ids:
            print("❌ 没有找到论文ID，请先运行 request_iclr26.py 获取论文数据")
            return 1

        # 运行爬虫
        crawler.run(paper_ids, "iclr26_ratings.json")

        print("=" * 60)
        print("✨ 所有任务完成!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n❌ 用户中断操作")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())