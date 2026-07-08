import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import re
from wordcloud import WordCloud

# Page configuration
st.set_page_config(
    page_title="Evaluation Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Evaluation Analysis Dashboard")
st.markdown("---")

# Load data function with caching
@st.cache_data
def load_data():
    normal_summary = pd.read_csv('evaluation_summary.csv')
    warning_summary = pd.read_csv('warning_evaluation_summary.csv')
    return normal_summary, warning_summary

try:
    normal_summary, warning_summary = load_data()
except FileNotFoundError:
    st.error("❌ CSV files not found. Please make sure 'evaluation_summary.csv' and 'warning_evaluation_summary.csv' are in the same directory.")
    st.stop()

# Convert percentage columns to float
normal_summary['Acceptance Rate(%)'] = normal_summary['Acceptance Rate'].str.rstrip('%').astype(float)
normal_summary['Rejection Rate(%)'] = normal_summary['Rejection Rate'].str.rstrip('%').astype(float)

warning_summary['Acceptance Rate(%)'] = warning_summary['Acceptance Rate'].str.rstrip('%').astype(float)
warning_summary['Rejection Rate(%)'] = warning_summary['Rejection Rate'].str.rstrip('%').astype(float)

# Helper function to create pivot tables
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

# Sidebar - Data Preview
with st.sidebar:
    st.header("📁 Data Preview")
    
    data_choice = st.selectbox(
        "Select dataset to preview:",
        ["Normal Summary", "Warning Summary"]
    )
    
    if data_choice == "Normal Summary":
        st.dataframe(normal_summary.head(10))
        st.caption(f"Shape: {normal_summary.shape}")
    else:
        st.dataframe(warning_summary.head(10))
        st.caption(f"Shape: {warning_summary.shape}")

# Main content - Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Heatmaps", 
    "📊 Bar Charts", 
    "🥧 Pie Charts",
    "📝 Text Analysis",
    "📋 Summary Tables"
])

# Tab 1: Heatmaps
with tab1:
    st.header("🔥 Heatmaps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Normal Acceptance Rate")
        seniority = ["Intern", "Junior Analyst", "Senior Manager", "Executive/CEO"]
        hastiness = ["Neutral", "Very Formal", "Very Hasty"]
        
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            normal_pivot,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            vmin=0,
            vmax=100,
            xticklabels=hastiness,
            yticklabels=seniority,
            cbar_kws={'label': 'Acceptance Rate (%)'},
            annot_kws={'size': 11, 'weight': 'bold'},
            ax=ax
        )
        ax.set_title('Acceptance Rate by Seniority and Hastiness', fontsize=12, fontweight='bold')
        ax.set_xlabel('Hastiness', fontsize=10)
        ax.set_ylabel('Seniority', fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Rejection heatmap
        rejection_pivot = 100 - normal_pivot
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            rejection_pivot,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn_r',
            vmin=0,
            vmax=100,
            xticklabels=hastiness,
            yticklabels=seniority,
            cbar_kws={'label': 'Rejection Rate (%)'},
            annot_kws={'size': 11, 'weight': 'bold'},
            ax=ax2
        )
        ax2.set_title('Rejection Rate by Seniority and Hastiness', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Hastiness', fontsize=10)
        ax2.set_ylabel('Seniority', fontsize=10)
        plt.tight_layout()
        st.pyplot(fig2)
    
    with col2:
        st.subheader("Warning Acceptance Rate")
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            warning_pivot,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            vmin=0,
            vmax=100,
            xticklabels=hastiness,
            yticklabels=seniority,
            cbar_kws={'label': 'Acceptance Rate (%)'},
            annot_kws={'size': 11, 'weight': 'bold'},
            ax=ax3
        )
        ax3.set_title('Acceptance Rate by Seniority and Hastiness (Warning)', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Hastiness', fontsize=10)
        ax3.set_ylabel('Seniority', fontsize=10)
        plt.tight_layout()
        st.pyplot(fig3)
        
        # Warning rejection heatmap
        warning_rejection_pivot = 100 - warning_pivot
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            warning_rejection_pivot,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn_r',
            vmin=0,
            vmax=100,
            xticklabels=hastiness,
            yticklabels=seniority,
            cbar_kws={'label': 'Rejection Rate (%)'},
            annot_kws={'size': 11, 'weight': 'bold'},
            ax=ax4
        )
        ax4.set_title('Rejection Rate by Seniority and Hastiness (Warning)', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Hastiness', fontsize=10)
        ax4.set_ylabel('Seniority', fontsize=10)
        plt.tight_layout()
        st.pyplot(fig4)

# Tab 2: Bar Charts
with tab2:
    st.header("📊 Bar Charts")
    
    chart_type = st.radio(
        "Select chart type:",
        ["Accepted Count Comparison", "Rejected Count Comparison"],
        horizontal=True
    )
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if chart_type == "Accepted Count Comparison":
        ax.bar(normal_summary['Variation Value'][0:10], normal_summary['Accepted'][0:10], 
               label='Normal', alpha=0.7)
        ax.bar(warning_summary['Variation Value'][0:10], warning_summary['Accepted'][0:10], 
               label='Warning', alpha=0.7)
        ax.set_ylabel('Accepted Count')
        ax.set_title('Comparison of Accepted Count for Normal and Warning Variations')
    else:
        ax.bar(warning_summary['Variation Value'][0:10], warning_summary['Rejected'][0:10], 
               label='Warning', alpha=0.7)
        ax.bar(normal_summary['Variation Value'][0:10], normal_summary['Rejected'][0:10], 
               label='Normal', alpha=0.7)
        ax.set_ylabel('Rejected Count')
        ax.set_title('Comparison of Rejected Count for Normal and Warning Variations')
    
    ax.set_xlabel('Variation Value')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)

# Tab 3: Pie Charts
with tab3:
    st.header("🥧 Acceptance vs Rejection Rates")
    
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

# Tab 4: Text Analysis
with tab4:
    st.header("📝 Text Analysis - Very Hasty Variations")
    
    # Load combined data for text analysis
    try:
        df = pd.read_csv('combined_variations.csv')
        
        # Filter for "very hasty" variations
        hasty_df = df[df['Variation Value'].str.contains('very hasty', case=False, na=False)]
        
        # Get text from Purpose column
        text = ' '.join(hasty_df['Purpose'].dropna().astype(str))
        cleaned = re.sub(r'[^\w\s]', '', text.lower())
        words = cleaned.split()
        
        # Count all words
        all_word_counts = Counter(words)
        
        # Define casual words
        casual_words = [
            'gotta', 'stuff', 'ppl', 'like', 'wanna', 'gonna', 'thx', 'thanks', 'hey', 
            'asap', 'pls', 'please', 'cool', 'yeah', 'ok', 'okay', 'btw', 'lol', 'omg',
            'u', 'ur', 'r', '2', '4', 'tho', 'though', 'dont', 'dunno', 'kinda', 
            'sorta', 'cuz', 'cause', 'gimme', 'lemme', 'nah', 'yep', 'nope', 'ya',
            'bro', 'guys', 'folks', 'peeps', 'team', 'quick', 'fast', 'pronto',
            'basically', 'actually', 'literally', 'seriously', 'honestly'
        ]
        
        # Filter casual words
        casual_word_counts = {word: count for word, count in all_word_counts.items() 
                              if word in casual_words and count > 0}
        sorted_casual = sorted(casual_word_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Display casual words
        st.subheader("🔤 Casual/Informal Words in Very Hasty Variations")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create a DataFrame for display
            casual_df = pd.DataFrame(sorted_casual, columns=['Word', 'Frequency'])
            st.dataframe(casual_df, use_container_width=True)
        
        with col2:
            st.metric("Total Casual Words Found", len(casual_word_counts))
            st.metric("Most Common", f"{sorted_casual[0][0]} ({sorted_casual[0][1]}×)" if sorted_casual else "N/A")
        
        # Word cloud
        st.subheader("☁️ Word Cloud - Casual Words")
        
        if casual_word_counts:
            casual_word_freq = {word: count for word, count in all_word_counts.items() 
                                if word in casual_words and count > 5}
            
            if casual_word_freq:
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='white',
                    colormap='rocket',
                    max_words=50
                ).generate_from_frequencies(casual_word_freq)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('Casual Words in Very Hasty Variations', fontsize=14, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("Not enough casual words with frequency > 5 to generate word cloud.")
        else:
            st.info("No casual words found.")
            
    except FileNotFoundError:
        st.warning("⚠️ 'combined_variations.csv' not found. Text analysis not available.")

# Tab 5: Summary Tables
with tab5:
    st.header("📋 Summary Tables")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Normal Summary - Pivot Table")
        st.dataframe(normal_pivot, use_container_width=True)
        
        st.subheader("Normal Summary - Data")
        st.dataframe(normal_summary, use_container_width=True)
    
    with col2:
        st.subheader("Warning Summary - Pivot Table")
        st.dataframe(warning_pivot, use_container_width=True)
        
        st.subheader("Warning Summary - Data")
        st.dataframe(warning_summary, use_container_width=True)

# Footer
st.markdown("---")
st.caption("📊 Dashboard created from evaluation analysis data")