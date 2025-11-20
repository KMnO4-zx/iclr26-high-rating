#!/usr/bin/env python3
"""
创建只包含高评分ICLR 2026论文的HTML页面
展示平均分≥6分且最低分≥5分的论文
"""

import json

def get_rating_html(paper):
    """生成论文评分的HTML显示"""
    if 'avg_rating' not in paper or paper['avg_rating'] is None:
        return ''

    avg_rating = paper['avg_rating']
    min_rating = paper.get('min_rating', 'N/A')
    max_rating = paper.get('max_rating', 'N/A')
    reviewer_count = paper.get('reviewer_count', 0)
    ratings = paper.get('ratings', [])

    # 确定评分等级颜色
    if avg_rating >= 8:
        rating_class = 'high'
    elif avg_rating >= 6:
        rating_class = 'medium'
    else:
        rating_class = 'low'

    ratings_html = f'''
        <div class="paper-ratings">
            <div class="ratings-title">📊 评审评分</div>
            <div class="ratings-details">
                <div class="rating-item">
                    <span class="rating-label">平均分:</span>
                    <span class="rating-value {rating_class}">{avg_rating:.2f}</span>
                </div>
                <div class="rating-item">
                    <span class="rating-label">最低分:</span>
                    <span class="rating-value {rating_class}">{min_rating}</span>
                </div>
                <div class="rating-item">
                    <span class="rating-label">最高分:</span>
                    <span class="rating-value {rating_class}">{max_rating}</span>
                </div>
                <div class="rating-item">
                    <span class="rating-label">评审人数:</span>
                    <span class="rating-value {rating_class}">{reviewer_count}</span>
                </div>
            </div>'''

    if ratings:
        ratings_html += f'''
            <div class="individual-ratings">
                详细评分: {', '.join(map(str, ratings))}
            </div>'''

    ratings_html += '</div>'
    return ratings_html

def create_high_rated_html():
    """创建只包含高评分论文的HTML页面"""

    # 读取高评分论文数据
    with open('./data/high_rated_papers.json', 'r', encoding='utf-8') as f:
        papers_data = json.load(f)

    # 按平均评分降序排序
    papers_data.sort(key=lambda x: x['avg_rating'], reverse=True)

    # 创建HTML内容
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ICLR 2026 高评分论文集 - 平均分≥6分且最低分≥5分</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #2c3e50;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #3498db;
        }}

        .header h1 {{
            font-size: 2.5rem;
            color: #2c3e50;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header .subtitle {{
            font-size: 1.2rem;
            color: #7f8c8d;
            margin-bottom: 15px;
        }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}

        .stat-item {{
            text-align: center;
            padding: 15px 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}

        .stat-number {{
            font-size: 1.8rem;
            font-weight: bold;
            color: #2c3e50;
            display: block;
        }}

        .stat-label {{
            font-size: 0.9rem;
            color: #7f8c8d;
            margin-top: 5px;
        }}

        .section {{
            margin: 40px 0;
        }}

        .section-title {{
            font-size: 1.5rem;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
            font-weight: 600;
        }}

        .section-count {{
            color: #7f8c8d;
            font-size: 1rem;
            font-weight: normal;
        }}

        .paper-card {{
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            page-break-inside: avoid;
        }}

        .paper-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            line-height: 1.3;
        }}

        .paper-authors {{
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-bottom: 10px;
            font-style: italic;
        }}

        .paper-abstract {{
            color: #2c3e50;
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 12px;
            text-align: justify;
        }}

        .paper-link {{
            display: inline-block;
            padding: 6px 12px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 500;
            transition: background-color 0.3s ease;
            margin-right: 8px;
        }}

        .paper-link:hover {{
            background: #2980b9;
        }}

        .paper-ratings {{
            margin: 12px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #3498db;
        }}

        .ratings-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 6px;
        }}

        .ratings-details {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }}

        .rating-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.8rem;
            color: #000000;
        }}

        .rating-label {{
            font-weight: 500;
            color: #7f8c8d;
        }}

        .rating-value {{
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 4px;
            color: white;
        }}

        .rating-value.high {{ background: #27ae60; }}
        .rating-value.medium {{ background: #f39c12; }}
        .rating-value.low {{ background: #e74c3c; }}

        .individual-ratings {{
            font-size: 0.75rem;
            color: #7f8c8d;
            margin-top: 5px;
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
        }}

        .download-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
            text-align: center;
        }}

        .download-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: #27ae60;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
            font-weight: 500;
            transition: background-color 0.3s ease;
        }}

        .download-btn:hover {{
            background: #229954;
        }}

        @media print {{
            body {{
                background: white !important;
                padding: 10px !important;
            }}

            .container {{
                box-shadow: none !important;
                padding: 10px !important;
            }}

            .paper-card {{
                break-inside: avoid;
                page-break-inside: avoid;
                margin-bottom: 10px !important;
                padding: 15px !important;
            }}

            .section {{
                page-break-before: always;
            }}

            .download-section {{
                display: none !important;
            }}
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}

            .header h1 {{
                font-size: 2rem;
            }}

            .stats {{
                flex-direction: column;
                align-items: center;
            }}

            .paper-card {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ICLR 2026 高评分论文</h1>
            <div class="subtitle">精选高评分投稿论文</div>
            <div class="subtitle">平均分≥6分且最低分≥5分</div>

            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{len(papers_data)}</span>
                    <span class="stat-label">高评分论文</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{papers_data[0]['avg_rating']:.2f}</span>
                    <span class="stat-label">最高平均分</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{papers_data[-1]['avg_rating']:.2f}</span>
                    <span class="stat-label">最低平均分</span>
                </div>
            </div>
        </div>
'''

    # 添加高评分论文部分（按评分排序）
    html_content += f'''
        <div class="section">
            <h2 class="section-title">
                高评分论文 <span class="section-count">({len(papers_data)}篇)</span>
                <span style="font-size: 0.8em; color: #7f8c8d; margin-left: 10px;">（按平均评分排序）</span>
            </h2>
'''

    for i, paper in enumerate(papers_data):
        authors = ', '.join(paper['authors'])
        abstract = paper['abstract']
        rating_html = get_rating_html(paper)

        html_content += f'''
            <div class="paper-card">
                <div class="paper-title">{i+1}. {paper['title']}</div>
                <div class="paper-authors">作者: {authors}</div>
                <div class="paper-abstract">{abstract}</div>
                {rating_html}
                <a href="{paper['forum_url']}" class="paper-link" target="_blank">📄 openreview</a>
                <a href="{paper['pdf_url']}" class="paper-link" target="_blank">📄 下载PDF</a>
            </div>
        '''

    html_content += '''
        </div>

        <div class="footer">
            <p><strong>ICLR 2026 高评分论文集</strong></p>
            <p>筛选条件: 平均分≥6分且最低分≥5分</p>
            <p>数据来源: OpenReview官方平台</p>
            <p>数据更新时间: 2025年11月20日</p>
        </div>
    </div>
</body>
</html>'''

    # 保存HTML文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"高评分论文HTML页面已创建")
    print(f"页面包含 {len(papers_data)} 篇高评分论文（平均分≥6分且最低分≥5分）")
    print(f"平均分范围: {papers_data[-1]['avg_rating']:.2f} - {papers_data[0]['avg_rating']:.2f}")

    return 'index.html'

if __name__ == "__main__":
    create_high_rated_html()