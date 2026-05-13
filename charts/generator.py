import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


FONT_FAMILY = "Microsoft YaHei, SimHei, sans-serif"
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']


def education_bar(jobs_df: pd.DataFrame):
    """学历要求分布柱状图"""
    if jobs_df.empty or 'education' not in jobs_df.columns:
        return _empty_fig("暂无数据")

    counts = jobs_df['education'].value_counts().reset_index()
    counts.columns = ['学历要求', '职位数量']
    order = ['博士', '硕士', '本科', '大专', '高中/中专', '不限', '未知']
    counts['sort'] = counts['学历要求'].apply(lambda x: order.index(x) if x in order else 99)
    counts = counts.sort_values('sort')

    fig = px.bar(counts, x='学历要求', y='职位数量', title='学历要求分布',
                 color='学历要求', text_auto=True,
                 color_discrete_sequence=COLORS)
    fig.update_traces(textposition='outside')
    fig.update_layout(font_family=FONT_FAMILY, title_font_size=20,
                      showlegend=False, height=500, xaxis_title='', yaxis_title='职位数量')
    return fig


def salary_bar(jobs_df: pd.DataFrame):
    """薪资范围分布柱状图"""
    if jobs_df.empty or 'salary_range' not in jobs_df.columns:
        return _empty_fig("暂无数据")

    order = ['<5K', '5K-10K', '10K-20K', '20K-35K', '35K+', '面议']
    counts = jobs_df['salary_range'].value_counts().reset_index()
    counts.columns = ['薪资范围', '职位数量']
    counts['sort'] = counts['薪资范围'].apply(lambda x: order.index(x) if x in order else 99)
    counts = counts.sort_values('sort')

    fig = px.bar(counts, x='薪资范围', y='职位数量', title='薪资范围分布',
                 color='薪资范围', text_auto=True,
                 color_discrete_sequence=COLORS)
    fig.update_traces(textposition='outside')
    fig.update_layout(font_family=FONT_FAMILY, title_font_size=20,
                      showlegend=False, height=500, xaxis_title='', yaxis_title='职位数量')
    return fig


def location_bar(jobs_df: pd.DataFrame, top_n: int = 15):
    """城市分布 TOP N 水平柱状图"""
    if jobs_df.empty or 'location' not in jobs_df.columns:
        return _empty_fig("暂无数据")

    counts = jobs_df['location'].value_counts().head(top_n).reset_index()
    counts.columns = ['城市', '职位数量']

    fig = px.bar(counts, x='职位数量', y='城市', title=f'城市分布 TOP {top_n}',
                 orientation='h', text_auto=True,
                 color='职位数量', color_continuous_scale='Blues')
    fig.update_layout(font_family=FONT_FAMILY, title_font_size=20,
                      height=500, yaxis={'categoryorder': 'total ascending'})
    return fig


def tech_stack_bar(jobs_df: pd.DataFrame):
    """技术栈需求分布"""
    if jobs_df.empty or 'tech_stack' not in jobs_df.columns:
        return _empty_fig("暂无数据")

    tech_counts = {}
    for ts in jobs_df['tech_stack']:
        if not ts:
            continue
        for t in str(ts).split(','):
            t = t.strip()
            if t:
                tech_counts[t] = tech_counts.get(t, 0) + 1

    if not tech_counts:
        return _empty_fig("未检测到技术栈数据")

    counts = pd.DataFrame({'技术栈': list(tech_counts.keys()), '需求数量': list(tech_counts.values())})
    counts = counts.sort_values('需求数量', ascending=True)

    fig = px.bar(counts, x='需求数量', y='技术栈', title='技术栈需求分布',
                 orientation='h', text_auto=True,
                 color='需求数量', color_continuous_scale='Greens')
    fig.update_layout(font_family=FONT_FAMILY, title_font_size=20, height=500)
    return fig


def source_bar(jobs_df: pd.DataFrame):
    """来源网站分布"""
    if jobs_df.empty or 'source' not in jobs_df.columns:
        return _empty_fig("暂无数据")

    counts = jobs_df['source'].value_counts().reset_index()
    counts.columns = ['来源网站', '职位数量']

    fig = px.pie(counts, names='来源网站', values='职位数量', title='数据来源分布',
                 color_discrete_sequence=COLORS)
    fig.update_traces(textposition='inside', textinfo='value+percent+label')
    fig.update_layout(font_family=FONT_FAMILY, title_font_size=20, height=500)
    return fig


def company_bar(jobs_df: pd.DataFrame, top_n: int = 20):
    """公司招聘 TOP N"""
    if jobs_df.empty or 'company' not in jobs_df.columns:
        return _empty_fig("暂无数据")

    counts = jobs_df[jobs_df['company'] != '']['company'].value_counts().head(top_n).reset_index()
    counts.columns = ['公司', '职位数量']

    fig = px.bar(counts, x='职位数量', y='公司', title=f'招聘职位最多的公司 TOP {top_n}',
                 orientation='h', text_auto=True,
                 color='职位数量', color_continuous_scale='Oranges')
    fig.update_layout(font_family=FONT_FAMILY, title_font_size=20,
                      height=500, yaxis={'categoryorder': 'total ascending'})
    return fig


def _empty_fig(message: str):
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font=dict(size=18))
    fig.update_layout(font_family=FONT_FAMILY, height=400, xaxis_visible=False, yaxis_visible=False)
    return fig
