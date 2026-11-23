import io
import textwrap
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image, ImageOps
import streamlit as st


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

# --- Генерація картки-картинки ---
if st.button("Надіслати"):
    if not name.strip():
        st.warning("Будь ласка, введіть ім'я.")
    else:
        st.session_state["card"] = make_card(
            name.strip(), age, specialty, gpa, dorm, photo
        )

# Картка зберігається в session_state, тому не зникає при натисканні
# на кнопку завантаження
if "card" in st.session_state:
    st.success("Дані успішно надіслано!")
    st.image(st.session_state["card"])
    st.download_button(
        "Завантажити картку (PNG)",
        data=st.session_state["card"],
        file_name="student_card.png",
        mime="image/png",
    )


# =====================================================================
# Завдання 2.2: медіа та прогрес-бар
# =====================================================================
st.divider()
st.header("Медіа та обробка")

# --- Зображення ---
st.subheader("Зображення")
image_file = st.file_uploader(
    "Завантажте зображення", type=["png", "jpg", "jpeg", "gif", "webp"], key="image"
)
if image_file is not None:
    st.image(image_file, caption=image_file.name)

# --- Аудіо / відео ---
st.subheader("Аудіо або відео")
media_file = st.file_uploader(
    "Завантажте аудіо або відео",
    type=["mp3", "wav", "ogg", "mp4", "webm", "mov"],
    key="media",
)
if media_file is not None:
    if media_file.type.startswith("audio"):
        st.audio(media_file)
    elif media_file.type.startswith("video"):
        st.video(media_file)
    else:
        st.warning("Непідтримуваний тип файлу.")

# --- Прогрес-бар ---
st.subheader("Імітація обробки")
if st.button("Запустити обробку"):
    progress = st.progress(0, text="Починаємо обробку...")
    for percent in range(1, 101):
        time.sleep(0.03)  # імітація роботи
        progress.progress(percent, text=f"Обробка... {percent}%")
    st.success("Обробку завершено!")