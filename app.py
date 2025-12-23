import streamlit as st
import pandas as pd
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Bṛhat Trayī with AI by PraKul",
    layout="wide"
)

DATA_FILE = "all3_cleaned.xlsx"

# ---------------- LOAD DATA ----------------
@st.cache_data(show_spinner="Loading Saṁhitā corpus…")
def load_data():
    df = pd.read_excel(DATA_FILE)
    df["Sloka_Number_Int"] = pd.to_numeric(df["Sloka_Number_Int"], errors="coerce")
    return df

df = load_data()

# ---------------- UTILITIES ----------------
def detect_script(text):
    if re.search(r"[ऀ-ॿ]", text):
        return "DEVANAGARI"
    if re.search(r"[āīūṛṝḷṅñṭḍṇśṣḥ]", text):
        return "IAST"
    if re.search(r"[A-Z]", text):
        return "ASCII"
    return "ROMAN"

def highlight_devanagari(sloka_text, pattern):
    return re.sub(
        pattern,
        lambda m: f"<span style='background-color:#b6e7b6'>{m.group(0)}</span>",
        sloka_text
    )

# ---------------- HEADER ----------------
st.title("📜 Bṛhat Trayī with AI by PraKul")
st.caption("AI-assisted data mining of the three major classical texts of Ayurveda")

# ---------------- SIDEBAR ----------------
st.sidebar.title("📂 Explore")

mode = st.sidebar.radio(
    "Choose Mode",
    ["Search Samhita", "Read Samhita"]
)

# ================= READ MODE =================
if mode == "Read Samhita":

    samhita = st.sidebar.selectbox("Samhita", sorted(df["File Name"].unique()))
    sthana = st.sidebar.selectbox(
        "Sthana",
        sorted(df[df["File Name"] == samhita]["Sthana"].unique())
    )

    chapters = df[
        (df["File Name"] == samhita) &
        (df["Sthana"] == sthana)
    ]["Chapter"].dropna().unique()

    chapter = st.sidebar.selectbox("Adhyaya (Chapter)", sorted(chapters, key=str))

    start_sloka = st.sidebar.number_input("Start Sloka Number", min_value=1, value=1)
    per_page = st.sidebar.selectbox("Slokas per page", [10, 20, 25, 50], index=2)

    if "read_pointer" not in st.session_state:
        st.session_state.read_pointer = start_sloka

    if st.button("📖 Read Slokas"):
        st.session_state.read_pointer = start_sloka

    subset = df[
        (df["File Name"] == samhita) &
        (df["Sthana"] == sthana) &
        (df["Chapter"] == chapter) &
        (df["Sloka_Number_Int"] >= st.session_state.read_pointer)
    ].sort_values("Sloka_Number_Int").head(per_page)

    # Header ONCE
    st.markdown(
        f"""
<div style="background:#eef2f7;padding:12px;border-radius:6px;margin-bottom:20px">
<strong>{samhita} | {sthana}</strong><br>
<strong>{chapter}</strong>
</div>
""",
        unsafe_allow_html=True
    )

    for _, row in subset.iterrows():
        st.markdown(
            f"""
<div style="font-size:22px; padding:10px 0 22px 10px;">
{row['Sloka Text']}
</div>
""",
            unsafe_allow_html=True
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡ Continue Reading"):
            st.session_state.read_pointer += per_page
            st.rerun()
    with col2:
        if st.button("🔄 Reset Reading"):
            st.session_state.read_pointer = start_sloka
            st.rerun()

# ================= SEARCH MODE =================
else:
    st.sidebar.info("Global search across entire Saṁhitā corpus")

    samhita_filter = st.sidebar.multiselect(
        "Select Samhita(s)",
        sorted(df["File Name"].unique()),
        default=sorted(df["File Name"].unique())
    )

    search_text = st.text_input(
        "Enter word (any script)",
        placeholder="प्रसन्न / prasanna / prasannā / prasannaM"
    )

    if st.button("🔍 Search") and search_text.strip():

        pattern = re.escape(search_text)
        corpus = df[df["File Name"].isin(samhita_filter)]

        results = []
        total_hits = 0

        for _, row in corpus.iterrows():
            hits = 0
            for col in ["Sloka Text", "IAST", "Roman", "ASCII"]:
                if pd.notna(row[col]):
                    matches = re.findall(pattern, row[col], flags=re.IGNORECASE)
                    hits += len(matches)

            if hits > 0:
                total_hits += hits
                results.append(row)

        if not results:
            st.warning("No matches found.")
        else:
            st.success(f"Total occurrences: **{total_hits}** in **{len(results)} slokas**")

            for row in results:
                highlighted = highlight_devanagari(row["Sloka Text"], pattern)
                st.markdown(
                    f"""
<div style="background:#f3f6fa;padding:10px;border-radius:6px;margin-bottom:6px">
<strong>{row['File Name']} | {row['Sthana']} | {row['Chapter']}</strong>
</div>
<div style="font-size:22px;padding:10px 0 22px 10px">
{highlighted}
</div>
""",
                    unsafe_allow_html=True
                )

# ---------------- SIDEBAR FOOTER ----------------
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
**An initiative by**  
**Prof. (Dr.) Prasanna Kulkarni**  
Ayurveda Physician | Educator | Clinician–Data Scientist  

🔗 [More AI tools](https://atharvaayurtech.com/AI)  
🔗 [LinkedIn](https://www.linkedin.com/in/drprasannakulkarni)
""",
    unsafe_allow_html=True
)
