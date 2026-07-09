
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


#Giving the user an option to select which dataset to preview
with st.sidebar:
    st.header("Data")
    
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

#Making a contents side bar
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Results Summary",
    "Bar Charts",
    "Pie Charts",
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
    
    st.subheader("Acceptance Rate (%) - Normal Summary")
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Variation', y='Acceptance Rate(%)', data=normal_summary)
    plt.xticks(rotation=45)
    plt.title("Acceptance Rate (%) by Variation - Normal Summary")
    st.pyplot(plt.gcf())
    
    st.subheader("Rejection Rate (%) - Normal Summary")
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Variation', y='Rejection Rate(%)', data=normal_summary)
    plt.xticks(rotation=45)
    plt.title("Rejection Rate (%) by Variation - Normal Summary")
    st.pyplot(plt.gcf())
    
    st.subheader("Acceptance Rate (%) - Warning Summary")
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Variation', y='Acceptance Rate(%)', data=warning_summary)
    plt.xticks(rotation=45)
    plt.title("Acceptance Rate (%) by Variation - Warning Summary")
    st.pyplot(plt.gcf())
    
    st.subheader("Rejection Rate (%) - Warning Summary")
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Variation', y='Rejection Rate(%)', data=warning_summary)
    plt.xticks(rotation=45)
    plt.title("Rejection Rate (%) by Variation - Warning Summary")
    st.pyplot(plt.gcf())