import pandas as pd
import streamlit as st

st.title("Редактор CSV")

# --- Ініціалізація стану ---
# original_df - те, що завантажено з файлу (вхід для редактора, не змінюється)
# df          - поточний стан у пам'яті (результат редагування)
# version     - номер редактора; його зміна повністю скидає стан віджета
st.session_state.setdefault("version", 0)


def reset_changes():
    """Стан -> редактор: повертаємо початкові дані."""
    st.session_state.df = st.session_state.original_df.copy()
    st.session_state.version += 1


uploaded = st.file_uploader("Завантажте CSV-файл", type="csv")

if uploaded is not None:
    # Читаємо файл лише тоді, коли це новий файл, а не при кожному перезапуску
    file_id = (uploaded.name, uploaded.size)
    if st.session_state.get("file_id") != file_id:
        try:
            # sep=None - автоматично визначає роздільник (кома, крапка з комою тощо)
            data = pd.read_csv(uploaded, sep=None, engine="python", encoding="utf-8-sig")
        except Exception as e:
            st.error(f"Не вдалося прочитати файл: {e}")
            st.stop()
        st.session_state.file_id = file_id
        st.session_state.original_df = data
        st.session_state.df = data.copy()
        st.session_state.version += 1

    editor_key = f"editor_{st.session_state.version}"

    st.subheader("Редагування даних")
    st.caption("Змінюйте клітинки, додавайте рядки внизу таблиці, видаляйте виділені рядки.")

    # Редактор отримує НЕЗМІННІ початкові дані; його результат (з усіма
    # правками) зберігаємо в session_state.df
    edited = st.data_editor(
        st.session_state.original_df,
        num_rows="dynamic",
        key=editor_key,
    )
    st.session_state.df = edited  # редактор -> стан у пам'яті

    # --- Стан у пам'яті ---
    st.subheader("Стан у пам'яті")
    changes = st.session_state[editor_key]  # зміни, які зафіксував віджет
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Рядків", len(st.session_state.df))
    c2.metric("Змінено рядків", len(changes["edited_rows"]))
    c3.metric("Додано", len(changes["added_rows"]))
    c4.metric("Видалено", len(changes["deleted_rows"]))

    numeric = st.session_state.df.select_dtypes("number")
    if not numeric.empty:
        st.write("Статистика числових стовпців (оновлюється після кожної правки):")
        st.dataframe(numeric.describe().T)

    col_a, col_b = st.columns(2)
    col_a.button("Скасувати зміни", on_click=reset_changes)
    col_b.download_button(
        "Завантажити відредагований CSV",
        data=st.session_state.df.to_csv(index=False).encode("utf-8-sig"),
        file_name="edited.csv",
        mime="text/csv",
    )
else:
    st.info("Завантажте CSV-файл, щоб відкрити редактор.")