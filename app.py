import streamlit as st

st.title("Анкета студента")

# --- Віджети форми ---
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

# --- Виведення картки після натискання кнопки ---
if st.button("Надіслати"):
    if not name.strip():
        st.warning("Будь ласка, введіть ім'я.")
    else:
        st.success("Дані успішно надіслано!")

        with st.container(border=True):
            if photo is not None:
                st.image(photo, width=220)
            else:
                st.caption("Фото не завантажено")

            st.subheader(name)
            st.write(f"**Вік:** {age}")
            st.write(f"**Спеціальність:** {specialty}")
            st.write(f"**Середній бал:** {gpa:.1f}")
            st.write(f"**Гуртожиток:** {'Так' if dorm else 'Ні'}")
