#!/usr/bin/env python3
"""
创建包含所有ICLR 2025论文核心信息的HTML页面
"""

import json

def create_simple_html_page():
    """创建简洁的HTML页面，包含所有论文的核心信息"""
    
    # 读取论文数据
    with open('./iclr25_all_papers.json', 'r', encoding='utf-8') as f:
        papers_data = json.load(f)
    
    # 按类型分组论文
    oral_papers = [p for p in papers_data if p['type'] == 'oral']
    spotlight_papers = [p for p in papers_data if p['type'] == 'spotlight']
    poster_papers = [p for p in papers_data if p['type'] == 'poster']
    
    # 创建HTML内容
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ICLR 2025 论文集 - 全部接收论文</title>
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
        
        .paper-type {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .paper-type.oral {{
            background: #e74c3c;
            color: white;
        }}
        
        .paper-type.spotlight {{
            background: #f39c12;
            color: white;
        }}
        
        .paper-type.poster {{
            background: #27ae60;
            color: white;
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
        }}
        
        .paper-link:hover {{
            background: #2980b9;
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
            <h1>ICLR 2025</h1>
            <div class="subtitle">第13届 ICLR 会议论文集</div>
            <div class="subtitle">完整收录所有接收论文</div>
            
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{len(oral_papers)}</span>
                    <span class="stat-label">Oral论文</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(spotlight_papers)}</span>
                    <span class="stat-label">Spotlight论文</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(poster_papers)}</span>
                    <span class="stat-label">Poster论文</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(papers_data)}</span>
                    <span class="stat-label">总论文数</span>
                </div>
            </div>
        </div>

        <div class="download-section">
            <h3>📥 数据下载</h3>
            <p>获取完整的论文数据集和PDF报告</p>
            <a href="iclr25_all_papers.json" class="download-btn" download>📄 JSON数据集</a>
            <a href="iclr25_all_papers_complete.csv" class="download-btn" download>📊 CSV数据集</a>
            <a href="README.md" class="download-btn" download>📖 使用说明</a>
        </div>
'''
    
    # 添加Oral论文部分
    html_content += f'''
        <div class="section">
            <h2 class="section-title">
                Oral 论文 <span class="section-count">({len(oral_papers)}篇)</span>
            </h2>
'''
    
    for i, paper in enumerate(oral_papers):
        authors = ', '.join(paper['authors'])
        abstract = paper['abstract']
        
        html_content += f'''
            <div class="paper-card">
                <div class="paper-type oral">Oral</div>
                <div class="paper-title">{i+1}. {paper['title']}</div>
                <div class="paper-authors">作者: {authors}</div>
                <div class="paper-abstract">{abstract}</div>
                <a href="{paper['forum_url']}" class="paper-link" target="_blank">📄 openreview</a>
                <a href="{paper['pdf_url']}" class="paper-link" target="_blank">📄 下载PDF</a>
            </div>
'''
    
    html_content += '''
        </div>
'''
    
    # 添加Spotlight论文部分
    html_content += f'''
        <div class="section">
            <h2 class="section-title">
                Spotlight 论文 <span class="section-count">({len(spotlight_papers)}篇)</span>
            </h2>
'''
    
    for i, paper in enumerate(spotlight_papers):
        authors = ', '.join(paper['authors'])
        abstract = paper['abstract']
        
        html_content += f'''
            <div class="paper-card">
                <div class="paper-type spotlight">Spotlight</div>
                <div class="paper-title">{i+1}. {paper['title']}</div>
                <div class="paper-authors">作者: {authors}</div>
                <div class="paper-abstract">{abstract}</div>
                <a href="{paper['forum_url']}" class="paper-link" target="_blank">📄 openreview</a>
                <a href="{paper['pdf_url']}" class="paper-link" target="_blank">📄 下载PDF</a>
            </div>
'''
    
    html_content += '''
        </div>
'''
    
    # 添加Poster论文部分
    html_content += f'''
        <div class="section">
            <h2 class="section-title">
                Poster 论文 <span class="section-count">({len(poster_papers)}篇)</span>
            </h2>
'''
    
    for i, paper in enumerate(poster_papers):
        authors = ', '.join(paper['authors'])
        abstract = paper['abstract']
        
        html_content += f'''
            <div class="paper-card">
                <div class="paper-type poster">Poster</div>
                <div class="paper-title">{i+1}. {paper['title']}</div>
                <div class="paper-authors">作者: {authors}</div>
                <div class="paper-abstract">{abstract}</div>
                <a href="{paper['forum_url']}" class="paper-link" target="_blank">📄 openreview</a>
                <a href="{paper['pdf_url']}" class="paper-link" target="_blank">📄 下载PDF</a>
            </div>
'''
    
    html_content += '''
        </div>
        
        <div class="footer">
            <p><strong>ICLR 2025 完整论文集</strong></p>
            <p>数据来源: OpenReview官方平台</p>
            <p>会议时间: 2025年5月7-11日 | 地点: 新加坡</p>
            <p>数据更新时间: 2025年11月15日</p>
        </div>
    </div>
</body>
</html>'''
    
    # 保存HTML文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"完整HTML页面已创建")
    print(f"页面包含 {len(papers_data)} 篇ICLR 2025论文的完整信息")
    
    return 'index.html'

if __name__ == "__main__":
    create_simple_html_page()