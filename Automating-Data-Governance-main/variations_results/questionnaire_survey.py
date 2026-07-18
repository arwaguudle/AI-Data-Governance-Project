import streamlit as st
import pandas as pd
from pathlib import Path
import random  # to generating random variations of the survey
from datetime import datetime  # to get current time for timestamp

# loading the dataset for the survey
@st.cache_data
def load_survey_data():
    df = pd.read_csv('variations_results/evaluation_results.csv')
    return df

# initialising the session state
def init_session_state():
    df = load_survey_data()

    # Convert to list of dictionaries
    all_items = df.to_dict('records')

    # Set up session state variables if they don't exist
    if 'survey_items' not in st.session_state:
        random.shuffle(all_items)  # randomly shuffling the purpose prompts
        st.session_state.survey_items = all_items[:50]  # taking only 3 items per user (change to 50 later)
        st.session_state.current_index = 0
        st.session_state.results = []
        st.session_state.user_id = f"user_{random.randint(1000, 9999)}"

# to show completion page when survey is done
def show_completion_page():
    st.write("Thank you for completing the survey! :)")

    st.write("Download your results:")
    survey_results_df = pd.DataFrame(st.session_state.results)
    results_csv = survey_results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=results_csv,
        file_name=f"human_survey_results_{st.session_state.user_id}.csv",
        mime='csv',
    )

# the main app
def main():
    init_session_state()  # initialising the session state

    # check if survey is complete
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

    # displaying the access request
    st.write("Access Request:")
    st.write(item.get('Purpose', ''))

    #
    # setting up the survey form (single form for ALL items)
    with st.form(key="survey_form"):
        st.write("Please answer the following questions:")

        # Question 1: Seniority
        seniority = st.radio(
            "1. What seniority level does this request appear to come from?",
            options=["Intern", "Junior", "Mid-level", "Senior", "Executive", "C-Suite", "Board"],
            index=3,
            horizontal=True
        )

        # Question 2: Hastiness
        hastiness = st.radio(
            "2. How formal or hasty is this request?",
            options=["Very Hasty", "Hasty", "Neutral", "Formal", "Very Formal"],
            index=2,
            horizontal=True
        )

       # Question 3: Meaning Preservation (only show if this is a variation)
        variation_type = item.get('Variation Type', '')

        if pd.isna(variation_type):
            variation_type = ''
        else:
            variation_type = str(variation_type).lower()

        # Show the original request only for variations
        if variation_type not in ['none', '']:
            st.write("**Original Request:**")
            st.write(item.get('Purpose', ''))

        
        if variation_type not in ['none', '']:
            meaning_preserved = st.radio(
                "3. How well does this request preserve the original meaning?",
                options=["Completely Different", "Mostly Different", "Somewhat Different", "Neutral",
                        "Somewhat Similar", "Mostly Similar", "Identical"],
                index=3,
                horizontal=True
            )
        else:
            meaning_preserved = "None - This is the original request"

        # Submit button
        submitted = st.form_submit_button("Submit & Next")

        if submitted:
            # Save the annotation
            st.session_state.results.append({
                'timestamp': datetime.now().isoformat(),  # recording when response was submitted
                'user_id': st.session_state.user_id,
                'item_id': current,
                'ID': item.get('ID', ''),  # saving original ID from dataset
                'Data Provider': item.get('Data Provider', ''),
                'Project Name': item.get('Project Name', ''),
                'Consumer Team': item.get('Consumer Team', ''),
                'Consumer Name': item.get('Consumer Name', ''),
                'Consumer Description': item.get('Consumer Description', ''),
                'Variation Type': item.get('Variation Type', ''),
                'Variation Value': item.get('Variation Value', ''),
                'Purpose': item.get('Purpose', ''),
                'Human Expert: Seniority': seniority,
                'Human Expert: Hastiness': hastiness,
                'Human Expert: Meaning Preservation': meaning_preserved,
            })

            # Move to next item
            st.session_state.current_index += 1
            st.rerun()  # Refresh the page to show the next item

    # Reset button in sidebar or at bottom
    if st.button("Start Over"):
        for key in ['survey_items', 'current_index', 'results', 'user_id']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()

    #Starting up the main consent page for users to select
def consent_page():

    st.write('Welcome to this survey!')
    st.write('Before we continue this there is something that needs to be done..')
    consent = st.radio (
        options = ['By ticking this box, I have given you my consent un using my participated input for your research purpose','I do not consent to this nonsense..'],
        index = 3,
        horizontal=False
)