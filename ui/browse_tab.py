import streamlit as st
import pandas as pd
from classifier.education import EDUCATION_ORDER
from classifier.salary import SALARY_BIN_LABELS
from classifier.location import TIER_MAP


def render():
    """浏览结果页面"""
    st.header("📋 浏览结果")

    db = st.session_state.db
    jobs_df = db.query_jobs()

    if jobs_df.empty:
        st.info("还没有数据，请先去 🔍 搜索爬取 页面搜索职位")
        return

    # 筛选器
    st.subheader("🔎 筛选条件")
    filtered = _render_filters(jobs_df)

    # 统计
    st.subheader(f"📊 筛选结果 ({len(filtered)} 条)")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("总职位", len(filtered))
    with col2:
        st.metric("公司数", filtered['company'].nunique() if 'company' in filtered.columns else 0)
    with col3:
        st.metric("城市数", filtered['location'].nunique() if 'location' in filtered.columns else 0)
    with col4:
        st.metric("平均月薪",
                  f"{int(filtered['salary_min'].mean()):,}" if 'salary_min' in filtered.columns and filtered['salary_min'].notna().any() else "N/A")
    with col5:
        st.metric("招应届",
                  filtered['is_accept_graduate'].sum() if 'is_accept_graduate' in filtered.columns else 0)
    with col6:
        st.metric("五险一金",
                  filtered['has_insurance'].sum() if 'has_insurance' in filtered.columns else 0)

    # 数据表格
    display_cols = ['title', 'company', 'location', 'location_tier', 'salary_text',
                    'salary_range', 'education', 'is_accept_graduate',
                    'has_insurance', 'has_weekend_off', 'tech_stack', 'source', 'post_date']
    display_cols = [c for c in display_cols if c in filtered.columns]
    column_names = {
        'title': '职位名称', 'company': '公司', 'location': '工作地点',
        'location_tier': '城市等级', 'salary_text': '薪资原文',
        'salary_range': '薪资档位', 'education': '学历要求',
        'is_accept_graduate': '招应届', 'has_insurance': '五险一金',
        'has_weekend_off': '双休', 'tech_stack': '技术栈',
        'source': '来源网站', 'post_date': '发布日期',
    }
    # 将布尔列转为勾号
    bool_cols = ['is_accept_graduate', 'has_insurance', 'has_weekend_off']
    for bc in bool_cols:
        if bc in filtered.columns:
            filtered[bc] = filtered[bc].apply(lambda x: '✅' if x else '')
    renamed = filtered[display_cols].rename(columns=column_names)
    st.dataframe(renamed, use_container_width=True, hide_index=True)

    # 详情查看
    st.subheader("🔍 查看详情")
    selected_title = st.selectbox("选择职位查看详情", filtered['title'].tolist() if len(filtered) > 0 else [])
    if selected_title:
        job = filtered[filtered['title'] == selected_title].iloc[0]
        _show_job_detail(job)


def _render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """渲染筛选器并返回过滤后的DataFrame"""
    col1, col2, col3, col4 = st.columns(4)

    filtered = df.copy()

    with col1:
        available_edu = sorted([e for e in df['education'].unique() if e], key=lambda x: EDUCATION_ORDER.index(x) if x in EDUCATION_ORDER else 99)
        edu_filter = st.multiselect("学历要求", options=available_edu, key="filter_edu")
        if edu_filter:
            filtered = filtered[filtered['education'].isin(edu_filter)]

    with col2:
        available_salary = sorted([s for s in df['salary_range'].unique() if s],
                                   key=lambda x: SALARY_BIN_LABELS.index(x) if x in SALARY_BIN_LABELS else 99)
        salary_filter = st.multiselect("薪资档位", options=available_salary, key="filter_salary")
        if salary_filter:
            filtered = filtered[filtered['salary_range'].isin(salary_filter)]

    with col3:
        available_tiers = sorted([t for t in df['location_tier'].unique() if t], key=lambda x: ['一线','新一线','二线','其他','远程'].index(x) if x in ['一线','新一线','二线','其他','远程'] else 99)
        tier_filter = st.multiselect("城市等级", options=available_tiers, key="filter_tier")
        if tier_filter:
            filtered = filtered[filtered['location_tier'].isin(tier_filter)]

    with col4:
        available_sources = sorted(df['source'].unique())
        source_filter = st.multiselect("来源网站", options=available_sources, key="filter_source")
        if source_filter:
            filtered = filtered[filtered['source'].isin(source_filter)]

    # 福利待遇筛选
    st.write("**待遇筛选**")
    wcol1, wcol2, wcol3 = st.columns(3)
    with wcol1:
        grad_filter = st.checkbox("仅看招应届生", key="filter_grad")
        if grad_filter and 'is_accept_graduate' in filtered.columns:
            filtered = filtered[filtered['is_accept_graduate'] == True]
    with wcol2:
        insurance_filter = st.checkbox("仅看有五险一金", key="filter_insurance")
        if insurance_filter and 'has_insurance' in filtered.columns:
            filtered = filtered[filtered['has_insurance'] == True]
    with wcol3:
        weekend_filter = st.checkbox("仅看有双休", key="filter_weekend")
        if weekend_filter and 'has_weekend_off' in filtered.columns:
            filtered = filtered[filtered['has_weekend_off'] == True]

    # 全文搜索
    kw = st.text_input("🔍 全文搜索（职位名/描述/技术栈）", key="browse_kw")
    if kw:
        mask = (
            filtered['title'].str.contains(kw, case=False, na=False) |
            filtered.get('description', pd.Series(['']*len(filtered))).str.contains(kw, case=False, na=False) |
            filtered.get('tech_stack', pd.Series(['']*len(filtered))).str.contains(kw, case=False, na=False) |
            filtered.get('company', pd.Series(['']*len(filtered))).str.contains(kw, case=False, na=False)
        )
        filtered = filtered[mask]

    return filtered


def _show_job_detail(job):
    """显示职位详情"""
    cols = [
        ('title', '职位名称'), ('company', '公司'), ('location', '工作地点'),
        ('location_tier', '城市等级'), ('salary_text', '薪资'), ('salary_range', '薪资档位'),
        ('education', '学历要求'), ('experience', '经验要求'),
        ('tech_stack', '技术栈'), ('source', '来源网站'),
        ('post_date', '发布日期'), ('job_type', '职位类型'),
        ('is_accept_graduate', '招应届生'), ('has_insurance', '五险一金'),
        ('has_weekend_off', '双休'),
    ]

    for col_key, col_label in cols:
        if col_key in job.index and job[col_key] is not None:
            val = job[col_key]
            if col_key.startswith('is_') or col_key.startswith('has_'):
                val = '✅ 是' if val else '❌ 否'
            st.write(f"**{col_label}**: {val}")

    for col_key, col_label in cols:
        if col_key in job.index and job[col_key]:
            st.write(f"**{col_label}**: {job[col_key]}")

    if 'description' in job.index and job['description']:
        with st.expander("📝 职位描述"):
            st.text(job['description'])

    if 'url' in job.index and job['url']:
        st.markdown(f"[🔗 打开原文链接]({job['url']})")
