import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.queries import get_engine
from sqlalchemy import text

st.set_page_config(
    page_title="Nepal Job Market Intelligence",
    page_icon="🇳🇵",
    layout="wide"
)

@st.cache_data(ttl=300)
def load_jobs():
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM jobs", conn)
    return df

@st.cache_data(ttl=300)
def load_skills():
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql("""
            SELECT s.skill_name, s.category, j.source, j.is_remote, j.location
            FROM skills s
            JOIN jobs j ON s.job_id = j.id
        """, conn)
    return df

# --- HEADER ---
st.title("🇳🇵 Nepal Job Market Intelligence")
st.markdown("*Real-time insights from Merojob & Himalayas — built by a Nepali job seeker*")
st.divider()

# --- LOAD DATA ---
jobs_df = load_jobs()
skills_df = load_skills()

# --- KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💼 Total Jobs", len(jobs_df))
with col2:
    st.metric("🌐 Remote Jobs", len(jobs_df[jobs_df['is_remote'] == True]))
with col3:
    st.metric("🏢 Local Jobs", len(jobs_df[jobs_df['is_remote'] == False]))
with col4:
    st.metric("🧠 Skills Tracked", skills_df['skill_name'].nunique())

st.divider()

# --- ROW 1: Top Skills + Job Sources ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top In-Demand Skills")
    top_skills = (
        skills_df.groupby('skill_name')
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
        .head(15)
    )
    fig = px.bar(
        top_skills,
        x='count',
        y='skill_name',
        orientation='h',
        color='count',
        color_continuous_scale='Blues',
        labels={'count': 'Job Count', 'skill_name': 'Skill'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=450)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Jobs by Source")
    source_counts = jobs_df['source'].value_counts().reset_index()
    source_counts.columns = ['source', 'count']
    fig2 = px.pie(
        source_counts,
        values='count',
        names='source',
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4
    )
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- ROW 2: Remote vs Local + Skills by Category ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 Remote vs Local Jobs")
    remote_counts = jobs_df['is_remote'].value_counts().reset_index()
    remote_counts.columns = ['type', 'count']
    remote_counts['type'] = remote_counts['type'].map({True: 'Remote', False: 'Local'})
    fig3 = px.pie(
        remote_counts,
        values='count',
        names='type',
        color_discrete_map={'Remote': '#2ecc71', 'Local': '#3498db'},
        hole=0.4
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("🗂️ Skills by Category")
    cat_counts = skills_df['category'].value_counts().reset_index()
    cat_counts.columns = ['category', 'count']
    fig4 = px.bar(
        cat_counts,
        x='category',
        y='count',
        color='category',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={'count': 'Skill Mentions', 'category': 'Category'}
    )
    fig4.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# --- ROW 3: Top Hiring Companies + Locations ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 Top Hiring Companies")
    top_companies = (
        jobs_df[jobs_df['company'].notna()]
        .groupby('company')
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
        .head(10)
    )
    fig5 = px.bar(
        top_companies,
        x='count',
        y='company',
        orientation='h',
        color='count',
        color_continuous_scale='Greens',
        labels={'count': 'Job Count', 'company': 'Company'}
    )
    fig5.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.subheader("📍 Jobs by Location")
    top_locations = (
        jobs_df[jobs_df['location'].notna()]
        .groupby('location')
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
        .head(10)
    )
    fig6 = px.bar(
        top_locations,
        x='count',
        y='location',
        orientation='h',
        color='count',
        color_continuous_scale='Oranges',
        labels={'count': 'Job Count', 'location': 'Location'}
    )
    fig6.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
    st.plotly_chart(fig6, use_container_width=True)

st.divider()

# --- JOB TABLE ---
st.subheader("📋 Browse All Jobs")

col1, col2, col3 = st.columns(3)
with col1:
    source_filter = st.selectbox("Filter by Source", ["All"] + list(jobs_df['source'].unique()))
with col2:
    remote_filter = st.selectbox("Filter by Type", ["All", "Remote", "Local"])
with col3:
    search = st.text_input("Search by title or company", "")

filtered = jobs_df.copy()
if source_filter != "All":
    filtered = filtered[filtered['source'] == source_filter]
if remote_filter == "Remote":
    filtered = filtered[filtered['is_remote'] == True]
elif remote_filter == "Local":
    filtered = filtered[filtered['is_remote'] == False]
if search:
    filtered = filtered[
        filtered['title'].str.contains(search, case=False, na=False) |
        filtered['company'].str.contains(search, case=False, na=False)
    ]

st.dataframe(
    filtered[['title', 'company', 'location', 'job_type', 'source', 'is_remote', 'source_url']]
    .rename(columns={
        'title': 'Job Title',
        'company': 'Company',
        'location': 'Location',
        'job_type': 'Type',
        'source': 'Source',
        'is_remote': 'Remote',
        'source_url': 'URL'
    }),
    use_container_width=True,
    height=400
)

st.caption("Data sourced from Merojob & Himalayas • Refreshes every 5 minutes")