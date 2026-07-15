import streamlit as st
import pandas as pd
import random
from pathlib import Path

# Load survey items
@st.cache_data
def load_items():
    df = pd.read_csv('data/survey_items.csv')
    # Filter to only realistic requests
    # df = df[df['Realistic'] == 'Yes']  # Adjust based on your column name
    return df.to_dict('records')

# Initialize session state
if 'items' not in st.session_state:
    all_items = load_items()
    random.shuffle(all_items)
    st.session_state.items = all_items[:50]  # 50 items per user
    st.session_state.current_index = 0
    st.session_state.results = []  # Store annotations
    st.session_state.user_id = f"user_{random.randint(1000, 9999)}"

# Check if finished
if st.session_state.current_index >= len(st.session_state.items):
    st.success("🎉 Thank you! You have completed all items.")
    st.balloons()
    
    # Show download button for results
    if st.session_state.results:
        df_results = pd.DataFrame(st.session_state.results)
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button("Download My Responses", csv, "my_annotations.csv", "text/csv")
    st.stop()

# Get current item
item = st.session_state.items[st.session_state.current_index]

# Display progress
st.progress(st.session_state.current_index / len(st.session_state.items))
st.write(f"Progress: {st.session_state.current_index + 1}/{len(st.session_state.items)}")

# Show the purpose
st.subheader("Access Request:")
st.info(item['purpose'])

# FORM: Batch the 3 ratings into one submission
with st.form(key="survey_form"):
    st.write("**Rate this request on the following scales:**")
    
    # Question 1: Seniority
    seniority = st.slider(
        "1. What seniority level does this request appear to come from?",
        min_value=1, max_value=7, value=4,
        help="1 = Very Junior, 7 = Very Senior"
    )
    
    # Question 2: Hastiness
    hastiness = st.slider(
        "2. How formal or hasty is this request?",
        min_value=1, max_value=7, value=4,
        help="1 = Very Hasty, 7 = Very Formal"
    )
    
    # Question 3: Meaning Preservation
    meaning_preserved = st.slider(
        "3. How well does this request preserve the original meaning?",
        min_value=1, max_value=7, value=4,
        help="1 = Completely Different, 7 = Identical"
    )
    
    # Submit button
    submitted = st.form_submit_button("Submit & Next")
    
    if submitted:
        # Save the annotation
        st.session_state.results.append({
            'user_id': st.session_state.user_id,
            'item_id': item['id'],
            'seniority': seniority,
            'hastiness': hastiness,
            'meaning_preserved': meaning_preserved,
            'variation_type': item.get('variation_type', ''),
        })
        
        # Move to next item
        st.session_state.current_index += 1
        st.rerun()  # Refresh the page to show the next item

# Add a reset button
if st.button("🔄 Start Over"):
    for key in ['items', 'current_index', 'results', 'user_id']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
