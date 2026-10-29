
import streamlit as st
import pandas as pd
import fitz
import re

st.set_page_config(
    page_title="Invoice Automation",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 AI Invoice Processing")
st.write(
    "Upload invoices, extract text, review the results, "
    "and export a CSV."
)

files = st.file_uploader(
    "Upload PDF invoices",
    type=["pdf"],
    accept_multiple_files=True
)

records = []

if files:
    for file in files:
        pdf = fitz.open(stream=file.getvalue(), filetype="pdf")
        text = "\n".join(page.get_text() for page in pdf)

        invoice_no = re.search(
            r"Invoice\s*(?:No|Number|#)\s*[:\-]?\s*([A-Z0-9/-]+)",
            text,
            re.IGNORECASE
        )

        date = re.search(
            r"(?:Invoice Date|Date)\s*[:\-]?\s*"
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            text,
            re.IGNORECASE
        )

        total = re.search(
            r"(?:Grand Total|Invoice Total|Amount Payable)"
            r"\s*[:\-]?\s*(?:₹|Rs\.?\s*)?([\d,]+\.?\d*)",
            text,
            re.IGNORECASE
        )

        records.append({
            "File": file.name,
            "Invoice Number": (
                invoice_no.group(1) if invoice_no else ""
            ),
            "Invoice Date": date.group(1) if date else "",
            "Total": (
                total.group(1).replace(",", "")
                if total else ""
            ),
            "Review Status": "Needs review"
        })

if records:
    df = pd.DataFrame(records)

    st.subheader("Extracted invoices")
    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic"
    )

    csv = edited.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Download CSV",
        data=csv,
        file_name="invoices.csv",
        mime="text/csv"
    )

    with st.expander("View extracted text"):
        for file in files:
            st.markdown(f"**{file.name}**")
            pdf = fitz.open(
                stream=file.getvalue(),
                filetype="pdf"
            )
            st.text("\n".join(page.get_text() for page in pdf))
