import csv
import io
import os
import sqlite3
import textwrap
from contextlib import closing
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image, ImageOps
import pandas as pd
import streamlit as st

DB_FILE = "students.db"
CSV_FILE = "students.csv"
CSV_FIELDS = ["datetime", "name", "age", "specialty", "gpa", "dorm", "photo"]


def save_student(row):
    """Дописує рядок у CSV; заголовки пишуться лише якщо файлу ще немає."""
    need_header = not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0
    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if need_header:
            writer.writeheader()
        writer.writerow(row)


def init_db():
    """Створює таблицю students, якщо її ще немає."""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:  # транзакція: commit/rollback
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    name      TEXT    NOT NULL,
                    age       INTEGER NOT NULL,
                    major     TEXT    NOT NULL,
                    gpa       REAL    NOT NULL,
                    dorm      INTEGER NOT NULL,   -- 0 або 1
                    timestamp TEXT    NOT NULL
                )
                """
            )


def insert_student(name, age, major, gpa, dorm):
    """Додає запис у БД (параметризований запит захищає від SQL-ін'єкцій)."""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        with conn:
            conn.execute(
                "INSERT INTO students (name, age, major, gpa, dorm, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (name, int(age), major, round(float(gpa), 1), int(dorm),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )


def load_students():
    """Повертає всі записи як DataFrame."""
    with closing(sqlite3.connect(DB_FILE)) as conn:
        return pd.read_sql_query(
            "SELECT id, name, age, major, gpa, dorm, timestamp "
            "FROM students ORDER BY id DESC",
            conn,
        )


def make_card(name, age, specialty, gpa, dorm, photo):
    """Малює картку студента і повертає її як PNG-байти."""
    H = 5.2  # висота картки
    fig = plt.figure(figsize=(8, H), dpi=150)
    fig.patch.set_facecolor("#EEF1F7")

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 8)
    ax.set_ylim(0, H)
    ax.axis("off")

    # Фон картки
    ax.add_patch(FancyBboxPatch(
        (0.2, 0.2), 7.6, H - 0.4,
        boxstyle="round,pad=0,rounding_size=0.2",
        fc="white", ec="#C9D1E0", lw=2,
    ))

    # Фото (ліворуч)
    if photo is not None:
        img = Image.open(photo)
        img = ImageOps.exif_transpose(img).convert("RGB")
        img = ImageOps.fit(img, (480, 680))
        photo_ax = fig.add_axes([0.5 / 8, (H - 3.4) / 2 / H, 2.4 / 8, 3.4 / H])
        photo_ax.imshow(img, aspect="auto")
        photo_ax.set_xticks([])
        photo_ax.set_yticks([])
        for spine in photo_ax.spines.values():
            spine.set_edgecolor("#C9D1E0")
            spine.set_linewidth(2)
    else:
        ax.add_patch(plt.Rectangle((0.5, (H - 3.4) / 2), 2.4, 3.4,
                                   fc="#EEF1F7", ec="#C9D1E0", lw=2))
        ax.text(1.7, H / 2, "Немає фото", ha="center", va="center",
                fontsize=12, color="#8A94A8")

    # Ім'я
    name_lines = textwrap.wrap(name, 22)[:2]
    y = H - 0.8
    for line in name_lines:
        ax.text(3.3, y, line, fontsize=20, fontweight="bold",
                color="#1F2A44", va="center")
        y -= 0.45
    y -= 0.05
    ax.plot([3.3, 7.5], [y, y], color="#C9D1E0", lw=1.5)
    y -= 0.4

    # Рядки з даними
    rows = [
        ("Вік", str(age)),
        ("Спеціальність", specialty),
        ("Середній бал", f"{gpa:.1f} / 5"),
        ("Гуртожиток", "Так" if dorm else "Ні"),
    ]
    for label, value in rows:
        lines = textwrap.wrap(value, 20)
        ax.text(3.3, y, label, fontsize=12, color="#8A94A8", va="center")
        for line in lines:
            ax.text(5.2, y, line, fontsize=13, color="#1F2A44", va="center")
            y -= 0.3
        y -= 0.12

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()


init_db()

st.title("Анкета студента")
tab_form, tab_records = st.tabs(["Анкета", "Всі записи"])

# =====================================================================
# Вкладка 1: форма
# =====================================================================
with tab_form:
    name = st.text_input("Ім'я")
    age = st.number_input("Вік", min_value=16, max_value=60, value=18, step=1)
    specialty = st.selectbox(
        "Спеціальність",
        ["Комп'ютерні науки", "Інженерія програмного забезпечення",
         "Кібербезпека", "Економіка", "Право", "Філологія"],
    )
    gpa = st.slider("Середній бал", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
    dorm = st.checkbox("Проживає в гуртожитку")
    photo = st.file_uploader("Фото", type=["png", "jpg", "jpeg"])

    if st.button("Надіслати"):
        if not name.strip():
            st.warning("Будь ласка, введіть ім'я.")
        else:
            st.session_state["card"] = make_card(
                name.strip(), age, specialty, gpa, dorm, photo
            )
            # запис у SQLite
            insert_student(name.strip(), age, specialty, gpa, dorm)
            # запис у CSV (завдання 3.1)
            save_student({
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "name": name.strip(),
                "age": age,
                "specialty": specialty,
                "gpa": round(gpa, 1),
                "dorm": "Так" if dorm else "Ні",
                "photo": photo.name if photo is not None else "",
            })
            st.session_state["saved"] = True

    # Картка зберігається в session_state, тому не зникає при натисканні
    # на кнопку завантаження
    if "card" in st.session_state:
        if st.session_state.pop("saved", False):
            st.success(f"Дані збережено в базі {DB_FILE} та файлі {CSV_FILE}")
        st.image(st.session_state["card"])
        st.download_button(
            "Завантажити картку (PNG)",
            data=st.session_state["card"],
            file_name="student_card.png",
            mime="image/png",
        )

# =====================================================================
# Вкладка 2: перегляд усіх записів із БД
# =====================================================================

with tab_records:
    df = load_students()
    if df.empty:
        st.info("У базі даних поки що немає записів.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Усього студентів", len(df))
        col2.metric("Середній бал (загальний)", f"{df['gpa'].mean():.2f}")

        search = st.text_input("Пошук за іменем", key="search")
        shown = df[df["name"].str.contains(search, case=False, na=False, regex=False)] if search else df
        shown = shown.assign(dorm=shown["dorm"].map({1: "Так", 0: "Ні"}))
        st.dataframe(shown, hide_index=True)