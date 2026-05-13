import streamlit as st
from charts.generator import (
    education_bar, salary_bar, location_bar,
    tech_stack_bar, source_bar, company_bar,
)


def render():
    """数据图表页面"""
    st.header("📊 数据图表")

    db = st.session_state.db
    jobs_df = db.query_jobs()

    if jobs_df.empty:
        st.info("还没有数据，请先去 🔍 搜索爬取 页面搜索职位")
        return

    # 子选项卡
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎓 学历分布", "💰 薪资分布", "🏙️ 城市分布",
        "💻 技术栈需求", "📡 来源分布", "🏢 公司TOP20"
    ])

    with tab1:
        fig = education_bar(jobs_df)
        st.plotly_chart(fig, use_container_width=True)
        _show_data_table(jobs_df, 'education', '学历要求')

    with tab2:
        fig = salary_bar(jobs_df)
        st.plotly_chart(fig, use_container_width=True)
        _show_data_table(jobs_df, 'salary_range', '薪资档位')

    with tab3:
        top_n = st.slider("显示城市数量", 10, 30, 15, key="location_topn")
        fig = location_bar(jobs_df, top_n)
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        fig = tech_stack_bar(jobs_df)
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        fig = source_bar(jobs_df)
        st.plotly_chart(fig, use_container_width=True)

    with tab6:
        top_n = st.slider("显示公司数量", 10, 30, 20, key="company_topn")
        fig = company_bar(jobs_df, top_n)
        st.plotly_chart(fig, use_container_width=True)

    # 导出图表数据
    with st.expander("📋 查看原始统计数据"):
        stats = db.get_stats()
        st.json(stats)


def _show_data_table(df, column: str, label: str):
    """显示分类统计表"""
    if column in df.columns:
        counts = df[column].value_counts().reset_index()
        counts.columns = [label, '数量']
        st.dataframe(counts, use_container_width=True, hide_index=True)
