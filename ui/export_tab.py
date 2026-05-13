import streamlit as st
import pandas as pd
from datetime import datetime
from export.excel import export_to_excel


def render():
    """导出 Excel 页面"""
    st.header("📥 导出数据到 Excel")

    db = st.session_state.db
    jobs_df = db.query_jobs()

    if jobs_df.empty:
        st.info("还没有数据，请先去 🔍 搜索爬取 页面搜索职位")
        return

    st.subheader(f"当前数据: {len(jobs_df)} 条职位")

    # 导出选项
    st.subheader("⚙️ 导出设置")

    col1, col2 = st.columns(2)
    with col1:
        export_sheets = st.multiselect(
            "导出内容",
            options=["全部职位（主表）", "按学历分类", "按薪资分类", "按城市分类", "按技术栈分类", "统计摘要"],
            default=["全部职位（主表）", "统计摘要"],
            key="export_sheets",
        )

    with col2:
        edu_filter = st.multiselect(
            "学历筛选（可选）",
            options=sorted(jobs_df['education'].dropna().unique()),
            key="export_edu_filter",
        )
        source_filter = st.multiselect(
            "来源筛选（可选）",
            options=sorted(jobs_df['source'].dropna().unique()),
            key="export_source_filter",
        )

    # 文件名
    default_name = f"职位数据_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    file_name = st.text_input("文件名", value=default_name, key="export_filename")

    # 导出按钮
    if st.button("📥 生成并下载 Excel", type="primary", use_container_width=True):
        # 应用筛选
        export_df = jobs_df.copy()
        if edu_filter:
            export_df = export_df[export_df['education'].isin(edu_filter)]
        if source_filter:
            export_df = export_df[export_df['source'].isin(source_filter)]

        if export_df.empty:
            st.warning("筛选后无数据")
            return

        with st.spinner("正在生成 Excel..."):
            excel_bytes = export_to_excel(export_df)

            st.download_button(
                label="💾 点击下载 Excel 文件",
                data=excel_bytes,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        st.success(f"✅ Excel 文件已生成！包含 {len(export_df)} 条职位数据")

    # 数据概览
    st.subheader("📊 数据概览")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总职位", len(jobs_df))
    with col2:
        st.metric("来源网站", jobs_df['source'].nunique() if 'source' in jobs_df.columns else 0)
    with col3:
        st.metric("覆盖城市", jobs_df['location'].nunique() if 'location' in jobs_df.columns else 0)
