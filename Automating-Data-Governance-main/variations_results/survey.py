import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from pathlib import Path
import random #to generating random variations of the survey
import time #to actually time the individuals went undergoing the survey


#loading the dataset for the survey
@st.cache_data
def load_survey_data():
    script_dir = Path(__file__).parent
    csv_path = script_dir / 'evaluation_results3.csv'

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
        st.session_state.survey_items = all_items[:2]  #taking only 50 item per user
        st.session_state.current_index = 0
        st.session_state.results = []
        st.session_state.user_id = f"user_{random.randint(100, 999)}"
        st.session_state.page = 'consent'

#Starting up the main consent page for users to select
def consent_page():
    st.write("### Welcome to this survey!")
    st.write("---")
    st.write("##### Instructions")
    st.write("""
    - You will see **50 different access requests** (these are modified versions of real data access requests).
    - For each request, please answer **3 questions**:
        1. **Seniority:** What level of seniority does the prompt appear to be?
        2. **Hastiness/Formality:** How formal or hasty is their language?
        3. **Meaning Preservation:** Does this request preserve the original meaning?
             (Note: Some access request that might the original so this question will not apply.  )
    - The survey should take approximately **20-30 minutes** for you to complete.
    - There are **no right or wrong answers** —just answer based on your first impression.
    - **Please don't rush or guess randomly!!** Your honest responses are crucial to this research.
    - You **cannot save and return later**, so please complete it in one sitting.
    - Your responses are **completely anonymous**.
    """)
    st.write("---")

    st.write("Before we continue...")
    consent = st.radio(
        "**Do you consent to participate?**",
        options=["Yes, I consent", "No, I do not consent"],
        index=None,
        horizontal = False
    )
    if st.button("Continue"):
        if consent == "Yes, I consent":
            st.session_state.page = 'survey'
            st.session_state.start_time = time.time() 
            st.rerun()
        else:
            st.write("Thank you for your time. You may close this page.")
            st.stop()
    
# Save responses to Google Sheets
def save_to_google_sheets(results_data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Survey Participants").sheet1
        
        existing_records = sheet.get_all_records()
        
        #there's no headers so we shall add them 
        if len(existing_records) == 0:
            headers = [
                "User ID",
                "ID",
                "Data Provider",
                "Project Name",
                "Consumer Team",
                "Consumer Name",
                "Consumer Description",
                "Variation Type",
                "Variation Value",
                "Purpose (truncated)",
                "AI Experts (Final Decision)",
                "Human Expert: Seniority",
                "Human Expert: Hastiness (1: Very Hasty | 7: Very Formal)",
                "Human Expert: Meaning Preservation (1: Very Different | 7: Very Similar)",
                "Time on Question (seconds)",
                "Total Elapsed Time (seconds)",
            ]
            sheet.append_row(headers)
        
        for row in results_data:
            sheet.append_row(row)
            
    except Exception as e:
        st.error(f"Error saving data: {e}")

#showing completion page when survey is done
def show_completion_page():
    
    #calcluating total time
    if 'start_time' in st.session_state:
        total_seconds = round(time.time() - st.session_state.start_time, 2)
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        total_time_str = f"{minutes} minute(s) and {seconds} second(s)"
    else:
        total_seconds = 0
        total_time_str = "Not recorded"
    
    #saving to Google sheets
    if st.session_state.results:
        rows_to_save = []
        for result in st.session_state.results:
            row = [
                result.get('User ID', ''),
                result.get('ID', ''),
                result.get('Data Provider', ''),
                result.get('Project Name', ''),
                result.get('Consumer Team', ''),
                result.get('Consumer Name', ''),
                result.get('Consumer Description', ''),
                result.get('Variation Type', ''),
                result.get('Variation Value', ''),
                result.get('Purpose', '')[:100],
                result.get('AI Experts', ''),
                result.get('Human Expert: Seniority', ''),
                result.get('Human Expert: Hastiness (1: Very Hasty | 7: Very Formal)', ''),
                result.get('Human Expert: Meaning Preservation (1: Very Different | 7: Very Similar)', ''),
                result.get('Time on Question (seconds)', ''),
                result.get('Total Elapsed Time (seconds)', ''),
            ]
            rows_to_save.append(row)
            #adding a space

        
        with st.spinner("Saving your responses..."):
            save_to_google_sheets(rows_to_save)
    
    st.write("##### Thank you for completing the survey! :)")

    st.write("**Your responses have been recorded successfully!**")
    st.write("You may now close this page.")
    
    #and if it all goes wrong with the CSV file
    st.write("---")
    st.write("**Download a backup of your responses (optional):**")
    survey_results_df = pd.DataFrame(st.session_state.results)
    results_csv = survey_results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV (Backup)",
        data=results_csv,
        file_name=f"survey_responses_backup_{st.session_state.user_id}.csv",
        mime='csv',
    )

#setting up the survey
def main_survey():
    #init_session_state()

    #setting the question time
    if 'question_start_time' not in st.session_state:
        st.session_state.question_start_time = time.time()

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

    #making the options look more appealing, and more spacious
    st.markdown("""
    <style>

    /* Center seniority radio buttons */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        width: 100%;
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
                "Junior Analyst",
                "Mid-level Analyst",
                "Senior Manager",
                "Lead",
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

        variation_type = item.get("Variation Type", "")

        if pd.isna(variation_type):
            variation_type = ""
        else:
            variation_type = str(variation_type).lower()

        #only showing original request if this is a variation
        if variation_type not in ["", "none"]:

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

            #checking if all the required questions have been checked by the users; (otherwise we give them an error message)
            errors = []


            if seniority is None:
                errors.append("Please select a seniority button before continuing.")
            if hastiness is None:
                errors.append("Please select a hastiness button before continuing.")
            if variation_type not in ["","none"] and meaning_preserved is None:
                errors.append("Please select how well the vairation request preserves the original meaning before continuing.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                #calculating time spent on this question
                if 'question_start_time' in st.session_state:
                    question_time = time.time() - st.session_state.question_start_time
                else:
                    question_time = 0

                if 'start_time' in st.session_state:
                    total_time_so_far = round(time.time() - st.session_state.start_time, 2)
                else:
                    total_time_so_far = 0

                st.session_state.results.append({
                    "User ID": st.session_state.user_id,
                    "ID": item.get("ID", ""),
                    "Data Provider": item.get("Data Provider", ""),
                    "Project Name": item.get("Project Name", ""),
                    "Consumer Team": item.get("Consumer Team", ""),
                    "Consumer Name": item.get("Consumer Name", ""),
                    "Consumer Description": item.get("Consumer Description", ""),
                    "Variation Type": item.get("Variation Type", ""),
                    "Variation Value": item.get("Variation Value", ""),
                    "Purpose": item.get("Purpose", ""),
                    "AI Experts": item.get("Final AI Decision", ""),
                    "Human Expert: Seniority": seniority,
                    "Human Expert: Hastiness (1: Very Hasty | 7: Very Formal)": hastiness,
                    "Human Expert: Meaning Preservation (1: Very Different | 7: Very Similar)": meaning_preserved,
                    "Time on Question (seconds)": round(question_time, 2),
                    "Total Elapsed Time (seconds)": total_time_so_far,
                })

                #resetting timer for next question
                st.session_state.question_start_time = time.time()

                st.session_state.current_index += 1

                # Reset radio button values
                for key in [
                    f"seniority_{st.session_state.current_index}",
                    f"hastiness_{st.session_state.current_index}",
                    f"meaning_preserved_{st.session_state.current_index}"
                ]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()  #for the next page

init_session_state()
if st.session_state.page == 'consent':
    consent_page()
elif st.session_state.page == 'survey':
    main_survey()
else:
    show_completion_page()