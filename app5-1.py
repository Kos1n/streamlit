import os

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Дашборд продажів", layout="wide")

DATA_FILE = "sales.csv"


def money(value):
    """Форматує суму: 1234567 -> '1 234 567 грн'."""
    return f"{value:,.0f} грн".replace(",", " ")


@st.cache_data
def load_data(source):
    df = pd.read_csv(source, parse_dates=["date"])
    return df


# --- Завантаження даних ---
if os.path.exists(DATA_FILE):
    data = load_data(DATA_FILE)
else:
    st.warning(f"Файл {DATA_FILE} не знайдено. Завантажте CSV із колонками: "
               "order_id, date, category, product, quantity, unit_price, revenue.")
    uploaded = st.file_uploader("CSV з даними про продажі", type="csv")
    if uploaded is None:
        st.stop()
    data = load_data(uploaded)

st.title("Дашборд аналітики продажів")

# --- Фільтри ---
with st.container(border=True):
    st.subheader("Фільтри")
    col_period, col_category = st.columns(2)

    min_date = data["date"].min().date()
    max_date = data["date"].max().date()

    with col_period:
        period = st.date_input(
            "Період",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    with col_category:
        all_categories = sorted(data["category"].unique())
        selected = st.multiselect("Категорії", all_categories, default=all_categories)

# date_input повертає кортеж; поки обрано лише одну дату, чекаємо другу
if not isinstance(period, (tuple, list)) or len(period) != 2:
    st.info("Оберіть кінцеву дату періоду.")
    st.stop()
if not selected:
    st.warning("Оберіть хоча б одну категорію.")
    st.stop()

start, end = pd.Timestamp(period[0]), pd.Timestamp(period[1])
filtered = data[
    (data["date"] >= start)
    & (data["date"] <= end)
    & (data["category"].isin(selected))
]

if filtered.empty:
    st.warning("За обраними фільтрами даних немає.")
    st.stop()

# --- Ключові метрики ---
total_revenue = filtered["revenue"].sum()
orders = filtered["order_id"].nunique()
avg_check = total_revenue / orders
items = filtered["quantity"].sum()

with st.container():
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Загальний дохід", money(total_revenue))
    m2.metric("Середній чек", money(avg_check))
    m3.metric("Кількість замовлень", f"{orders:,}".replace(",", " "))
    m4.metric("Продано одиниць", f"{items:,}".replace(",", " "))

# --- Графіки ---
with st.container():
    chart_left, chart_right = st.columns([3, 2])

    with chart_left:
        st.subheader("Продажі за днями")
        daily = (
            filtered.groupby("date", as_index=False)["revenue"].sum()
            .set_index("date")
            .reindex(pd.date_range(start, end), fill_value=0)
            .rename_axis("date")
            .reset_index()
        )
        line = (
            alt.Chart(daily)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="Дата"),
                y=alt.Y("revenue:Q", title="Дохід, грн"),
                tooltip=[
                    alt.Tooltip("date:T", title="Дата"),
                    alt.Tooltip("revenue:Q", title="Дохід, грн", format=",.0f"),
                ],
            )
        )
        st.altair_chart(line)

    with chart_right:
        st.subheader("Дохід за категоріями")
        by_category = filtered.groupby("category", as_index=False)["revenue"].sum()
        donut = (
            alt.Chart(by_category)
            .mark_arc(innerRadius=60)
            .encode(
                theta=alt.Theta("revenue:Q", title="Дохід"),
                color=alt.Color("category:N", title="Категорія"),
                tooltip=[
                    alt.Tooltip("category:N", title="Категорія"),
                    alt.Tooltip("revenue:Q", title="Дохід, грн", format=",.0f"),
                ],
            )
        )
        st.altair_chart(donut)

# --- Таблиця з даними ---
with st.expander("Показати дані"):
    st.dataframe(filtered.sort_values("date", ascending=False), hide_index=True)