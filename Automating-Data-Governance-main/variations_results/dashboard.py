
#importing libraries
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from wordcloud import WordCloud


#setting up the page
st.set_page_config(page_title="Linguistic Variation in Data Governance AI Results", layout="wide")

#page title
st.title("Linguistic Variation in Data Governance AI Results")

#loading up the data files
@st.cache_data
def load_data():
    normal_summary = pd.read_csv('variations_results/evaluation_summary.csv')
    warning_summary = pd.read_csv('variations_results/warning_evaluation_summary.csv')
    return normal_summary, warning_summary

try:
    normal_summary, warning_summary = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

if 'Acceptance Rate' in normal_summary.columns:
    normal_summary['Acceptance Rate(%)'] = normal_summary['Acceptance Rate'].str.rstrip('%').astype(float)
    normal_summary['Rejection Rate(%)'] = normal_summary['Rejection Rate'].str.rstrip('%').astype(float)
    
    warning_summary['Acceptance Rate(%)'] = warning_summary['Acceptance Rate'].str.rstrip('%').astype(float)
    warning_summary['Rejection Rate(%)'] = warning_summary['Rejection Rate'].str.rstrip('%').astype(float)
else:
    # If columns already have (%) in name
    normal_summary['Acceptance Rate(%)'] = normal_summary['Acceptance Rate(%)'].astype(float)
    normal_summary['Rejection Rate(%)'] = normal_summary['Rejection Rate(%)'].astype(float)
    
    warning_summary['Acceptance Rate(%)'] = warning_summary['Acceptance Rate(%)'].astype(float)
    warning_summary['Rejection Rate(%)'] = warning_summary['Rejection Rate(%)'].astype(float)


#Making a contents side bar
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Results Summary",
    "Bar Charts",
    "Pie Charts",
    "Heatmaps",
    "Text Analysis"
])

#Tab 1- giving a summary of the results
with tab1:
    st.header("Results Summary")
    
    st.subheader("Normal Summary")
    st.dataframe(normal_summary)
    
    st.subheader("Warning Summary")
    st.dataframe(warning_summary)

#Tab 2- bar charts for acceptance and rejection rates
with tab2:
    st.header("Bar Charts")

    #making a radio button for the user to select which data type to view
    data_type = st.radio(
        "Select data type:",
        ["Normal Variations", "Warning Variations", "Both Variations"],
        horizontal=True,
        key="bar_chart_data_type"
    )
    if data_type == "Normal Variations":
        plt.figure(figsize=(50, 6))
        plt.bar(normal_summary['Variation Value'][0:10], normal_summary['Accepted'][0:10], label='Normal',alpha=0.7)
        plt.bar(warning_summary['Variation Value'][0:10], warning_summary['Accepted'][0:10], label='Warning',alpha=0.7)
        plt.xlabel('Variation Value')
        plt.ylabel('Accepted Count')
        plt.title('Comparison of Accepted Count for Normal and Warning Variations')
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(plt)
    elif data_type == "Warning Variations":
        plt.figure(figsize=(50, 6))
        plt.bar(warning_summary['Variation Value'][0:10], warning_summary['Rejected'][0:10], label='Warning',alpha=0.7)
        plt.bar(normal_summary['Variation Value'][0:10], normal_summary['Rejected'][0:10], label='Normal',alpha=0.7)
        plt.xlabel('Variation Value')
        plt.ylabel('Rejected Count')
        plt.title('Comparison of Rejected Count for Normal and Warning Variations')
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(plt)
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Normal Variations")
            plt.figure(figsize=(50, 6))
            plt.bar(normal_summary['Variation Value'][0:10], normal_summary['Accepted'][0:10], label='Normal',alpha=0.7)
            plt.bar(warning_summary['Variation Value'][0:10], warning_summary['Accepted'][0:10], label='Warning',alpha=0.7)
            plt.xlabel('Variation Value')
            plt.ylabel('Accepted Count')
            plt.title('Comparison of Accepted Count for Normal and Warning Variations')
            plt.xticks(rotation=45)
            plt.legend()
            st.pyplot(plt)
        with col2:
            st.subheader("Warning Variations")
            plt.figure(figsize=(50, 6))
            plt.bar(warning_summary['Variation Value'][0:10], warning_summary['Rejected'][0:10], label='Warning',alpha=0.7)
            plt.bar(normal_summary['Variation Value'][0:10], normal_summary['Rejected'][0:10], label='Normal',alpha=0.7)
            plt.xlabel('Variation Value')
            plt.ylabel('Rejected Count')
            plt.title('Comparison of Rejected Count for Normal and Warning Variations')
            plt.xticks(rotation=45)
            plt.legend()
            st.pyplot(plt)


#Tab 3- pie charts for acceptance and rejection rates
with tab3:
    st.header("Pie Charts")

    #making another radio button for accpetance and rejection rates

    data_type1 = st.radio(
        "Select Data type:",
        ["Normal Variations", "Warning Variations", "Both Variations"],
        horizontal=True,
        key="pie_chart_data_type"
    )

    if data_type1 == "Normal Variations":
        normal_acceptance = normal_summary['Accepted'].sum()
        normal_rejection = normal_summary['Rejected'].sum()
        
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(
            [normal_acceptance, normal_rejection], 
            labels=['Accepted', 'Rejected'], 
            autopct='%1.1f%%', 
            startangle=90,
            colors=['#2ecc71', '#e74c3c']
        )
        ax.set_title('Acceptance vs Rejection Rate for Normal Variations')
        st.pyplot(fig)
    elif data_type1 == "Warning Variations":
        st.subheader("Warning Variations")
        warning_acceptance = warning_summary['Accepted'].sum()
        warning_rejection = warning_summary['Rejected'].sum()
        
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(
            [warning_acceptance, warning_rejection], 
            labels=['Accepted', 'Rejected'], 
            autopct='%1.1f%%', 
            startangle=90,
            colors=['#2ecc71', '#e74c3c']
        )
        ax.set_title('Acceptance vs Rejection Rate for Warning Variations')
        st.pyplot(fig)
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Normal Variations")
            normal_acceptance = normal_summary['Accepted'].sum()
            normal_rejection = normal_summary['Rejected'].sum()
            
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.pie(
                [normal_acceptance, normal_rejection], 
                labels=['Accepted', 'Rejected'], 
                autopct='%1.1f%%', 
                startangle=90,
                colors=['#2ecc71', '#e74c3c']
            )
            ax.set_title('Acceptance vs Rejection Rate for Normal Variations')
            st.pyplot(fig)
        
        with col2:
            st.subheader("Warning Variations")
            warning_acceptance = warning_summary['Accepted'].sum()
            warning_rejection = warning_summary['Rejected'].sum()
            
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.pie(
                [warning_acceptance, warning_rejection], 
                labels=['Accepted', 'Rejected'], 
                autopct='%1.1f%%', 
                startangle=90,
                colors=['#2ecc71', '#e74c3c']
            )
            ax.set_title('Acceptance vs Rejection Rate for Warning Variations')
            st.pyplot(fig)


#Tab 4- making a heatmap for acceptance and rejection rates
#making a pivot table for the heatmap
def create_pivot(df):
    heatmap_df = df[df['Variation Type'] == 'combined'].copy()
    
    def extract_seniority(value):
        parts = value.split(' + ')
        return parts[0].strip()
    
    def extract_hastiness(value):
        parts = value.split(' + ')
        if len(parts) > 1:
            hastiness = parts[1].strip().lower()
            if 'neutral' in hastiness:
                return 'Neutral'
            elif 'very formal' in hastiness:
                return 'Very Formal'
            elif 'very hasty' in hastiness:
                return 'Very Hasty'
        return None
    
    heatmap_df['Seniority'] = heatmap_df['Variation Value'].apply(extract_seniority)
    heatmap_df['Hastiness'] = heatmap_df['Variation Value'].apply(extract_hastiness)
    
    seniority_map = {
        'intern': 'Intern',
        'junior analyst': 'Junior Analyst',
        'senior manager': 'Senior Manager',
        'executive/CEO': 'Executive/CEO'
    }
    heatmap_df['Seniority'] = heatmap_df['Seniority'].map(seniority_map)
    
    pivot = heatmap_df.pivot_table(
        index='Seniority',
        columns='Hastiness',
        values='Acceptance Rate(%)'
    )
    
    seniority_order = ["Intern", "Junior Analyst", "Senior Manager", "Executive/CEO"]
    hastiness_order = ["Neutral", "Very Formal", "Very Hasty"]
    
    return pivot.reindex(index=seniority_order, columns=hastiness_order)

# Create pivot tables
normal_pivot = create_pivot(normal_summary)
warning_pivot = create_pivot(warning_summary)

# Create rejection pivot tables (100 - acceptance)
normal_rejection_pivot = 100 - normal_pivot
warning_rejection_pivot = 100 - warning_pivot

#making the heatmaps
with tab4:
    st.header("Heatmaps")
    #making a radio button for the user to select which data type to view
    data_type2 = st.radio(
        "Select data type:",
        ["Normal Variations", "Warning Variations", "Both Variations"],
        horizontal=True,
        key="heatmap_data_type"
    )
    #making another radio button for accpetance and rejection rates
    rate_type1 = st.radio(
        "Select rate type:",
        ["Acceptance Rate", "Rejection Rate"],
        horizontal=True,
        key="heatmap_rate_type"
    )

    # Select the correct pivot based on rate type
    if rate_type1 == "Acceptance Rate":
        normal_pivot_display = normal_pivot
        warning_pivot_display = warning_pivot
        title_suffix = "Acceptance Rate"
        cmap = "YlGnBu"
    else:
        normal_pivot_display = normal_rejection_pivot
        warning_pivot_display = warning_rejection_pivot
        title_suffix = "Rejection Rate"
        cmap = "YlOrRd"

    if data_type2 == "Normal Variations":
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(normal_pivot_display, annot=True, fmt=".1f", cmap=cmap, vmin=0, vmax=100, ax=ax)
        ax.set_title(f"{title_suffix} Heatmap for Normal Variations")
        st.pyplot(fig)

    elif data_type2 == "Warning Variations":
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(warning_pivot_display, annot=True, fmt=".1f", cmap=cmap, vmin=0, vmax=100, ax=ax)
        ax.set_title(f"{title_suffix} Heatmap for Warning Variations")
        st.pyplot(fig)

    else:  # Both Variations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Normal Variations")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.heatmap(normal_pivot_display, annot=True, fmt=".1f", cmap=cmap, vmin=0, vmax=100, ax=ax)
            ax.set_title(f"{title_suffix} Heatmap for Normal Variations")
            st.pyplot(fig)
        
        with col2:
            st.subheader("Warning Variations")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.heatmap(warning_pivot_display, annot=True, fmt=".1f", cmap=cmap, vmin=0, vmax=100, ax=ax)
            ax.set_title(f"{title_suffix} Heatmap for Warning Variations")
            st.pyplot(fig)
# Tab 5- text analysis for the variations
with tab5:
    st.header("Text Analysis")
    data_type2 = st.radio(
        "Select data type:",
        ["Normal Variations", "Warning Variations", "Both Variations"],
        horizontal=True,
        key="text_data_type"
    )
    if data_type2 == "Normal Variations":
        st.subheader("Normal Variations")


        df = pd.read_csv('variations_results/combined_variations.csv')

        # Filter for "very hasty" variations
        hasty_df = df[df['Variation Value'].str.contains('very hasty', case=False, na=False)]

        # Get text from Purpose column
        text = ' '.join(hasty_df['Purpose'].dropna().astype(str))

        # Clean and split
        cleaned = re.sub(r'[^\w\s]', '', text.lower())
        words = cleaned.split()

        # Count all words
        all_word_counts = Counter(words)

        # Define the casual/informal words you want to track
        casual_words = [
            'gotta', 'stuff', 'ppl', 'like', 'wanna', 'gonna', 'thx', 'thanks', 'hey', 
            'asap', 'pls', 'please', 'cool', 'yeah', 'ok', 'okay', 'btw', 'lol', 'omg',
            'u', 'ur', 'r', '2', '4', 'tho', 'though', 'dont', 'dunno', 'kinda', 
            'sorta', 'cuz', 'cause', 'gimme', 'lemme', 'nah', 'yep', 'nope', 'ya',
            'bro', 'guys', 'folks', 'peeps', 'team', 'quick', 'fast', 'pronto',
            'basically', 'actually', 'literally', 'seriously', 'honestly'
        ]

        # Filter to only show casual words that appear in the data
        casual_word_counts = {word: count for word, count in all_word_counts.items() 
                            if word in casual_words and count > 0}

        # Sort by frequency
        sorted_casual = sorted(casual_word_counts.items(), key=lambda x: x[1], reverse=True)

        # Filter casual words only
        casual_word_freq = {word: count for word, count in all_word_counts.items() 
                            if word in casual_words and count > 5}

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='rocket',
            max_words=50
        ).generate_from_frequencies(casual_word_freq)

        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Casual Words in Very Hasty Variations', fontsize=14, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)


    