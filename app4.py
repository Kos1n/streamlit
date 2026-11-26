import pandas as pd
import streamlit as st


def is_prime(n):
    if n < 2:
        return False
    return all(n % d for d in range(2, int(n ** 0.5) + 1))


st.set_page_config(page_title="Повзунки та прапорці")
st.title("Діапазон чисел")
st.write("Оберіть діапазон повзунком і ввімкніть потрібні додаткові обчислення.")

# Повзунок для вибору діапазону (повертає кортеж: початок, кінець)
start, end = st.slider("Діапазон", min_value=0, max_value=1000, value=(10, 50))
numbers = list(range(start, end + 1))

# Основні результати (є завжди)
col1, col2 = st.columns(2)
col1.metric("Кількість чисел", len(numbers))
col2.metric("Межі діапазону", f"{start} … {end}")

# Прапорці вмикають/вимикають додаткові обчислення
st.subheader("Додаткові обчислення")
show_stats = st.checkbox("Сума та середнє")
show_even = st.checkbox("Парні числа")
show_primes = st.checkbox("Прості числа")
show_chart = st.checkbox("Графік квадратів")

if show_stats:
    c1, c2 = st.columns(2)
    c1.metric("Сума", sum(numbers))
    c2.metric("Середнє", f"{sum(numbers) / len(numbers):g}")

if show_even:
    even = [n for n in numbers if n % 2 == 0]
    st.write(f"**Парних чисел:** {len(even)}")
    st.write(", ".join(map(str, even[:30])) + (" …" if len(even) > 30 else ""))

if show_primes:
    primes = [n for n in numbers if is_prime(n)]
    st.write(f"**Простих чисел:** {len(primes)}")
    st.write(", ".join(map(str, primes[:30])) + (" …" if len(primes) > 30 else "") if primes
             else "У цьому діапазоні простих чисел немає.")

if show_chart:
    squares = pd.Series([n ** 2 for n in numbers], index=numbers, name="n²")
    st.line_chart(squares)

if not any([show_stats, show_even, show_primes, show_chart]):
    st.info("Поставте прапорець, щоб побачити додаткові результати.")