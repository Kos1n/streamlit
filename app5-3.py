import pandas as pd
import streamlit as st
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="Передбачення прогресування діабету", layout="centered")

# Назва, крок слайдера для кожної ознаки датасету
FEATURES = {
    "age": ("Вік, років", 1),
    "bmi": ("Індекс маси тіла (BMI)", 0.1),
    "bp": ("Середній артеріальний тиск", 1.0),
    "s1": ("S1: загальний холестерин", 1.0),
    "s2": ("S2: ЛПНЩ (LDL)", 1.0),
    "s3": ("S3: ЛПВЩ (HDL)", 1.0),
    "s4": ("S4: холестерин / HDL", 0.1),
    "s5": ("S5: log рівня тригліцеридів", 0.01),
    "s6": ("S6: рівень глюкози", 1.0),
}


@st.cache_resource
def train_model():
    """Навчає модель один раз і кешує її між перезапусками скрипта."""
    # scaled=False - ознаки в оригінальних одиницях, а не стандартизовані
    data = load_diabetes(as_frame=True, scaled=False)
    X, y = data.data, data.target

    # Клас 1 - прогресування хвороби за рік вище медіанного
    threshold = y.median()
    y_class = (y > threshold).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_class, test_size=0.2, random_state=42, stratify=y_class
    )
    model = RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    return {
        "model": model,
        "accuracy": model.score(X_test, y_test),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "threshold": threshold,
        "X": X,
        "importances": pd.Series(model.feature_importances_, index=X.columns),
    }


bundle = train_model()
model, X = bundle["model"], bundle["X"]

st.title("Передбачення прогресування діабету")
st.caption(
    "Навчальна демонстрація на датасеті sklearn `load_diabetes` (RandomForestClassifier). "
    "Це не медична порада."
)

# --- Інформація про модель ---
with st.expander("Про модель"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Точність на тесті", f"{bundle['accuracy']:.0%}")
    c2.metric("Навчальна вибірка", bundle["n_train"])
    c3.metric("Тестова вибірка", bundle["n_test"])
    st.write(
        f"Клас **«високий ризик»** означає, що показник прогресування хвороби "
        f"через рік вищий за медіанний ({bundle['threshold']:.0f})."
    )
    st.write("Важливість ознак:")
    st.bar_chart(bundle["importances"].sort_values())

# --- Введення даних пацієнта ---
st.subheader("Показники пацієнта")
values = {}
with st.container(border=True):
    left, right = st.columns(2)
    columns = [left, right]

    for i, (key, (label, step)) in enumerate(FEATURES.items()):
        col = columns[i % 2]
        lo, hi, med = float(X[key].min()), float(X[key].max()), float(X[key].median())
        if key == "age":
            values[key] = col.slider(label, int(lo), int(hi), int(med), step=1)
        else:
            values[key] = col.slider(label, lo, hi, med, step=float(step))

    # Стать у датасеті закодована числами 1 і 2
    values["sex"] = columns[len(FEATURES) % 2].selectbox(
        "Стать (код у датасеті)", [1, 2], format_func=lambda v: f"Код {v}"
    )

# --- Передбачення ---
patient = pd.DataFrame([values])[list(X.columns)]  # порядок колонок як у навчанні
proba_high = float(model.predict_proba(patient)[0][1])

st.subheader("Результат")
col_a, col_b = st.columns([1, 2])
col_a.metric("Ймовірність високого ризику", f"{proba_high:.0%}")
col_b.progress(proba_high)

if proba_high >= 0.5:
    st.error("Високий ризик прогресування хвороби. Рекомендується консультація лікаря.")
else:
    st.success("Низький ризик прогресування хвороби за цими показниками.")