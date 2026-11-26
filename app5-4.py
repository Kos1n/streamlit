import io
from datetime import date

import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

# Типи документів: заголовок, вступна фраза, ім'я файлу
DOC_TYPES = {
    "Заява": {
        "title": "ЗАЯВА",
        "intro": "Прошу розглянути моє звернення. Причина звернення:",
        "file": "zayava",
    },
    "Пояснювальна записка": {
        "title": "ПОЯСНЮВАЛЬНА ЗАПИСКА",
        "intro": "Надаю пояснення щодо ситуації, що склалася. Причина:",
        "file": "poyasnyuvalna_zapyska",
    },
    "Службова записка": {
        "title": "СЛУЖБОВА ЗАПИСКА",
        "intro": "Доводжу до Вашого відома наступне:",
        "file": "sluzhbova_zapyska",
    },
}

FONT_NAME = "Times New Roman"


def set_font(run, size=14, bold=False):
    """Задає шрифт, який коректно працює з кирилицею."""
    run.font.name = FONT_NAME
    run.font.size = Pt(size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT_NAME)


def add_paragraph(doc, text="", *, align=None, size=14, bold=False,
                  left_indent=None, first_line=None, before=0, after=0, line_spacing=1.0):
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    if align is not None:
        p.alignment = align
    if left_indent is not None:
        fmt.left_indent = Cm(left_indent)
    if first_line is not None:
        fmt.first_line_indent = Cm(first_line)
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing = line_spacing
    if text:
        set_font(p.add_run(text), size=size, bold=bold)
    return p


def build_docx(doc_type, addressee, name, position, doc_date, reason):
    """Створює .docx у пам'яті та повертає його як байти."""
    spec = DOC_TYPES[doc_type]
    doc = Document()

    # Поля сторінки (A4, стандарт для українського діловодства)
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.left_margin, section.right_margin = Cm(3), Cm(1.5)
    section.top_margin = section.bottom_margin = Cm(2)

    # Базовий стиль
    normal = doc.styles["Normal"]
    normal.font.name = FONT_NAME
    normal.font.size = Pt(14)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT_NAME)

    # Шапка (права половина сторінки)
    add_paragraph(doc, f"Кому: {addressee}", left_indent=8.5)
    add_paragraph(doc, f"від: {position}", left_indent=8.5)
    add_paragraph(doc, name, left_indent=8.5)

    # Заголовок
    add_paragraph(doc, spec["title"], align=WD_ALIGN_PARAGRAPH.CENTER,
                  size=16, bold=True, before=36, after=18)

    # Основний текст
    add_paragraph(doc, spec["intro"], align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                  first_line=1.25, line_spacing=1.5)
    for line in reason.strip().splitlines():
        if line.strip():
            add_paragraph(doc, line.strip(), align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                          first_line=1.25, line_spacing=1.5)

    # Дата та підпис в одному рядку (праве вирівнювання через табуляцію)
    p = add_paragraph(doc, before=36)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16.5), WD_TAB_ALIGNMENT.RIGHT)
    set_font(p.add_run(f"{doc_date:%d.%m.%Y}\t_______________ / {name}"))
    add_paragraph(doc, "(підпис)", align=WD_ALIGN_PARAGRAPH.RIGHT, size=10)

    # Метадані
    doc.core_properties.title = doc_type
    doc.core_properties.author = name

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# --------------------------------------------------------------------------
# Інтерфейс
# --------------------------------------------------------------------------
st.set_page_config(page_title="Генератор документів", layout="centered")
st.title("Генератор шаблонів документів")
st.caption("Заповніть поля, натисніть «Згенерувати» і завантажте готовий .docx.")

doc_type = st.selectbox("Тип документа", list(DOC_TYPES))
addressee = st.text_input("Кому (адресат)", value="Директору підприємства")

col1, col2 = st.columns(2)
name = col1.text_input("Ім'я (ПІБ)", placeholder="Іваненко Іван Іванович")
position = col2.text_input("Посада", placeholder="Менеджер з продажу")
doc_date = st.date_input("Дата", value=date.today(), format="DD.MM.YYYY")
reason = st.text_area("Причина", placeholder="Опишіть причину звернення…", height=120)

if st.button("Згенерувати", type="primary"):
    missing = [label for label, value in
               [("ім'я", name), ("посаду", position), ("причину", reason)]
               if not value.strip()]
    if missing:
        st.warning("Будь ласка, заповніть: " + ", ".join(missing) + ".")
    else:
        st.session_state["docx"] = {
            "data": build_docx(doc_type, addressee.strip(), name.strip(),
                               position.strip(), doc_date, reason),
            "file_name": f"{DOC_TYPES[doc_type]['file']}_{doc_date:%Y%m%d}.docx",
            "preview": (doc_type, addressee.strip(), name.strip(),
                        position.strip(), doc_date, reason.strip()),
        }

# Результат зберігається в session_state, тому кнопка завантаження
# не зникає після власного перезапуску скрипта
if "docx" in st.session_state:
    result = st.session_state["docx"]
    st.success("Документ згенеровано!")

    st.download_button(
        "Завантажити .docx",
        data=result["data"],
        file_name=result["file_name"],
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    p_type, p_to, p_name, p_pos, p_date, p_reason = result["preview"]
    with st.expander("Попередній перегляд", expanded=True):
        with st.container(border=True):
            st.text(f"Кому: {p_to}\nвід: {p_pos}\n{p_name}")
            st.subheader(DOC_TYPES[p_type]["title"])
            st.text(f"{DOC_TYPES[p_type]['intro']}\n{p_reason}")
            st.text(f"{p_date:%d.%m.%Y}      ______________ / {p_name}")