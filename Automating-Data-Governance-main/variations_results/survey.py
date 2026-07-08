import streamlit as st
import pandas as pd
import datetime
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="Access Request Evaluation Survey",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'survey_complete' not in st.session_state:
    st.session_state.survey_complete = False
if 'annotator_id' not in st.session_state:
    st.session_state.annotator_id = None

# ============== DATA LOADING ==============

@st.cache_data
def load_access_requests():
    """Load the access requests from CSV"""
    try:
        # Try to load the combined variations file
        df = pd.read_csv('combined_variations.csv')
        return df
    except FileNotFoundError:
        # If not found, create sample data
        st.warning("⚠️ 'combined_variations.csv' not found. Using sample data.")
        return create_sample_data()

def create_sample_data():
    """Create sample access requests for testing"""
    sample_data = []
    
    seniority_levels = ["Intern", "Junior Analyst", "Senior Manager", "Executive/CEO"]
    hastiness_levels = ["Neutral", "Very Formal", "Very Hasty"]
    
    # Sample purposes for different combinations
    purposes = {
        ("Intern", "Neutral"): "I need access to the customer database for my internship project.",
        ("Intern", "Very Formal"): "Requesting temporary access to the customer database to complete the assigned project.",
        ("Intern", "Very Hasty"): "hey, need access to customer db for my project asap",
        ("Junior Analyst", "Neutral"): "Requesting access to the sales data for my quarterly analysis.",
        ("Junior Analyst", "Very Formal"): "Formal request for access to the sales data to conduct the quarterly performance analysis.",
        ("Junior Analyst", "Very Hasty"): "need sales data access for quarterly analysis, pls approve",
        ("Senior Manager", "Neutral"): "Need access to the employee records for team performance review.",
        ("Senior Manager", "Very Formal"): "Requesting access to employee records to conduct the annual team performance review.",
        ("Senior Manager", "Very Hasty"): "gotta review team performance, need employee records access",
        ("Executive/CEO", "Neutral"): "I need access to the financial reports for board meeting preparation.",
        ("Executive/CEO", "Very Formal"): "Requesting comprehensive access to financial reports for the upcoming board meeting.",
        ("Executive/CEO", "Very Hasty"): "board meeting tomorrow, need financial reports access now"
    }
    
    for seniority in seniority_levels:
        for hastiness in hastiness_levels:
            sample_data.append({
                'Variation Value': f"{seniority} + {hastiness}",
                'Seniority': seniority,
                'Hastiness': hastiness,
                'Purpose': purposes.get((seniority, hastiness), f"Sample access request from {seniority} with {hastiness} style.")
            })
    
    return pd.DataFrame(sample_data)

def load_purpose_variations():
    """Load purpose variations from existing data"""
    try:
        # Try to load the original data if it has Purpose column
        df = pd.read_csv('combined_variations.csv')
        if 'Purpose' in df.columns:
            return df[['Variation Value', 'Purpose', 'Seniority', 'Hastiness']]
    except:
        pass
    
    # If not available, use sample data
    return create_sample_data()

# ============== SURVEY QUESTIONS ==============

# Evaluation dimensions based on supervisor's feedback
EVALUATION_DIMENSIONS = [
    {
        "id": "perceived_seniority",
        "question": "What level of seniority does this request appear to come from?",
        "description": "Rate based on the language, tone, and content of the request.",
        "options": ["Intern/Junior", "Junior Analyst", "Senior Manager", "Executive/CEO"],
        "type": "seniority"  # Special handling for seniority
    },
    {
        "id": "perceived_hastiness",
        "question": "How hasty or thorough does this request appear?",
        "description": "Consider the completeness, professionalism, and urgency of the language.",
        "options": ["Very Thorough", "Thorough", "Neutral", "Hasty", "Very Hasty"],
        "type": "likert"
    },
    {
        "id": "clarity",
        "question": "How clear is the purpose of this access request?",
        "description": "Can you easily understand what access is being requested and why?",
        "options": ["Very Unclear", "Unclear", "Neutral", "Clear", "Very Clear"],
        "type": "likert"
    },
    {
        "id": "professionalism",
        "question": "How professional does this request appear?",
        "description": "Consider the language, structure, and overall presentation.",
        "options": ["Very Unprofessional", "Unprofessional", "Neutral", "Professional", "Very Professional"],
        "type": "likert"
    },
    {
        "id": "trustworthiness",
        "question": "How trustworthy does this request seem?",
        "description": "Would you approve this request based on its presentation?",
        "options": ["Not Trustworthy", "Somewhat Trustworthy", "Neutral", "Trustworthy", "Very Trustworthy"],
        "type": "likert"
    },
    {
        "id": "urgency",
        "question": "What level of urgency does this request convey?",
        "description": "How time-sensitive does the request appear to be?",
        "options": ["Not Urgent", "Slightly Urgent", "Neutral", "Urgent", "Very Urgent"],
        "type": "likert"
    },
    {
        "id": "completeness",
        "question": "How complete is the information provided in this request?",
        "description": "Does the request include all necessary details for approval?",
        "options": ["Very Incomplete", "Incomplete", "Neutral", "Complete", "Very Complete"],
        "type": "likert"
    }
]

# ============== HELPER FUNCTIONS ==============

def map_rating_to_numeric(rating, dimension_type):
    """Convert Likert ratings to numeric values"""
    if dimension_type == "seniority":
        mapping = {"Intern/Junior": 1, "Junior Analyst": 2, "Senior Manager": 3, "Executive/CEO": 4}
    else:
        # Likert scale (5-point)
        mapping = {
            "Very Unclear": 1, "Unclear": 2, "Neutral": 3, "Clear": 4, "Very Clear": 5,
            "Very Unprofessional": 1, "Unprofessional": 2, "Neutral": 3, "Professional": 4, "Very Professional": 5,
            "Not Trustworthy": 1, "Somewhat Trustworthy": 2, "Neutral": 3, "Trustworthy": 4, "Very Trustworthy": 5,
            "Not Urgent": 1, "Slightly Urgent": 2, "Neutral": 3, "Urgent": 4, "Very Urgent": 5,
            "Very Incomplete": 1, "Incomplete": 2, "Neutral": 3, "Complete": 4, "Very Complete": 5,
            "Very Thorough": 1, "Thorough": 2, "Neutral": 3, "Hasty": 4, "Very Hasty": 5
        }
    return mapping.get(rating, None)

def get_actual_values(row):
    """Extract actual seniority and hastiness from variation value"""
    # Handle different formats
    value = row.get('Variation Value', '')
    if ' + ' in value:
        parts = value.split(' + ')
        seniority = parts[0].strip()
        hastiness = parts[1].strip().split('(')[0].strip() if len(parts) > 1 else 'Unknown'
        return seniority, hastiness
    return 'Unknown', 'Unknown'

# ============== MAIN APP ==============

st.title("📝 Access Request Evaluation Survey")

# Annotator registration
if st.session_state.annotator_id is None:
    st.markdown("### 👤 Annotator Registration")
    st.markdown("Please register to begin the evaluation.")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name", placeholder="Enter your name")
    with col2:
        role = st.selectbox("Your Role", ["Student", "Researcher", "Academic Staff", "Other"])
    
    if st.button("Start Evaluation"):
        if name.strip():
            st.session_state.annotator_id = f"{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.annotator_name = name
            st.session_state.annotator_role = role
            st.rerun()
        else:
            st.error("Please enter your name.")
    st.stop()

# Load data
df = load_access_requests()

# Filter rows with Purpose column if available
if 'Purpose' in df.columns:
    df = df[df['Purpose'].notna()]
else:
    # If no Purpose column, use Variation Value
    df['Purpose'] = df['Variation Value']

# Get unique variations
if 'Seniority' in df.columns and 'Hastiness' in df.columns:
    variations = df[['Seniority', 'Hastiness', 'Purpose', 'Variation Value']].drop_duplicates()
else:
    # Extract from Variation Value
    variations_data = []
    for _, row in df.iterrows():
        seniority, hastiness = get_actual_values(row)
        variations_data.append({
            'Seniority': seniority,
            'Hastiness': hastiness,
            'Purpose': row.get('Purpose', row.get('Variation Value', '')),
            'Variation Value': row.get('Variation Value', '')
        })
    variations = pd.DataFrame(variations_data).drop_duplicates(subset=['Seniority', 'Hastiness'])

# Shuffle variations for each annotator
np.random.seed(hash(st.session_state.annotator_id) % 2**32)
variations = variations.sample(frac=1).reset_index(drop=True)

total_requests = len(variations)
current_idx = st.session_state.current_idx

# Check if survey is complete
if current_idx >= total_requests:
    st.session_state.survey_complete = True

if st.session_state.survey_complete:
    st.success("✅ Survey Complete! Thank you for your participation.")
    
    # Show summary
    st.subheader("📊 Your Responses Summary")
    
    if st.session_state.responses:
        df_responses = pd.DataFrame(st.session_state.responses)
        
        # Show summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Evaluated", len(df_responses))
        with col2:
            # Get average seniority perception
            seniority_scores = [r.get('perceived_seniority_numeric', 0) for r in st.session_state.responses]
            st.metric("Avg Perceived Seniority", f"{np.mean(seniority_scores):.2f}/4" if seniority_scores else "N/A")
        with col3:
            # Get average hastiness perception
            hastiness_scores = [r.get('perceived_hastiness_numeric', 0) for r in st.session_state.responses]
            st.metric("Avg Perceived Hastiness", f"{np.mean(hastiness_scores):.2f}/5" if hastiness_scores else "N/A")
        
        st.dataframe(df_responses, use_container_width=True)
        
        # Download button
        csv = df_responses.to_csv(index=False)
        st.download_button(
            label="📥 Download Your Responses",
            data=csv,
            file_name=f"survey_responses_{st.session_state.annotator_id}.csv",
            mime="text/csv"
        )
    
    if st.button("🔄 Start New Survey"):
        st.session_state.responses = []
        st.session_state.current_idx = 0
        st.session_state.survey_complete = False
        st.session_state.annotator_id = None
        st.rerun()
    
    st.stop()

# Display current request
current_variation = variations.iloc[current_idx]

# Progress
progress = (current_idx / total_requests) * 100
st.progress(progress / 100)
st.caption(f"Progress: {current_idx + 1} of {total_requests} requests ({progress:.0f}%)")

# Annotator info
st.sidebar.markdown(f"**Annotator:** {st.session_state.annotator_name}")
st.sidebar.markdown(f"**Role:** {st.session_state.annotator_role}")

# Main content
with st.container():
    st.markdown(f"### Request {current_idx + 1} of {total_requests}")
    
    # Display the access request
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**📋 Request Details**")
        st.info(f"**Seniority:** {current_variation['Seniority']}")
        st.info(f"**Hastiness:** {current_variation['Hastiness']}")
    
    with col2:
        st.markdown("**📄 Access Request**")
        st.markdown(
            f"""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50;">
                <p style="margin: 0; font-size: 16px;"><em>"{current_variation['Purpose']}"</em></p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # Evaluation questions
    st.markdown("### 📊 Evaluate This Request")
    st.caption("Please rate the request on each dimension based on your perception.")
    
    # Store responses for this request
    responses = {}
    
    # Display each question
    for dim in EVALUATION_DIMENSIONS:
        st.markdown(f"**{dim['question']}**")
        st.caption(dim['description'])
        
        response = st.radio(
            dim['question'],
            dim['options'],
            key=f"{current_idx}_{dim['id']}",
            index=None,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if response:
            responses[dim['id']] = response
            responses[f"{dim['id']}_numeric"] = map_rating_to_numeric(response, dim['type'])
    
    # Decision question (Accept/Reject)
    st.markdown("**✅ Decision**")
    decision = st.radio(
        "Would you approve this access request?",
        ["Accept", "Reject"],
        key=f"{current_idx}_decision",
        index=None,
        horizontal=True
    )
    
    if decision:
        responses['decision'] = decision
        responses['decision_numeric'] = 1 if decision == "Accept" else 0
    
    # Additional comments
    st.markdown("**💬 Additional Comments (Optional)**")
    comments = st.text_area(
        "Any additional observations about this request?",
        key=f"{current_idx}_comments",
        placeholder="E.g., what influenced your decision, any red flags, etc.",
        height=80
    )
    
    if comments:
        responses['comments'] = comments
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        # Check if all required questions are answered
        required_fields = [dim['id'] for dim in EVALUATION_DIMENSIONS]
        required_fields.append('decision')
        missing_fields = [field for field in required_fields if field not in responses]
        
        submit_disabled = len(missing_fields) > 0
        
        submit_button = st.button(
            "✅ Submit & Next" if current_idx < total_requests - 1 else "✅ Submit & Finish",
            disabled=submit_disabled,
            use_container_width=True,
            type="primary"
        )
    
    if submit_disabled:
        missing_names = []
        for field in missing_fields:
            if field == 'decision':
                missing_names.append("Decision")
            else:
                dim = next((d for d in EVALUATION_DIMENSIONS if d['id'] == field), None)
                if dim:
                    missing_names.append(dim['question'])
        st.warning(f"⚠️ Please answer all questions before submitting. Missing: {', '.join(missing_names)}")
    
    if submit_button:
        # Save response
        response_record = {
            "annotator_id": st.session_state.annotator_id,
            "annotator_name": st.session_state.annotator_name,
            "annotator_role": st.session_state.annotator_role,
            "timestamp": datetime.datetime.now().isoformat(),
            "request_number": current_idx + 1,
            "actual_seniority": current_variation['Seniority'],
            "actual_hastiness": current_variation['Hastiness'],
            "purpose": current_variation['Purpose'],
            **responses
        }
        st.session_state.responses.append(response_record)
        
        # Move to next request
        st.session_state.current_idx += 1
        st.rerun()

# Sidebar - Progress and Info
with st.sidebar:
    st.divider()
    
    st.markdown("### 📈 Progress Summary")
    completed = len(st.session_state.responses)
    st.metric("Completed", f"{completed}/{total_requests}")
    
    # Show completed requests
    if st.session_state.responses:
        st.markdown("**✅ Completed:**")
        for resp in st.session_state.responses[-5:]:
            st.caption(f"• #{resp['request_number']}: {resp['actual_seniority']} - {resp['actual_hastiness']}")
        if len(st.session_state.responses) > 5:
            st.caption(f"... and {len(st.session_state.responses) - 5} more")
    
    st.divider()
    
    st.markdown("""
    ### 📋 Evaluation Guidelines
    
    1. **Read** the access request carefully
    2. **Rate** on each dimension based on your perception
    3. **Decide** whether to Accept or Reject
    4. **Comment** if you notice anything noteworthy
    
    ### 🎯 What to Look For
    
    - **Language style** (formal vs informal)
    - **Completeness** of information
    - **Urgency** conveyed
    - **Professionalism** of the request
    - **Trustworthiness** of the request
    """)
    
    # Export option
    if st.session_state.responses and st.button("📊 Export Progress"):
        df_progress = pd.DataFrame(st.session_state.responses)
        csv_progress = df_progress.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_progress,
            file_name=f"survey_progress_{st.session_state.annotator_id}.csv",
            mime="text/csv"
        )