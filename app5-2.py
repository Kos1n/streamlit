import io
import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

RESPONSES_FILE = "survey_responses.json"
MAX_ATTACHMENT_CHARS = 5000

ASPECTS = [
    "Якість матеріалів",
    "Викладач",
    "Практичні завдання",
    "Темп навчання",
    "Підтримка та зворотний зв'язок",
    "Організація курсу",
]


# --------------------------------------------------------------------------
# Робота зі сховищем (JSON)
# --------------------------------------------------------------------------
def load_responses():
    """Повертає список відгуків із JSON-файлу (порожній список, якщо файлу немає)."""
    if not os.path.exists(RESPONSES_FILE) or os.path.getsize(RESPONSES_FILE) == 0:
        return []
    with open(RESPONSES_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_response(response):
    """Додає відгук у JSON-файл (запис через тимчасовий файл, щоб не пошкодити дані)."""
    responses = load_responses()
    response["id"] = len(responses) + 1
    responses.append(response)

    tmp_file = RESPONSES_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
    os.replace(tmp_file, RESPONSES_FILE)
    return response


# --------------------------------------------------------------------------
# Обробка завантаженого файлу відгуку (.txt / .pdf)
# --------------------------------------------------------------------------
def read_attachment(uploaded):
    """Витягує текст із .txt або .pdf. Повертає (текст, попередження)."""
    name = uploaded.name.lower()
    raw = uploaded.getvalue()

    if name.endswith(".txt"):
        return raw.decode("utf-8", errors="replace").strip(), None

    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError:
            return "", "Бібліотека pypdf не встановлена: текст PDF не прочитано."
        try:
            reader = PdfReader(io.BytesIO(raw))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            return text.strip(), None
        except Exception as e:
            return "", f"Не вдалося прочитати PDF: {e}"

    return "", "Непідтримуваний формат файлу."


def build_text_copy(r):
    """Текстова копія відгуку для завантаження респондентом."""
    lines = [
        "ВІДГУК ПРО КУРС",
        f"Дата: {r['timestamp']}",
        f"Ім'я: {r['name'] or 'Анонімно'}",
        f"Email: {r['email'] or '—'}",
        f"Оцінка: {r['rating']} / 5",
        f"Сподобалось: {', '.join(r['liked']) if r['liked'] else '—'}",
        f"Рекомендує друзям: {r['recommend']}",
        "",
        "Коментар:",
        r["comment"] or "—",
    ]
    if r["attachment_text"]:
        lines += ["", f"Текст із файлу {r['attachment_name']}:", r["attachment_text"]]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Інтерфейс
# --------------------------------------------------------------------------
st.set_page_config(page_title="Оцінка курсу", layout="centered")
st.title("Оцінка задоволеності курсом")

# Місце для статистики: створюємо зверху, заповнюємо після обробки форми,
# щоб лічильник одразу враховував щойно надісланий відгук
stats_box = st.container(border=True)

with st.form("survey_form"):
    st.subheader("Ваш відгук")

    name = st.text_input("Ім'я (необов'язково)")
    email = st.text_input("Email (необов'язково)")

    rating = st.radio(
        "Загальна оцінка курсу",
        options=[1, 2, 3, 4, 5],
        format_func=lambda n: "★" * n + "☆" * (5 - n),
        index=None,
        horizontal=True,
    )

    liked = st.multiselect("Що вам найбільше сподобалось?", ASPECTS)
    recommend = st.radio(
        "Чи порекомендували б ви цей курс друзям?",
        ["Так", "Можливо", "Ні"],
        horizontal=True,
    )
    comment = st.text_area("Ваш коментар", placeholder="Що можна покращити?")
    attachment = st.file_uploader(
        "Розгорнутий відгук у файлі (необов'язково)", type=["txt", "pdf"]
    )

    submitted = st.form_submit_button("Надіслати відгук")

if submitted:
    email_clean = email.strip()
    if rating is None:
        st.error("Будь ласка, поставте оцінку курсу.")
    elif email_clean and "@" not in email_clean:
        st.error("Email введено некоректно.")
    else:
        attachment_text, attachment_name = "", ""
        if attachment is not None:
            attachment_name = attachment.name
            attachment_text, warning = read_attachment(attachment)
            if warning:
                st.warning(warning)

        saved = save_response({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name.strip(),
            "email": email_clean,
            "rating": rating,
            "liked": liked,
            "recommend": recommend,
            "comment": comment.strip(),
            "attachment_name": attachment_name,
            "attachment_text": attachment_text[:MAX_ATTACHMENT_CHARS],
        })
        st.session_state["last_copy"] = build_text_copy(saved)
        st.success("Дякуємо! Ваш відгук збережено.")

if "last_copy" in st.session_state:
    st.download_button(
        "Завантажити копію мого відгуку (.txt)",
        data=st.session_state["last_copy"].encode("utf-8"),
        file_name="my_feedback.txt",
        mime="text/plain",
    )

# --- Статистика (заповнюємо контейнер, створений зверху) ---
all_responses = load_responses()
with stats_box:
    c1, c2 = st.columns(2)
    c1.metric("Кількість відгуків", len(all_responses))
    if all_responses:
        df = pd.DataFrame(all_responses)
        c2.metric("Середня оцінка", f"{df['rating'].mean():.2f} / 5")
        distribution = df["rating"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        st.caption("Розподіл оцінок")
        st.bar_chart(distribution)
    else:
        c2.metric("Середня оцінка", "—")
        st.caption("Відгуків поки що немає. Ви можете бути першим!")

# --- Перегляд і експорт усіх відгуків ---
if all_responses:
    with st.expander("Усі відгуки"):
        table = pd.DataFrame(all_responses)
        table["liked"] = table["liked"].apply(", ".join)
        table = table.drop(columns=["attachment_text"])
        st.dataframe(table, hide_index=True)
        st.download_button(
            "Експортувати відгуки в CSV",
            data=table.to_csv(index=False).encode("utf-8-sig"),
            file_name="survey_responses.csv",
            mime="text/csv",
        )