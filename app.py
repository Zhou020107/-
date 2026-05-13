import streamlit as st
import socket
from storage.database import Database
from ui import search_tab, browse_tab, charts_tab, export_tab

st.set_page_config(
    page_title="就业查询",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 免责声明（首次运行时显示）
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

if not st.session_state.disclaimer_accepted:
    st.title("⚠️ 使用声明")
    st.markdown("""
    ### 请阅读以下声明：

    1. **本工具仅供个人学习和求职目的使用**
    2. 请遵守各招聘网站的 robots.txt 和服务条款
    3. 请勿进行大规模、高频的数据采集
    4. 爬取的数据请勿用于商业目的或公开分发
    5. 过度爬取可能导致您的 IP 被网站封禁
    6. 请尊重招聘网站和企业的数据权益
    7. 本工具内置了爬取速度限制，每次请求间隔 3-8 秒
    8. 每个网站单次最多爬取 10 页

    点击下方按钮即表示您已知悉并同意以上声明。
    """)
    if st.button("✅ 我已知悉并同意", type="primary"):
        st.session_state.disclaimer_accepted = True
        st.rerun()
    st.stop()


# 初始化数据库
@st.cache_resource
def init_db():
    db = Database()
    db.init()
    return db


db = init_db()
if 'db' not in st.session_state:
    st.session_state.db = db

# 侧边栏
with st.sidebar:
    st.title("🔍 就业查询")

    # 数据概览
    st.subheader("📊 数据概览")
    stats = db.get_stats()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总职位数", stats['total'])
    with col2:
        st.metric("覆盖网站", len(stats['sources']))

    if stats['sources']:
        st.caption("来源分布:")
        for s in stats['sources']:
            st.caption(f"  {s['source']}: {s['cnt']} 条")

    st.divider()

    # 设置
    st.subheader("⚙️ 快速设置")
    if st.button("🗑️ 清空所有数据", use_container_width=True):
        db.clear_all()
        st.success("数据已清空")
        st.rerun()

    st.divider()

    # 网络地址提示
    st.subheader("📱 手机访问")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        st.info(f"在同一WiFi下，手机浏览器访问:\n\n**http://{local_ip}:8501**")
    except Exception:
        st.caption("确保手机与电脑在同一WiFi网络")

    st.caption(f"本地访问: http://localhost:8501")

# 主界面
st.title("🔍 就业查询")

# 四个选项卡
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 搜索爬取",
    "📋 浏览结果",
    "📊 数据图表",
    "📥 导出Excel",
])

with tab1:
    search_tab.render()

with tab2:
    browse_tab.render()

with tab3:
    charts_tab.render()

with tab4:
    export_tab.render()
