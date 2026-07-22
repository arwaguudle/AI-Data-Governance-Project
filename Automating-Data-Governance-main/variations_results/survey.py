import streamlit as st
import pandas as pd
from pathlib import Path
import random #to generating random variations of the survey


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

    # Convert to list of dictionaries
    all_items = df.to_dict('records')

    # Setting up session state variables; if they dont exist
    if 'survey_items' not in st.session_state:
        random.shuffle(all_items)  # randomly shuffling the purpose prompts
        st.session_state.survey_items = all_items[:20]  #taking only 20 item per user
        st.session_state.current_index = 0
        st.session_state.results = []
        st.session_state.user_id = f"user_{random.randint(100, 999)}"
        st.session_state.page = 'consent'

#Starting up the main consent page for users to select
def consent_page():
    st.write("Welcome to this survey!")
    st.write("Before we continue...")
    consent = st.radio(
        "Do you consent to participate?",
        options=["Yes, I consent", "No, I do not consent"],
        index=None,
        horizontal = False
    )
    if st.button("Continue"):
        if consent == "Yes, I consent":
            st.session_state.page = 'survey'
            st.rerun()
        else:
            st.write("Thank you for your time. You may close this page.")
            st.stop()
    
# to show completion page when survey is done
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
#setting up the survey
def main_survey():
    init_session_state()

    # Load the full dataframe
    df = load_survey_data()

    # checking if survey is complete
    if st.session_state.current_index >= len(st.session_state.survey_items):
        show_completion_page()
        return

    # get the current item
    item = st.session_state.survey_items[st.session_state.current_index]
    current = st.session_state.current_index + 1
    total = len(st.session_state.survey_items)

    # showing progress bar
    st.write(f"Progress: {current} / {total}")
    st.progress(current / total)

    st.markdown("""
    <style>

    /* Center seniority radio buttons */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        width: 100%;
        padding-top: 0px;
        padding-bottom:0px;
    }

    /* Make each seniority option equal width */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex: 1;
        min-width: 85px;
        max-width: 200px;
        text-align: center;
        justify-content: center;
    }

    /* Center the circle and text vertically */
    div[data-testid="stRadio"] label {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;
    }

    /* Prevent long labels breaking awkwardly */
    div[data-testid="stRadio"] label p {
        text-align: center;
        font-size: 15px;
    }

    </style>
    """, unsafe_allow_html=True)

    # displaying the access request (variation or original)
    st.write("### Access Request")
    st.write(item.get("Purpose", ""))

    with st.form(key="survey_form"):

        st.write("Please answer the following questions:")

        # Question 1
        st.write("**1. What seniority level does this request appear to come from?**")
        seniority = st.radio(
            "",
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
            key = f"seniority_{st.session_state.current_index}"
        )

        #Question 2
        st.write("**2. How formal or hasty is this request?**")

        col1,col2 = st.columns([1,1])

        with col1:
            st.write("Very Hasty")

        with col2:
            st.write(
                "<div style='text-align:right'>Very Formal</div>",
                unsafe_allow_html=True
            )
    
        st.markdown('<div class="likert-scale">', unsafe_allow_html=True)
        hastiness = st.radio(
            "",
            options=[1, 2, 3, 4, 5, 6, 7],
            index=None,
            horizontal=True,
            label_visibility="collapsed",
            key=f"hastiness_{st.session_state.current_index}"
        
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # Determine variation type
        variation_type = item.get("Variation Type", "")

        if pd.isna(variation_type):
            variation_type = ""
        else:
            variation_type = str(variation_type).lower()

        # Only show original request if this is a variation
        if variation_type not in ["", "none"]:

            # Find the original request with the same ID
            original_request = df[
                (df["ID"] == item["ID"])
                &
                (
                    (df["Variation Type"] == "None")
                    | (df["Variation Type"].isna())
                )
            ]

            if not original_request.empty:
                st.write("###### Original Request:")
                st.write(original_request.iloc[0]["Purpose"])

            st.write("**3. How well does this request preserve the original meaning?**")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.write("Very Different")

            with col2:
                st.write(
                    "<div style='text-align:right'>Very Similar</div>",
                    unsafe_allow_html=True
                )
            st.markdown('<div class="likert-scale">', unsafe_allow_html=True)

            meaning_preserved = st.radio(
                "",
                options=[1, 2, 3, 4, 5, 6, 7],
                index=None,
                horizontal=True,
                label_visibility="collapsed",
                key=f"meaning_preserved_{st.session_state.current_index}"
            )


            st.markdown("</div>", unsafe_allow_html=True)

        else:
            meaning_preserved = "None - Original Request"

        # Submit button
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

            # Reset radio button values
            for key in [
                f"seniority_{st.session_state.current_index}",
                f"hastiness_{st.session_state.current_index}",
                f"meaning_preserved_{st.session_state.current_index}"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()  # Refresh the page to show the next item

init_session_state()
if st.session_state.page == 'consent':
    consent_page()
elif st.session_state.page == 'survey':
    main_survey()
else:
    show_completion_page()








