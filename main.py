import flet as ft
import datetime
import json
import os

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

    # Убираем жесткие размеры окна, чтобы приложение подстроилось под экран телефона
    page.window.width = None
    page.window.height = None

    today = datetime.date.today().strftime("%d.%m.%Y")
    current_month = datetime.date.today().strftime("%m")

    content_area = ft.Container(expand=True, padding=5)
    tab_buttons = {}

    pair_state = [1]
    pair_btn_refs = {}

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

        absent_students = set()
        count_n, count_spravka, count_zayav, count_ob = 0, 0, 0, 0

        for pair in ["1", "2", "3"]:
            pair_data = today_data.get(pair, {})
            for student, reason in pair_data.items():
                absent_students.add(student)
                if reason == 'н':
                    count_n += 1
                elif reason == 'спр':
                    count_spravka += 1
                elif reason == 'заяв':
                    count_zayav += 1
                elif reason == 'об':
                    count_ob += 1

        absent_total = len(absent_students)
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
            ft.Text(f"Общая посещаемость на {today}", size=16, color=ft.Colors.GREY_700),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"✅ Присутствуют (полностью): {present}", size=18),
                    ft.Text(f"❌ Отсутствовали хотя бы раз: {absent_total}", size=18, weight=ft.FontWeight.BOLD),
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

        def update_button_colors():
            pair_key = str(pair_state[0])
            current_db = load_db()
            pair_data = current_db.get(today, {}).get(pair_key, {})

            for student in STUDENTS:
                current_val = pair_data.get(student, "Присутствует")
                for label, value in STATUS_OPTIONS:
                    btn = student_buttons[student][value]
                    if value == current_val:
                        btn.bgcolor = ft.Colors.BLUE_600
                        btn.color = ft.Colors.WHITE
                    else:
                        btn.bgcolor = ft.Colors.GREY_200
                        btn.color = ft.Colors.BLACK

            for num, btn in pair_btn_refs.items():
                if num == pair_state[0]:
                    btn.bgcolor = ft.Colors.BLUE_600
                    btn.color = ft.Colors.WHITE
                else:
                    btn.bgcolor = ft.Colors.GREY_200
                    btn.color = ft.Colors.BLACK

            page.update()

        def make_setter(student_name, value):
            def setter(e):
                current_db = load_db()
                if today not in current_db:
                    current_db[today] = {}
                pair_key = str(pair_state[0])
                if pair_key not in current_db[today]:
                    current_db[today][pair_key] = {}

                if value == "Присутствует":
                    if student_name in current_db[today][pair_key]:
                        del current_db[today][pair_key][student_name]
                else:
                    current_db[today][pair_key][student_name] = value

                save_db(current_db)

                update_button_colors()
                status_text.value = f"💾 {student_name}: {value} (Пара {pair_key})"
                page.update()

            return setter

        rows = []
        status_text = ft.Text("", size=12, color=ft.Colors.GREEN)

        for student in STUDENTS:
            student_buttons[student] = {}
            buttons_row = ft.Row(spacing=2)  # Уменьшили расстояние между кнопками

            pair_key = str(pair_state[0])
            current_val = today_data.get(pair_key, {}).get(student, "Присутствует")

            for label, value in STATUS_OPTIONS:
                btn = ft.Button(
                    content=ft.Text(label, size=11),
                    width=58,  # Уменьшили ширину для телефона
                    height=36,  # Уменьшили высоту
                    bgcolor=ft.Colors.BLUE_600 if value == current_val else ft.Colors.GREY_200,
                    color=ft.Colors.WHITE if value == current_val else ft.Colors.BLACK,
                )
                btn.on_click = make_setter(student, value)
                student_buttons[student][value] = btn
                buttons_row.controls.append(btn)

            rows.append(
                ft.Row([
                    ft.Text(student, size=12, expand=True),
                    buttons_row
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )

        def change_pair(pair_num):
            pair_state[0] = pair_num
            update_button_colors()

        btn_pair1 = ft.Button("1", on_click=lambda e: change_pair(1), width=40, height=35)
        btn_pair2 = ft.Button("2", on_click=lambda e: change_pair(2), width=40, height=35)
        btn_pair3 = ft.Button("3", on_click=lambda e: change_pair(3), width=40, height=35)

        pair_btn_refs[1] = btn_pair1
        pair_btn_refs[2] = btn_pair2
        pair_btn_refs[3] = btn_pair3

        pair_selector = ft.Row([
            ft.Text("Пара:", size=14, weight=ft.FontWeight.BOLD),
            btn_pair1,
            btn_pair2,
            btn_pair3,
        ], alignment=ft.MainAxisAlignment.CENTER)

        update_button_colors()

        return ft.Column([
            ft.Text(f"Отметка на {today}", size=18, weight=ft.FontWeight.BOLD),
            pair_selector,
            ft.Divider(),
            ft.Column(rows, scroll=ft.ScrollMode.AUTO, expand=True, spacing=5),
            ft.Divider(),
            status_text,
        ], spacing=5, expand=True)

    # --- ВЕДОМОСТЬ ---
    table_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    table_scroll = ft.Row([table_container], scroll=ft.ScrollMode.AUTO, expand=True)

    month_dropdown = ft.Dropdown(
        label="Месяц",
        width=150,
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
                ft.Text(f"Нет данных за месяц {month_text}.{year}", size=14),
                ft.Text(f"Всего записей в БД: {len(db)}", size=12, color=ft.Colors.GREY_600),
            ]
            page.update()
            return

        header_cells = [ft.DataColumn(ft.Text("Студент", weight=ft.FontWeight.BOLD, size=10))]
        for d in dates:
            day_str = d[:2]
            header_cells.append(ft.DataColumn(ft.Text(day_str, weight=ft.FontWeight.BOLD, size=10)))

        rows = []
        for student in STUDENTS:
            cells = [ft.DataCell(ft.Text(student, size=9))]

            for d in dates:
                day_data = db.get(d, {})
                row_cells = ft.Row(spacing=0)

                for pair_num in ["1", "2", "3"]:
                    val = day_data.get(pair_num, {}).get(student, "")

                    if val == "":
                        cell_content = ft.Container(
                            content=ft.Text("", size=10),
                            width=18, height=20,
                            alignment=ft.Alignment.CENTER,
                            border=ft.Border(right=ft.BorderSide(1, ft.Colors.GREY_300) if pair_num != "3" else None)
                        )
                    else:
                        bg = ft.Colors.WHITE if val == 'н' else ft.Colors.YELLOW
                        cell_content = ft.Container(
                            content=ft.Text("2", size=10, color=ft.Colors.BLACK),
                            bgcolor=bg,
                            width=18, height=20,
                            alignment=ft.Alignment.CENTER,
                            border=ft.Border(
                                left=ft.BorderSide(1, ft.Colors.GREY_400) if pair_num == "1" else None,
                                right=ft.BorderSide(1, ft.Colors.GREY_400) if pair_num != "3" else None,
                                top=ft.BorderSide(1, ft.Colors.GREY_400),
                                bottom=ft.BorderSide(1, ft.Colors.GREY_400),
                            )
                        )
                    row_cells.controls.append(cell_content)

                cells.append(ft.DataCell(row_cells))

            rows.append(ft.DataRow(cells=cells))

        table = ft.DataTable(
            columns=header_cells,
            rows=rows,
            column_spacing=8,
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
        )
        table_container.controls = [table]
        page.update()

    month_dropdown.on_change = load_month

    def build_statement_view():
        load_month()
        return ft.Column([
            ft.Text("Ведомость", size=18, weight=ft.FontWeight.BOLD),
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

    btn_main = ft.Button(content=ft.Text("🏠", size=16), on_click=lambda e: switch_tab(0), expand=True, height=45)
    btn_mark = ft.Button(content=ft.Text("✅", size=16), on_click=lambda e: switch_tab(1), expand=True, height=45)
    btn_statement = ft.Button(content=ft.Text("📊", size=16), on_click=lambda e: switch_tab(2), expand=True, height=45)

    tab_buttons[0] = btn_main
    tab_buttons[1] = btn_mark
    tab_buttons[2] = btn_statement

    top_tabs = ft.Row([btn_main, btn_mark, btn_statement], spacing=5)

    set_active_tab(0)
    content_area.content = build_main_view()

    page.add(top_tabs, content_area)
    page.update()


ft.run(main)
