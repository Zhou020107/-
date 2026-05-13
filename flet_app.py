"""
就业信息采集 App — Flet 版本
可在 PC 和 Android 上运行，打包为 APK
打包入口文件，位于项目根目录以便直接 import 所有模块
"""
import os
import tempfile
from datetime import datetime

import flet as ft

from scraper.ncss import NCSSScraper
from classifier import (
    classify_education, parse_salary, classify_salary_range,
    classify_location, detect_tech_stack, detect_welfare
)
from storage.database import Database
from export.excel import export_to_excel


# ── 全局数据库 ──
db = Database()
db.init()


def main(page: ft.Page):
    page.title = "就业信息采集"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    page.window.width = 420
    page.window.height = 800

    # ── 状态 ──
    current_tab = 0
    all_jobs = []
    filtered_jobs = []

    # ── UI 组件引用 ──
    # 搜索页
    keyword_input = ft.TextField(label="关键词", hint_text="例: Python 实习", expand=True)
    location_input = ft.TextField(label="地点", hint_text="留空=全国", expand=True)
    max_pages_input = ft.Dropdown(
        label="页数",
        options=[ft.dropdown.Option(str(i)) for i in [1, 2, 3, 5]],
        value="2",
        width=80,
    )
    search_progress = ft.ProgressBar(width=300, visible=False)
    search_status = ft.Text("", size=14)
    result_count_text = ft.Text("数据库: 0 条", size=13, italic=True)

    # 结果页
    results_list = ft.ListView(expand=True, spacing=5, padding=5)
    filter_chips = ft.Row(wrap=True, spacing=5)

    # 图表页
    chart_image = ft.Image(visible=False, fit=ft.ImageFit.CONTAIN)
    chart_type_dd = ft.Dropdown(
        label="图表类型",
        options=[
            ft.dropdown.Option("education", "学历分布"),
            ft.dropdown.Option("salary", "薪资分布"),
            ft.dropdown.Option("location", "城市TOP15"),
            ft.dropdown.Option("tech", "技术栈需求"),
        ],
        value="education",
        width=200,
    )

    # 导出页
    export_status = ft.Text("", size=14)
    export_file_name = ft.Text("", size=12, italic=True)

    # 统计文字
    stats_text = ft.Text("", size=12)

    # ── 搜索逻辑 ──
    def do_search(e):
        nonlocal all_jobs
        keyword = keyword_input.value.strip()
        if not keyword:
            search_status.value = "请输入关键词"
            page.update()
            return

        search_progress.visible = True
        search_status.value = "正在搜索..."
        page.update()

        scraper = NCSSScraper({'min_delay_seconds': 1, 'max_delay_seconds': 2})
        max_pages = int(max_pages_input.value)

        jobs = []
        try:
            for item in scraper.search(keyword, location_input.value.strip(), max_pages):
                # 分类
                item['location_tier'] = classify_location(item.get('location', ''))[1]
                item['education'] = classify_education(
                    item.get('title', ''), item.get('description', ''), item.get('education', '')
                )
                sal_min, sal_max = parse_salary(item.get('salary_text', ''))
                item['salary_min'] = sal_min
                item['salary_max'] = sal_max
                item['salary_range'] = classify_salary_range(sal_min, sal_max)
                item['tech_stack'] = ','.join(detect_tech_stack(item.get('title', ''), item.get('description', '')))
                welfare = detect_welfare(item.get('description', ''), item.get('rec_tags', ''))
                item['is_accept_graduate'] = item.get('is_accept_graduate', welfare['is_accept_graduate'])
                item['has_weekend_off'] = welfare['has_weekend_off']
                item['has_insurance'] = welfare['has_insurance']
                item['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                jobs.append(item)

                search_status.value = f"已采集 {len(jobs)} 条..."
                page.update()

        except Exception as ex:
            search_status.value = f"搜索失败: {ex}"
            search_progress.visible = False
            page.update()
            return

        if jobs:
            new_count = db.upsert_jobs(jobs)
            all_jobs = jobs
            search_status.value = f"✅ 采集 {len(jobs)} 条，新增 {new_count} 条"
        else:
            search_status.value = "未找到结果"

        search_progress.visible = False
        load_stats()
        render_results(all_jobs)
        page.update()

    def load_stats():
        stats = db.get_stats()
        total = stats.get('total', 0)
        grad = sum(1 for j in all_jobs if j.get('is_accept_graduate')) if all_jobs else 0
        ins = sum(1 for j in all_jobs if j.get('has_insurance')) if all_jobs else 0
        result_count_text.value = f"本次: {len(all_jobs)} 条 | 数据库: {total} 条 | 招应届: {grad} | 五险一金: {ins}"
        page.update()

    # ── 结果渲染 ──
    def render_results(jobs):
        nonlocal filtered_jobs
        filtered_jobs = jobs
        results_list.controls.clear()

        if not jobs:
            results_list.controls.append(ft.Text("没有结果", size=14))
        else:
            for i, job in enumerate(jobs[:100]):
                title = job.get('title', '?')
                company = job.get('company', '?')
                salary = job.get('salary_text', '?')
                location = job.get('location', '?')
                edu = job.get('education', '?')
                ins = '✅' if job.get('has_insurance') else ''
                grad = '🎓' if job.get('is_accept_graduate') else ''

                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"{title}", weight=ft.FontWeight.BOLD, size=14, max_lines=2),
                            ft.Text(f"{company}  |  {salary}", size=12),
                            ft.Row([
                                ft.Chip(ft.Text(location, size=10)),
                                ft.Chip(ft.Text(edu, size=10)),
                                ft.Text(ins + grad, size=14),
                            ]),
                        ], spacing=3),
                        padding=10,
                    ),
                )
                results_list.controls.append(card)

        page.update()

    def apply_filters(e):
        jobs = list(all_jobs)
        if not jobs:
            render_results([])
            return
        render_results(jobs)

    # ── 图表生成 ──
    def generate_chart(e):
        chart_type = chart_type_dd.value
        if not all_jobs:
            chart_image.visible = False
            export_status.value = "请先搜索获取数据"
            page.update()
            return

        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=(8, 5))

        if chart_type == "education":
            from collections import Counter
            edu_counts = Counter(j.get('education', '未知') for j in all_jobs)
            order = ['博士', '硕士', '本科', '大专', '高中/中专', '不限', '未知']
            items = sorted(edu_counts.items(), key=lambda x: order.index(x[0]) if x[0] in order else 99)
            labels, values = zip(*items) if items else ([], [])
            ax.bar(labels, values, color='#4472C4')
            ax.set_title('学历要求分布')
        elif chart_type == "salary":
            from collections import Counter
            sal_order = ['<5K', '5K-10K', '10K-20K', '20K-35K', '35K+', '面议']
            sal_counts = Counter(j.get('salary_range', '面议') for j in all_jobs)
            items = sorted(sal_counts.items(), key=lambda x: sal_order.index(x[0]) if x[0] in sal_order else 99)
            labels, values = zip(*items) if items else ([], [])
            ax.bar(labels, values, color='#ED7D31')
            ax.set_title('薪资范围分布')
        elif chart_type == "location":
            from collections import Counter
            loc_counts = Counter(j.get('location', '未知') for j in all_jobs)
            top = loc_counts.most_common(15)
            names, vals = zip(*top) if top else ([], [])
            ax.barh(list(reversed(names)), list(reversed(vals)), color='#5B9BD5')
            ax.set_title('城市分布 TOP15')
        elif chart_type == "tech":
            from collections import Counter
            tech_counts = Counter()
            for j in all_jobs:
                ts = j.get('tech_stack', '')
                for t in str(ts).split(','):
                    t = t.strip()
                    if t:
                        tech_counts[t] += 1
            top = tech_counts.most_common(12)
            names, vals = zip(*top) if top else ([], [])
            ax.barh(list(reversed(names)), list(reversed(vals)), color='#70AD47')
            ax.set_title('技术栈需求分布')

        fig.tight_layout()

        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        fig.savefig(tmp.name, dpi=100, bbox_inches='tight')
        plt.close(fig)

        chart_image.src = tmp.name
        chart_image.visible = True
        chart_image.update()

    # ── 导出 Excel ──
    def do_export(e):
        if not all_jobs:
            export_status.value = "暂无数据可导出"
            page.update()
            return

        import pandas as pd
        jobs_df = pd.DataFrame(all_jobs)
        try:
            excel_bytes = export_to_excel(jobs_df)
            save_path = os.path.join(tempfile.gettempdir(), f"就业数据_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")
            with open(save_path, 'wb') as f:
                f.write(excel_bytes)
            export_status.value = f"✅ 已导出: {save_path}"
            export_file_name.value = os.path.basename(save_path)
        except Exception as ex:
            export_status.value = f"导出失败: {ex}"

        page.update()

    # ── 页面切换 ──
    search_view = ft.Column([
        ft.Text("🔍 搜索职位", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([keyword_input, max_pages_input]),
        location_input,
        ft.ElevatedButton("开始搜索", on_click=do_search, icon=ft.Icons.SEARCH),
        search_progress,
        search_status,
        result_count_text,
    ], spacing=10, expand=True)

    results_view = ft.Column([
        ft.Text("📋 搜索结果", size=20, weight=ft.FontWeight.BOLD),
        stats_text,
        ft.Row([
            ft.ElevatedButton("刷新", on_click=lambda e: render_results(all_jobs), icon=ft.Icons.REFRESH),
        ]),
        results_list,
    ], spacing=10, expand=True)

    charts_view = ft.Column([
        ft.Text("📊 数据图表", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([chart_type_dd, ft.ElevatedButton("生成图表", on_click=generate_chart)]),
        chart_image,
    ], spacing=10, expand=True)

    export_view = ft.Column([
        ft.Text("📥 导出 Excel", size=20, weight=ft.FontWeight.BOLD),
        ft.Text(f"当前数据: {len(all_jobs)} 条", size=14),
        ft.ElevatedButton("导出为 Excel (.xlsx)", on_click=do_export, icon=ft.Icons.DOWNLOAD),
        export_status,
        export_file_name,
    ], spacing=10, expand=True)

    views = [search_view, results_view, charts_view, export_view]

    body = ft.Container(
        content=views[current_tab],
        expand=True,
        padding=10,
    )

    def on_nav_change(e):
        nonlocal current_tab
        current_tab = e.control.selected_index
        body.content = views[current_tab]
        if current_tab == 0:
            load_stats()
        elif current_tab == 1:
            render_results(all_jobs)
        body.update()

    nav_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.SEARCH, label="搜索"),
            ft.NavigationBarDestination(icon=ft.Icons.LIST, label="结果"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="图表"),
            ft.NavigationBarDestination(icon=ft.Icons.DOWNLOAD, label="导出"),
        ],
    )

    page.add(body)
    page.navigation_bar = nav_bar
    page.update()


ft.app(target=main)
