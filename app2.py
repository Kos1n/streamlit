import streamlit as st

st.set_page_config(page_title="Привітання")

# Заголовок та опис сторінки
st.title("Ласкаво просимо!")
st.write(
    "Це простий веб-інтерфейс на Streamlit. "
    "Введіть своє ім'я, і додаток привітає вас персонально."
)

# Текстове поле для імені
name = st.text_input("Ваше ім'я", placeholder="Наприклад, Олена")

# Персоналізоване привітання
if name.strip():
    st.success(f"Привіт, {name.strip()}! Раді вас бачити.")
else:
    st.info("Введіть ім'я, щоб отримати привітання.")