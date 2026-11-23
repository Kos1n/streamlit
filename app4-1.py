import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

FUNCTIONS = {
    "sin": np.sin,
    "cos": np.cos,
    "exp": np.exp,
}


def make_figure(func_name, amplitude, frequency):
    """Будує графік y = A * f(ω * x) на відрізку [0, 2π]."""
    x = np.linspace(0, 2 * np.pi, 500)
    y = amplitude * FUNCTIONS[func_name](frequency * x)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y, linewidth=2)
    ax.set_title(f"y = {amplitude} · {func_name}({frequency} · x)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="black", linewidth=0.8)
    return fig


st.title("Побудова графіка функції")

# --- Віджети ---
func_name = st.selectbox("Функція", list(FUNCTIONS))
amplitude = st.slider("Амплітуда", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
frequency = st.slider("Частота", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# --- Обробка події: кнопка зберігає обрані параметри в session_state ---
if st.button("Побудувати графік"):
    st.session_state["plot_params"] = (func_name, amplitude, frequency)

# --- Графік показується лише після першого натискання кнопки ---
if "plot_params" in st.session_state:
    params = st.session_state["plot_params"]

    # Якщо після побудови змінили віджети, графік залишається старим,
    # доки користувач знову не натисне кнопку
    if params != (func_name, amplitude, frequency):
        st.warning("Параметри змінено. Натисніть «Побудувати графік», щоб оновити.")

    fig = make_figure(*params)
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("Оберіть функцію та параметри, потім натисніть «Побудувати графік».")