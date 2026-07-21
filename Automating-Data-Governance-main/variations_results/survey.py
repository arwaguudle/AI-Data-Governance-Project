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
    #sending the csv file to me via email
    

#setting up the survey
def main_survey():
    init_session_state()  # initialising the session state

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

    # displaying the access request
    st.write("Access Request:")
    st.write(item.get('Purpose', ''))
    
    with st.form(key="survey_form"):
        st.write("Please answer the following questions:")
        
        #Question 1: Testing for seniority
        seniority = st.radio(
            "1. What seniority level does this request appear to come from?",
            options=["Intern", "Junior", "Mid-level", "Lead", "Senior", "Director", "Executive/CEO"],
            index=None,
            horizontal=True
        )
        
        #Question 2: Testing for hastiness
        hastiness = st.radio(
            "2. How formal or hasty is this request?",
            options=["Very Hasty", "Hasty", "Neutral", "Formal", "Very Formal"],
            index=None,
            horizontal=True
        )
        
        #Question 3: Testing for meaning preservation
        #Only showcasing this if the user is exposed to a variation
        variation_type = item.get('Variation Type', '')

        if pd.isna(variation_type):
            variation_type = ''
        else:
            variation_type = str(variation_type).lower()

        # Show the original request only for variations
        if variation_type not in ['none', '']:

            original_request = df[
                (df["ID"] == item["ID"]) &
                (df["Variation Type"] == "None")
            ]

        if not original_request.empty:
            st.write("**Original Request:**")
            st.write(original_request.iloc[0]["Purpose"])

        
        if variation_type not in ['none', '']:
            meaning_preserved = st.radio(
                "3. How well does this request preserve the original meaning?",
                options=["Completely Different", "Fairly Different", "Neutral", "Somewhat Similar", "Identical"],
                index=None,
                horizontal=True
            )
        else:
            meaning_preserved = "None - This is the original request"
        
        # Submit button
        submitted = st.form_submit_button("Continue")
        
        if submitted:
            #saving the results to the session state
            st.session_state.results.append({
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

init_session_state()
if st.session_state.page == 'consent':
    consent_page()
elif st.session_state.page == 'survey':
    main_survey()
else:
    show_completion_page()








