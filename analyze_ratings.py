#!/usr/bin/env python3
"""
ICLR 2026 评分数据深度分析
分析所有论文的评分分布、统计特征和趋势
"""

import json
import statistics
from collections import Counter, defaultdict

def load_ratings_data(filepath):
    """加载评分数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

def basic_statistics(ratings_data):
    """基础统计分析"""
    print("=" * 60)
    print("📊 ICLR 2026 评分数据基础统计")
    print("=" * 60)

    total_papers = len(ratings_data)
    total_ratings = sum(paper['reviewer_count'] for paper in ratings_data)

    # 提取所有评分用于分析
    all_ratings = []
    avg_ratings = []
    min_ratings = []
    max_ratings = []
    reviewer_counts = []

    for paper in ratings_data:
        all_ratings.extend(paper['ratings'])
        avg_ratings.append(paper['avg_rating'])
        min_ratings.append(paper['min_rating'])
        max_ratings.append(paper['max_rating'])
        reviewer_counts.append(paper['reviewer_count'])

    print(f"📄 总论文数量: {total_papers:,} 篇")
    print(f"⭐ 总评分数量: {total_ratings:,} 个")
    print(f"📊 平均评分: {statistics.mean(all_ratings):.2f}")
    print(f"📈 评分中位数: {statistics.median(all_ratings):.2f}")
    print(f"📉 评分标准差: {statistics.stdev(all_ratings):.2f}")
    print(f"🔢 评分范围: {min(all_ratings)} - {max(all_ratings)}")
    print()

    print("📋 平均分统计:")
    print(f"  平均分均值: {statistics.mean(avg_ratings):.2f}")
    print(f"  平均分中位数: {statistics.median(avg_ratings):.2f}")
    print(f"  平均分标准差: {statistics.stdev(avg_ratings):.2f}")
    print(f"  平均分范围: {min(avg_ratings):.2f} - {max(avg_ratings):.2f}")
    print()

    print("📈 最高分和最低分统计:")
    print(f"  最低分均值: {statistics.mean(min_ratings):.2f}")
    print(f"  最高分均值: {statistics.mean(max_ratings):.2f}")
    print()

    print("👥 评审人数统计:")
    print(f"  平均评审人数: {statistics.mean(reviewer_counts):.2f}")
    print(f"  评审人数范围: {min(reviewer_counts)} - {max(reviewer_counts)}")

    return {
        'all_ratings': all_ratings,
        'avg_ratings': avg_ratings,
        'min_ratings': min_ratings,
        'max_ratings': max_ratings,
        'reviewer_counts': reviewer_counts
    }

def rating_distribution_analysis(all_ratings):
    """评分分布分析"""
    print("\n" + "=" * 60)
    print("📈 评分分布分析")
    print("=" * 60)

    rating_counter = Counter(all_ratings)
    total_ratings = len(all_ratings)

    print("📊 各分数段分布:")
    for rating in sorted(rating_counter.keys()):
        count = rating_counter[rating]
        percentage = (count / total_ratings) * 100
        bar_length = int(percentage / 2)  # 缩放到合适长度
        bar = "█" * bar_length + "░" * (25 - bar_length)
        print(f"  {rating:2d}分: {count:6,} ({percentage:5.1f}%) |{bar}|")

    print("\n📋 评分分组统计:")
    groups = {
        '0分': rating_counter[0],
        '2分': rating_counter[2],
        '4分': rating_counter[4],
        '6分': rating_counter[6],
        '8分': rating_counter[8],
        '10分': rating_counter[10]
    }

    for group, count in groups.items():
        percentage = (count / total_ratings) * 100
        print(f"  {group}: {count:,} ({percentage:.1f}%)")

def avg_rating_distribution_analysis(avg_ratings):
    """平均分分布分析"""
    print("\n" + "=" * 60)
    print("📊 平均分分布分析")
    print("=" * 60)

    # 分段统计
    ranges = {
        "0.0-1.9": 0, "2.0-2.9": 0, "3.0-3.9": 0, "4.0-4.9": 0,
        "5.0-5.9": 0, "6.0-6.9": 0, "7.0-7.9": 0, "8.0-8.5": 0
    }

    for avg in avg_ratings:
        if 0.0 <= avg <= 1.9:
            ranges["0.0-1.9"] += 1
        elif 2.0 <= avg <= 2.9:
            ranges["2.0-2.9"] += 1
        elif 3.0 <= avg <= 3.9:
            ranges["3.0-3.9"] += 1
        elif 4.0 <= avg <= 4.9:
            ranges["4.0-4.9"] += 1
        elif 5.0 <= avg <= 5.9:
            ranges["5.0-5.9"] += 1
        elif 6.0 <= avg <= 6.9:
            ranges["6.0-6.9"] += 1
        elif 7.0 <= avg <= 7.9:
            ranges["7.0-7.9"] += 1
        elif 8.0 <= avg <= 8.5:
            ranges["8.0-8.5"] += 1

    total_papers = len(avg_ratings)
    print("📈 平均分区间分布:")
    for range_name, count in ranges.items():
        percentage = (count / total_papers) * 100
        bar_length = int(percentage / 2)
        bar = "█" * bar_length + "░" * (25 - bar_length)
        print(f"  {range_name}: {count:4,} ({percentage:5.1f}%) |{bar}|")

def reviewer_analysis(reviewer_counts):
    """评审人数分析"""
    print("\n" + "=" * 60)
    print("👥 评审人数分析")
    print("=" * 60)

    reviewer_counter = Counter(reviewer_counts)
    total_papers = len(reviewer_counts)

    print("📊 评审人数分布:")
    for num_reviewers in sorted(reviewer_counter.keys()):
        count = reviewer_counter[num_reviewers]
        percentage = (count / total_papers) * 100
        print(f"  {num_reviewers}位评审: {count:4,}篇论文 ({percentage:5.1f}%)")

def high_rated_papers_analysis(avg_ratings):
    """高评分论文分析"""
    print("\n" + "=" * 60)
    print("⭐ 高评分论文分析")
    print("=" * 60)

    # 定义高评分标准
    high_rated = [avg for avg in avg_ratings if avg >= 6.0]
    very_high_rated = [avg for avg in avg_ratings if avg >= 8.0]

    print(f"📈 平均分≥6.0的论文: {len(high_rated):,}篇 ({len(high_rated)/len(avg_ratings)*100:.1f}%)")
    print(f"📈 平均分≥8.0的论文: {len(very_high_rated):,}篇 ({len(very_high_rated)/len(avg_ratings)*100:.1f}%)")

    # 找出最高分论文
    max_rating = max(avg_ratings)
    max_count = sum(1 for avg in avg_ratings if avg == max_rating)
    print(f"🏆 最高平均分: {max_rating:.2f}分 ({max_count}篇论文)")

    # 统计各个高分段
    score_ranges = {
        "6.0-6.9": sum(1 for avg in avg_ratings if 6.0 <= avg < 7.0),
        "7.0-7.9": sum(1 for avg in avg_ratings if 7.0 <= avg < 8.0),
        "8.0-8.5": sum(1 for avg in avg_ratings if 8.0 <= avg <= 8.5)
    }

    print("\n📊 高分段分布:")
    for range_name, count in score_ranges.items():
        percentage = (count / len(avg_ratings)) * 100
        print(f"  {range_name}分: {count:,}篇 ({percentage:.1f}%)")

def extreme_cases_analysis(ratings_data):
    """极端案例分析"""
    print("\n" + "=" * 60)
    print("🎯 极端案例分析")
    print("=" * 60)

    # 找出评分最高和最低的论文
    highest_rated = max(ratings_data, key=lambda x: x['avg_rating'])
    lowest_rated = min(ratings_data, key=lambda x: x['avg_rating'])

    print("🏆 评分最高论文:")
    print(f"  论文ID: {highest_rated['paper_id']}")
    print(f"  平均分: {highest_rated['avg_rating']:.2f}")
    print(f"  评分范围: {highest_rated['min_rating']} - {highest_rated['max_rating']}")
    print(f"  评审人数: {highest_rated['reviewer_count']}")
    print(f"  详细评分: {highest_rated['ratings']}")

    print("\n📉 评分最低论文:")
    print(f"  论文ID: {lowest_rated['paper_id']}")
    print(f"  平均分: {lowest_rated['avg_rating']:.2f}")
    print(f"  评分范围: {lowest_rated['min_rating']} - {lowest_rated['max_rating']}")
    print(f"  评审人数: {lowest_rated['reviewer_count']}")
    print(f"  详细评分: {lowest_rated['ratings']}")

    # 找出评审人数最多和最少的论文
    most_reviewed = max(ratings_data, key=lambda x: x['reviewer_count'])
    least_reviewed = min(ratings_data, key=lambda x: x['reviewer_count'])

    print(f"\n👥 评审人数最多: {most_reviewed['reviewer_count']}位评审 (论文ID: {most_reviewed['paper_id']})")
    print(f"👤 评审人数最少: {least_reviewed['reviewer_count']}位评审 (论文ID: {least_reviewed['paper_id']})")

def quality_indicators_analysis(ratings_data):
    """质量指标分析"""
    print("\n" + "=" * 60)
    print("📋 质量指标分析")
    print("=" * 60)

    # 计算各种质量指标
    consistent_papers = []  # 评分一致的论文
    controversial_papers = []  # 评分差异大的论文

    for paper in ratings_data:
        ratings = paper['ratings']
        if len(set(ratings)) == 1:  # 所有评分相同
            consistent_papers.append(paper)
        elif paper['max_rating'] - paper['min_rating'] >= 6:  # 评分差异≥6分
            controversial_papers.append(paper)

    print(f"✅ 评分完全一致论文: {len(consistent_papers):,}篇 ({len(consistent_papers)/len(ratings_data)*100:.1f}%)")
    print(f"⚡ 评分差异≥6分论文: {len(controversial_papers):,}篇 ({len(controversial_papers)/len(ratings_data)*100:.1f}%)")

    # 分析评分差异分布
    rating_spreads = [paper['max_rating'] - paper['min_rating'] for paper in ratings_data]
    print(f"\n📊 评分差异统计:")
    print(f"  平均评分差异: {statistics.mean(rating_spreads):.2f}分")
    print(f"  中位数评分差异: {statistics.median(rating_spreads):.2f}分")
    print(f"  最大评分差异: {max(rating_spreads)}分")

def main():
    """主函数"""
    print("🚀 ICLR 2026 评分数据深度分析报告")
    print("=" * 80)

    # 加载数据
    ratings_data = load_ratings_data('./data/iclr26_ratings.json')
    if not ratings_data:
        return

    print(f"✅ 成功加载 {len(ratings_data)} 篇论文的评分数据")

    # 基础统计分析
    stats_data = basic_statistics(ratings_data)

    # 详细分析
    rating_distribution_analysis(stats_data['all_ratings'])
    avg_rating_distribution_analysis(stats_data['avg_ratings'])
    reviewer_analysis(stats_data['reviewer_counts'])
    high_rated_papers_analysis(stats_data['avg_ratings'])
    extreme_cases_analysis(ratings_data)
    quality_indicators_analysis(ratings_data)

    print("\n" + "=" * 80)
    print("✅ 分析完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()