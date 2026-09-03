# projrct.py
"""
Simple Streamlit Resume Detector (Mock ATS)
- Upload a PDF resume
- Choose / edit a mock list of required skills
- Scans resume text and computes an ATS match score

Save and run with:
    pip install streamlit PyPDF2
    streamlit run projrct.py
"""

import io
import re
from typing import Dict, List, Tuple

import streamlit as st
from PyPDF2 import PdfReader


# --- Mock default required skills ---
DEFAULT_SKILLS = [
    "Python",
    "SQL",
    "Machine Learning",
    "Data Analysis",
    "Communication",
    "Teamwork",
    "Docker",
    "Kubernetes",
    "AWS",
    "Git",
    "Pandas",
    "NumPy",
]


# --- Utilities ---


def extract_text_from_pdf(file_like) -> str:
    """
    Extract text from a PDF file-like object using PyPDF2.
    Returns a single string with the concatenated page texts.
    """
    try:
        reader = PdfReader(file_like)
    except Exception as e:
        st.error(f"Unable to read PDF: {e}")
        return ""

    texts = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        texts.append(page_text)
    return "\n".join(texts)


def scan_skills(text: str, skills: List[str]) -> Dict[str, int]:
    """
    Count occurrences of each skill in the provided text.
    Case-insensitive. Uses word-boundaries where possible.
    Returns dict mapping skill -> occurrence count.
    """
    counts = {}
    if not text:
        return {skill: 0 for skill in skills}

    text_to_search = text

    for skill in skills:
        escaped = re.escape(skill)
        pattern = rf"(?i)\b{escaped}s?\b"
        matches = re.findall(pattern, text_to_search)
        counts[skill] = len(matches)
    return counts


def calculate_score(skill_counts: Dict[str, int]) -> Tuple[int, int, float]:
    """
    Given skill->count mapping:
    - matched_count: number of skills with count > 0
    - total_required: total skills considered
    - score: percentage matched (0-100)
    """
    total = len(skill_counts)
    if total == 0:
        return 0, 0, 0.0
    matched = sum(1 for c in skill_counts.values() if c > 0)
    score = (matched / total) * 100.0
    return matched, total, score


def highlight_matches(text: str, matched_skills: List[str], max_chars: int = 8000) -> str:
    """
    Return an HTML-safe snippet of text with matched skill occurrences highlighted with <mark>.
    Limit output length to max_chars for performance.
    """
    if not text:
        return ""

    snippet = text[: max_chars]

    highlighted = snippet
    for skill in matched_skills:
        highlighted = re.sub(rf"(?i)({re.escape(skill)})", r"<mark>\1</mark>", highlighted)

    highlighted = highlighted.replace("\n", "<br>")
    return highlighted


# --- Streamlit UI ---


st.set_page_config(page_title="Resume Detector (Mock ATS)", layout="centered")
st.title("Resume Detector — Mock ATS Match")

st.markdown(
    "Upload a PDF resume and compare it to a mock required-skills list. "
    "This app demonstrates a simple keyword-based ATS match scoring."
)

# Sidebar: skill selection & editing
st.sidebar.header("Required Skills (Mock)")
selected_skills = st.sidebar.multiselect(
    "Pick required skills (editable)",
    options=DEFAULT_SKILLS,
    default=DEFAULT_SKILLS[:6],
)

# Allow adding a new skill
new_skill = st.sidebar.text_input("Add a new required skill", "")
if st.sidebar.button("Add skill"):
    if new_skill.strip():
        if new_skill not in DEFAULT_SKILLS and new_skill not in selected_skills:
            selected_skills = selected_skills + [new_skill.strip()]
            st.sidebar.success(f"Added skill: {new_skill.strip()}")
        else:
            st.sidebar.info("That skill is already present.")
    else:
        st.sidebar.error("Enter a non-empty skill to add.")

# Option to use full default list quickly
if st.sidebar.button("Use full default list"):
    selected_skills = DEFAULT_SKILLS.copy()

st.sidebar.write("Selected skills count:", len(selected_skills))

# File uploader
uploaded_file = st.file_uploader("Upload PDF resume", type=["pdf"], accept_multiple_files=False)

if uploaded_file is None:
    st.info("Please upload a PDF resume to analyze. You can also select required skills in the sidebar.")
else:
    # Extract text
    with st.spinner("Extracting text from PDF..."):
        try:
            pdf_bytes = uploaded_file.read()
            text = extract_text_from_pdf(io.BytesIO(pdf_bytes))
        except Exception as e:
            st.error(f"Failed to read uploaded PDF: {e}")
            text = ""

    if not text.strip():
        st.warning("No text detected in the PDF or extraction failed. Try another file.")
    else:
        # Scan skills
        skill_counts = scan_skills(text, selected_skills)
        matched, total, score = calculate_score(skill_counts)

        # Header with score
        st.subheader("ATS Match Results")
        st.metric(label="Match score", value=f"{score:.0f}%", delta=f"{matched}/{total} skills matched")

        # Progress bar
        st.progress(min(max(int(round(score)), 0), 100))

        # Matched skills and counts
        matched_skills = [s for s, c in skill_counts.items() if c > 0]
        missing_skills = [s for s, c in skill_counts.items() if c == 0]

        st.write("### Matched skills")
        if matched_skills:
            rows = []
            for s in matched_skills:
                rows.append(f"- **{s}** — {skill_counts[s]} occurrence(s)")
            st.markdown("\n".join(rows))
        else:
            st.write("No required skills were detected in the resume text.")

        st.write("### Missing skills")
        if missing_skills:
            st.write(", ".join(missing_skills))
        else:
            st.write("None — resume contains all required skills!")

        # Show a highlighted excerpt of resume text where matches appear
        st.write("---")
        st.write("### Resume excerpt (matched terms highlighted)")
        highlighted_html = highlight_matches(text, matched_skills, max_chars=10000)
        if highlighted_html:
            st.markdown(highlighted_html, unsafe_allow_html=True)
        else:
            st.write("No text to display.")

        # Offer full plain-text download
        st.download_button(
            label="Download extracted resume text",
            data=text,
            file_name=f"{uploaded_file.name.rsplit('.',1)[0]}_extracted.txt",
            mime="text/plain",
        )

st.write("---")
st.write(
    "Note: This is a simple keyword-based mock ATS detector intended for demonstration. "
    "Real ATS systems use weighted fields, context, synonyms, and more advanced NLP."
)
