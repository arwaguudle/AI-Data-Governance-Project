import streamlit as st
import pandas as pd
from pathlib import Path
import random

#loading the dataset for the survey
@st.cache_data
def load_survey_data():
    script_dir = Path(__file__).parent
    csv_path = script_dir / 'evaluation_results.csv'

    if not csv_path.exists():
        st.error(f"File not found. Tried to open: {csv_path}")
        st.stop()
    
    df = pd.read_csv(csv_path)
    return df

#initialising the session state
def init_session_state():
    df = load_survey_data()
    all_items = df.to_dict('records')

    if 'survey_items' not in st.session_state:
        random.shuffle(all_items)
        st.session_state.survey_items = all_items[:20]
        st.session_state.current_index = 0
        st.session_state.results = []
        st.session_state.user_id = f"user_{random.randint(100, 999)}"
        st.session_state.page = 'consent'

def consent_page():
    st.write("Welcome to this survey!")
    st.write("Before we continue...")
    consent = st.radio(
        "Do you consent to participate?",
        options=["Yes, I consent", "No, I do not consent"],
        index=None,
        horizontal=False
    )
    if st.button("Continue"):
        if consent == "Yes, I consent":
            st.session_state.page = 'survey'
            st.rerun()
        else:
            st.write("Thank you for your time. You may close this page.")
            st.stop()

def show_completion_page():
    st.write("Thank you for completing the survey! :)")
    st.write("Download your results:")
    survey_results_df = pd.DataFrame(st.session_state.results)
    results_csv = survey_results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=results_csv,
        file_name=f"human_survey_results_for{st.session_state.user_id}.csv",
        mime='csv',
    )

def main_survey():
    init_session_state()
    df = load_survey_data()

    if st.session_state.current_index >= len(st.session_state.survey_items):
        show_completion_page()
        return

    item = st.session_state.survey_items[st.session_state.current_index]
    current = st.session_state.current_index + 1
    total = len(st.session_state.survey_items)

    st.write(f"Progress: {current} / {total}")
    st.progress(current / total)

    # CSS for card‑style radio buttons (kept as before)
    st.markdown("""
    <style>
    div[data-testid="stRadio"] > div {
        display: flex;
        justify-content: space-between;
        width: 100%;
        gap: 4px;
    }
    div[data-testid="stRadio"] label {
        flex: 1;
        text-align: center;
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 6px 0;
        margin: 2px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
        cursor: pointer;
        font-weight: 500;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #d0d8e6;
        transform: scale(1.02);
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    /* Colour each option from red to green */
    div[data-testid="stRadio"] label:nth-child(1) { background: #ffcccc; }
    div[data-testid="stRadio"] label:nth-child(2) { background: #ffddbb; }
    div[data-testid="stRadio"] label:nth-child(3) { background: #ffeeaa; }
    div[data-testid="stRadio"] label:nth-child(4) { background: #ffffcc; }
    div[data-testid="stRadio"] label:nth-child(5) { background: #ccffcc; }
    div[data-testid="stRadio"] label:nth-child(6) { background: #aaffaa; }
    div[data-testid="stRadio"] label:nth-child(7) { background: #88ff88; }
    div[data-testid="stRadio"] label:has(input:checked) {
        border: 2px solid #2c3e50;
        box-shadow: 0 0 0 2px #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

    st.write("### Access Request")
    st.write(item.get("Purpose", ""))

    with st.form(key="survey_form"):
        st.write("Please answer the following questions:")

        # Question 1 (unchanged)
        seniority = st.radio(
            "**1. What seniority level does this request appear to come from?**",
            options=[
                "Intern",
                "Junior",
                "Mid-level",
                "Lead",
                "Senior",
                "Director",
                "Executive/CEO",
            ],
            index=None,
            horizontal=True,
            key=f"seniority_{st.session_state.current_index}"
        )

        # Question 2 – Likert scale with labels on the same row
        st.write("**2. How formal or hasty is this request?**")

        # Use three columns: left label, radio, right label
        col_left, col_mid, col_right = st.columns([1, 5, 1])

        with col_left:
            st.write("Very Hasty")

        with col_mid:
            # The radio is placed here; it will stretch to fill the column
            hastiness = st.radio(
                "",
                options=[1, 2, 3, 4, 5, 6, 7],
                index=None,
                horizontal=True,
                label_visibility="collapsed",
                key=f"hastiness_{st.session_state.current_index}"
            )

        with col_right:
            st.write("Very Formal")

        # Determine variation type
        variation_type = item.get("Variation Type", "")
        if pd.isna(variation_type):
            variation_type = ""
        else:
            variation_type = str(variation_type).lower()

        # Question 3 – only shown for variations
        if variation_type not in ["", "none"]:
            original_request = df[
                (df["ID"] == item["ID"]) &
                ((df["Variation Type"] == "None") | (df["Variation Type"].isna()))
            ]
            if not original_request.empty:
                st.write("###### Original Request:")
                st.write(original_request.iloc[0]["Purpose"])

            st.write("**3. How well does this request preserve the original meaning?**")

            # Same three‑column layout for the meaning‑preservation scale
            col_left2, col_mid2, col_right2 = st.columns([1, 5, 1])

            with col_left2:
                st.write("Very Different")

            with col_mid2:
                meaning_preserved = st.radio(
                    "",
                    options=[1, 2, 3, 4, 5, 6, 7],
                    index=None,
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"meaning_preserved_{st.session_state.current_index}"
                )

            with col_right2:
                st.write("Very Similar")
        else:
            meaning_preserved = "None - Original Request"

        submitted = st.form_submit_button("Continue")

        if submitted:
            st.session_state.results.append({
                "ID": item.get("ID", ""),
                "Data Provider": item.get("Data Provider", ""),
                "Project Name": item.get("Project Name", ""),
                "Consumer Team": item.get("Consumer Team", ""),
                "Consumer Name": item.get("Consumer Name", ""),
                "Consumer Description": item.get("Consumer Description", ""),
                "Variation Type": item.get("Variation Type", ""),
                "Variation Value": item.get("Variation Value", ""),
                "Purpose": item.get("Purpose", ""),
                "Human Expert: Seniority": seniority,
                "Human Expert: Hastiness": hastiness,
                "Human Expert: Meaning Preservation": meaning_preserved,
            })

            st.session_state.current_index += 1

            # Clean up session keys for the next question
            for key in [
                f"seniority_{st.session_state.current_index}",
                f"hastiness_{st.session_state.current_index}",
                f"meaning_preserved_{st.session_state.current_index}"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Entry point
init_session_state()
if st.session_state.page == 'consent':
    consent_page()
elif st.session_state.page == 'survey':
    main_survey()
else:
    show_completion_page()