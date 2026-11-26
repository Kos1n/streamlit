import streamlit as st

st.set_page_config(page_title="Калькулятор")
st.title("Калькулятор")
st.write("Введіть два числа, оберіть операцію, і результат з'явиться нижче.")

# Введення двох чисел
col1, col2 = st.columns(2)
a = col1.number_input("Перше число", value=0.0, format="%g")
b = col2.number_input("Друге число", value=0.0, format="%g")

# Вибір арифметичної операції
operation = st.radio("Операція", ["+", "−", "×", "÷"], horizontal=True)

# Обчислення
if operation == "+":
    result = a + b
elif operation == "−":
    result = a - b
elif operation == "×":
    result = a * b
else:
    result = None if b == 0 else a / b

# Виведення результату
if result is None:
    st.error("Ділення на нуль неможливе.")
else:
    st.success(f"{a:g} {operation} {b:g} = {result:g}")