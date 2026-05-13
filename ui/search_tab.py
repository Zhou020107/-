import streamlit as st
import pandas as pd
from datetime import datetime
from scraper.manager import ScraperManager
from classifier import classify_education, parse_salary, classify_salary_range, classify_location, detect_tech_stack, detect_welfare


def render():
    """搜索爬取页面"""
    st.header("🔍 搜索职位")

    col1, col2 = st.columns([3, 1])
    with col1:
        keyword = st.text_input("关键词", placeholder="例: Python 后端 实习", key="search_keyword")
    with col2:
        max_pages = st.number_input("最大页数", min_value=1, max_value=10, value=3, key="max_pages")

    col3, col4 = st.columns(2)
    with col3:
        location = st.text_input("工作地点（留空=全国）", placeholder="例: 北京", key="search_location")
    with col4:
        sites_enabled = st.multiselect(
            "目标网站",
            options=["51job", "国家大学生就业服务平台"],
            default=["51job", "国家大学生就业服务平台"],
            key="search_sites",
        )

    if st.button("🚀 开始搜索", type="primary", use_container_width=True, disabled=not keyword):
        _do_search(keyword, location, max_pages, sites_enabled)


def _do_search(keyword: str, location: str, max_pages: int, sites: list):
    """执行搜索"""
    manager = ScraperManager()
    db = st.session_state.db

    progress_bar = st.progress(0)
    status_text = st.empty()
    result_container = st.container()

    all_items = []
    seen_urls = set()

    site_results = {}
    for site in sites:
        site_results[site] = {'status': 'waiting', 'count': 0}

    for i, item in enumerate(manager.search_all(keyword, location, max_pages)):
        if item.get('url') in seen_urls:
            continue
        seen_urls.add(item.get('url', ''))

        # 分类
        item['education'] = classify_education(
            item.get('title', ''), item.get('description', ''), item.get('education', '')
        )
        salary_min, salary_max = parse_salary(item.get('salary_text', ''))
        item['salary_min'] = salary_min
        item['salary_max'] = salary_max
        item['salary_range'] = classify_salary_range(salary_min, salary_max)

        city, tier = classify_location(item.get('location', ''))
        item['city'] = city
        item['location_tier'] = tier

        item['tech_stack'] = detect_tech_stack(
            item.get('title', ''), item.get('description', ''), keyword=keyword
        )
        item['tech_stack'] = ','.join(item['tech_stack']) if item.get('tech_stack') else ''

        # 福利检测
        welfare = detect_welfare(
            item.get('description', ''),
            item.get('rec_tags', '')
        )
        item['is_accept_graduate'] = item.get('is_accept_graduate', welfare['is_accept_graduate'])
        item['has_weekend_off'] = welfare['has_weekend_off']
        item['has_insurance'] = welfare['has_insurance']

        item['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        all_items.append(item)

        # 阶段性存入数据库（每10条写入一次）
        if len(all_items) % 10 == 0 and all_items:
            db.upsert_jobs(all_items[-10:])

        # 更新进度
        percentage = min(len(all_items) / (max_pages * 20 * len(sites)), 0.95)
        progress_bar.progress(percentage)
        status_text.text(f"已采集 {len(all_items)} 条职位信息...")

    # 写入剩余数据
    if all_items:
        new_count = db.upsert_jobs(all_items)
        progress_bar.progress(1.0)
        status_text.text(f"✅ 搜索完成！共采集 {len(all_items)} 条，新增 {new_count} 条")

        # 实时预览
        with result_container:
            st.subheader(f"📋 搜索结果 ({len(all_items)} 条)")
            preview_df = pd.DataFrame(all_items)
            display_cols = ['title', 'company', 'location', 'salary_text', 'education', 'source']
            display_cols = [c for c in display_cols if c in preview_df.columns]
            st.dataframe(preview_df[display_cols], use_container_width=True)
    else:
        progress_bar.progress(1.0)
        status_text.text("⚠️ 未找到匹配的职位信息")
