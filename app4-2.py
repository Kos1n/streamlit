import streamlit as st

# --- Ініціалізація стану (виконується лише при першому запуску сесії) ---
if "count" not in st.session_state:
    st.session_state.count = 0
if "last_value" not in st.session_state:
    st.session_state.last_value = ""


# --- Обробники подій (callback-и виконуються ДО перезапуску скрипта) ---
def increment():
    st.session_state.count += 1


def reset():
    st.session_state.count = 0


def save_value():
    st.session_state.last_value = st.session_state.input_value


st.title("session_state: лічильник і збереження значення")

# --- 1. Лічильник натискань ---
st.header("Лічильник натискань")
col1, col2 = st.columns(2)
col1.button("Натисни мене", on_click=increment)
col2.button("Скинути", on_click=reset)
st.metric("Кількість натискань (session_state)", st.session_state.count)

# Для порівняння: звичайна змінна скидається при кожному перезапуску
plain_counter = 0
plain_counter += 1
st.metric("Звичайна змінна Python", plain_counter)
st.caption("Звичайна змінна завжди дорівнює 1, бо скрипт виконується заново.")

st.divider()

# --- 2. Збереження останнього введеного значення ---
st.header("Останнє введене значення")
st.text_input("Введіть значення і натисніть Enter", key="input_value", on_change=save_value)

if st.session_state.last_value:
    st.success(f"Останнє збережене значення: {st.session_state.last_value}")
else:
    st.info("Значення ще не вводилось.")

with st.expander("Вміст st.session_state"):
    st.write(dict(st.session_state))