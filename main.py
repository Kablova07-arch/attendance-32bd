import flet as ft
import datetime
import json
import os
import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "attendance_db.json")

STUDENTS = [
    "Алексеев Степан", "Бойко Степан", "Гордиенко Милена", "Гриненко Анастасия",
    "Дубина Константин", "Каблова Олеся", "Колузаев Павел", "Куркин Игорь",
    "Лебедев Вадим", "Лисневский Иван", "Лисовой Евгений", "Лукьянчиков Артем",
    "Павленко Степан", "Пивненко Татьяна", "Соловцов Александр", "Стаценко Ангелина",
    "Тараник Владимир", "Точенова Екатерина", "Чесноков Владимир", "Чурсин Максим",
    "Шуман Иван"
]

STATUS_OPTIONS = [
    ("П", "Присутствует"),
    ("н", "н"),
    ("спр", "спр"),
    ("заяв", "заяв"),
    ("об", "об"),
]

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main(page: ft.Page):
    page.title = "32-бд"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    page.window.width = 600
    page.window.height = 950

    today = datetime.date.today().strftime("%d.%m.%Y")
    current_month = datetime.date.today().strftime("%m")

    content_area = ft.Container(expand=True, padding=10)
    tab_buttons = {}

    def set_active_tab(active_index):
        for i, btn in tab_buttons.items():
            if i == active_index:
                btn.style = ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_600)
            else:
                btn.style = ft.ButtonStyle(color=ft.Colors.BLUE_600, bgcolor=ft.Colors.TRANSPARENT)

    # --- ГЛАВНАЯ ---
    def build_main_view():
        db = load_db()
        today_data = db.get(today, {})

        count_n = sum(1 for v in today_data.values() if v == 'н')
        count_spravka = sum(1 for v in today_data.values() if v == 'спр')
        count_zayav = sum(1 for v in today_data.values() if v == 'заяв')
        count_ob = sum(1 for v in today_data.values() if v == 'об')

        absent_total = len(today_data)
        present = len(STUDENTS) - absent_total

        def refresh(e):
            content_area.content = build_main_view()
            page.update()

        return ft.Column([
            ft.Row([
                ft.Text("32-бд", size=30, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.REFRESH, on_click=refresh),
            ]),
            ft.Text(f"Посещаемость на {today}", size=16, color=ft.Colors.GREY_700),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"✅ Присутствуют: {present}", size=18),
                    ft.Text(f"❌ Отсутствуют: {absent_total}", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=10),
                    ft.Text(f"📄 Заявления: {count_zayav}", size=16),
                    ft.Text(f"📝 Объяснительные: {count_ob}", size=16),
                    ft.Text(f"🏥 Справки: {count_spravka}", size=16),
                    ft.Text(f"⚠️ Неуважительная: {count_n}", size=16),
                ], spacing=8),
                padding=20,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=15,
            ),
        ], spacing=15)


    # --- ОТМЕТКА ---
    def build_mark_view():
        db = load_db()
        today_data = db.get(today, {})

        student_buttons = {}

        def update_button_styles(student_name):
            current = today_data.get(student_name, "Присутствует")
            for label, value in STATUS_OPTIONS:
                btn = student_buttons[student_name][value]
                if value == current:
                    btn.style = ft.ButtonStyle(
                        color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_600, padding=5,
                    )
                else:
                    btn.style = ft.ButtonStyle(
                        color=ft.Colors.BLACK, bgcolor=ft.Colors.GREY_200, padding=5,
                    )

        def make_setter(student_name, value):
            def setter(e):
                current_db = load_db()
                if today not in current_db:
                    current_db[today] = {}

                if value == "Присутствует":
                    if student_name in current_db[today]:
                        del current_db[today][student_name]
                else:
                    current_db[today][student_name] = value

                save_db(current_db)

                if value == "Присутствует":
                    today_data.pop(student_name, None)
                else:
                    today_data[student_name] = value

                update_button_styles(student_name)
                status_text.value = f"💾 {student_name}: {value}"
                page.update()
            return setter

        rows = []
        status_text = ft.Text("", size=13, color=ft.Colors.GREEN)

        for student in STUDENTS:
            student_buttons[student] = {}
            buttons_row = ft.Row(spacing=3)

            for label, value in STATUS_OPTIONS:
                btn = ft.Button(
                    content=ft.Text(label, size=11),
                    width=55,
                    height=35,
                    style=ft.ButtonStyle(padding=5),
                )
                btn.on_click = make_setter(student, value)
                student_buttons[student][value] = btn
                buttons_row.controls.append(btn)

            current_val = today_data.get(student, "Присутствует")
            for value in student_buttons[student]:
                btn = student_buttons[student][value]
                if value == current_val:
                    btn.style = ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_600, padding=5)
                else:
                    btn.style = ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor=ft.Colors.GREY_200, padding=5)

            rows.append(
                ft.Row([
                    ft.Text(student, size=13, expand=True),
                    buttons_row
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )

        async def go_to_main(e):
            status_text.value = "✅ Сохранено!"
            page.update()
            await asyncio.sleep(0.4)
            set_active_tab(0)
            content_area.content = build_main_view()
            page.update()

        back_button = ft.Button(
            content=ft.Text("🏠 На главную", size=16, color=ft.Colors.WHITE),
            on_click=go_to_main,
            width=250,
            height=50,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600),
        )

        return ft.Column([
            ft.Text(f"Отметка на {today}", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Изменения сохраняются автоматически при нажатии", size=11, color=ft.Colors.GREY_600),
            ft.Divider(),
            ft.Column(rows, scroll=ft.ScrollMode.AUTO, expand=True, spacing=4),
            ft.Divider(),
            status_text,
            ft.Row([back_button], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=8, expand=True)


    # --- ВЕДОМОСТЬ ---
    table_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    table_scroll = ft.Row([table_container], scroll=ft.ScrollMode.AUTO, expand=True)

    month_dropdown = ft.Dropdown(
        label="Месяц",
        width=200,
        value=current_month,
        options=[ft.dropdown.Option(f"{m:02d}") for m in range(1, 13)],
    )

    def load_month(e=None):
        month_text = month_dropdown.value
        if not month_text:
            return
        db = load_db()
        year = "2026"

        dates = sorted(
            [d for d in db.keys() if d.endswith(f".{month_text}.{year}")],
            key=lambda x: datetime.datetime.strptime(x, "%d.%m.%Y")
        )

        if not dates:
            table_container.controls = [
                ft.Text(f"Нет данных за месяц {month_text}.{year}", size=16),
                ft.Text(f"Всего записей в БД: {len(db)}", size=12, color=ft.Colors.GREY_600),
            ]
            page.update()
            return

        header_cells = [ft.DataColumn(ft.Text("Студент", weight=ft.FontWeight.BOLD, size=11))]
        for d in dates:
            header_cells.append(ft.DataColumn(ft.Text(d[:2], weight=ft.FontWeight.BOLD, size=11)))

        rows = []
        for student in STUDENTS:
            cells = [ft.DataCell(ft.Text(student, size=10))]
            for d in dates:
                val = db.get(d, {}).get(student, "")
                if val == "":
                    cell = ft.DataCell(ft.Container(
                        content=ft.Text("", size=11),
                        width=28, height=22, alignment=ft.Alignment.CENTER
                    ))
                else:
                    bg = ft.Colors.WHITE if val == 'н' else ft.Colors.YELLOW
                    cell = ft.DataCell(ft.Container(
                        content=ft.Text("2", size=11, color=ft.Colors.BLACK),
                        bgcolor=bg,
                        width=28, height=22,
                        alignment=ft.Alignment.CENTER,
                        border=ft.Border.all(1, ft.Colors.GREY_400)
                    ))
                cells.append(cell)
            rows.append(ft.DataRow(cells=cells))

        table = ft.DataTable(
            columns=header_cells,
            rows=rows,
            column_spacing=4,
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
        )
        table_container.controls = [table]
        page.update()

    month_dropdown.on_change = load_month

    def build_statement_view():
        load_month()
        return ft.Column([
            ft.Text("Ведомость посещаемости", size=20, weight=ft.FontWeight.BOLD),
            month_dropdown,
            ft.Divider(),
            table_scroll
        ], spacing=10, expand=True)


    # --- НАВИГАЦИЯ ---
    def switch_tab(index):
        if index == 0:
            content_area.content = build_main_view()
        elif index == 1:
            content_area.content = build_mark_view()
        elif index == 2:
            content_area.content = build_statement_view()
        set_active_tab(index)
        page.update()

    btn_main = ft.Button(content=ft.Text("🏠 Главная", size=13), on_click=lambda e: switch_tab(0), expand=True, height=45)
    btn_mark = ft.Button(content=ft.Text("✅ Отметка", size=13), on_click=lambda e: switch_tab(1), expand=True, height=45)
    btn_statement = ft.Button(content=ft.Text("📊 Ведомость", size=13), on_click=lambda e: switch_tab(2), expand=True, height=45)

    tab_buttons[0] = btn_main
    tab_buttons[1] = btn_mark
    tab_buttons[2] = btn_statement

    top_tabs = ft.Row([btn_main, btn_mark, btn_statement], spacing=5)

    set_active_tab(0)
    content_area.content = build_main_view()

    page.add(top_tabs, content_area)
    page.update()


ft.run(main)