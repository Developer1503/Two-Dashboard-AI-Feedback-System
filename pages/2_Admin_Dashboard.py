"""
Admin Dashboard - Fynd AI Intern Assessment Task 2
Internal-facing interface for viewing all reviews and AI analysis
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="📊",
    layout="wide"
)

# Data file path
DATA_FILE = "data/reviews.csv"

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Initialize CSV if it doesn't exist
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        'timestamp', 'rating', 'review', 'ai_response', 
        'ai_summary', 'recommended_actions'
    ])
    df.to_csv(DATA_FILE, index=False)

@st.cache_data(ttl=30)  # Cache for 30 seconds for live updates
def load_data():
    """Load review data from CSV"""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if len(df) > 0:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    return pd.DataFrame()

def get_rating_emoji(rating):
    """Return emoji for rating"""
    emojis = {1: "😞", 2: "😕", 3: "😐", 4: "👍", 5: "😊"}
    return emojis.get(rating, "⭐")

# ============================================================================
# HEADER
# ============================================================================

st.title("📊 Admin Dashboard")
st.markdown("Real-time monitoring of customer reviews and AI-generated insights")

# Auto-refresh button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ============================================================================
# LOAD DATA
# ============================================================================

df = load_data()

if df.empty:
    st.info("📭 No reviews yet. Waiting for submissions...")
    st.markdown("""
    ### Getting Started
    1. Share the User Dashboard link with customers
    2. Reviews will appear here in real-time
    3. AI analysis will be automatically generated
    """)
    st.stop()

# ============================================================================
# KEY METRICS
# ============================================================================

st.markdown("### 📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Reviews",
        len(df),
        delta=f"+{len(df[df['timestamp'] > (datetime.now() - timedelta(days=1))])} today"
    )

with col2:
    avg_rating = df['rating'].mean()
    st.metric(
        "Average Rating",
        f"{avg_rating:.2f} ⭐",
        delta=f"{avg_rating - 3:.2f} vs neutral"
    )

with col3:
    positive_reviews = len(df[df['rating'] >= 4])
    positive_pct = (positive_reviews / len(df)) * 100
    st.metric(
        "Positive Reviews",
        f"{positive_pct:.1f}%",
        delta=f"{positive_reviews} reviews"
    )

with col4:
    critical_reviews = len(df[df['rating'] <= 2])
    st.metric(
        "Critical Reviews",
        critical_reviews,
        delta="Needs attention" if critical_reviews > 0 else "All good",
        delta_color="inverse"
    )

st.markdown("---")

# ============================================================================
# ANALYTICS VISUALIZATIONS
# ============================================================================

st.markdown("### 📊 Analytics")

tab1, tab2, tab3 = st.tabs(["Rating Distribution", "Timeline", "Insights"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Rating distribution bar chart
        rating_counts = df['rating'].value_counts().sort_index()
        fig = px.bar(
            x=rating_counts.index,
            y=rating_counts.values,
            labels={'x': 'Rating (Stars)', 'y': 'Number of Reviews'},
            title='Rating Distribution',
            color=rating_counts.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(showlegend=False, xaxis={'tickmode': 'linear', 'tick0': 1, 'dtick': 1})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Rating pie chart
        fig = go.Figure(data=[go.Pie(
            labels=[f"{i} ⭐" for i in rating_counts.index],
            values=rating_counts.values,
            hole=.4,
            marker_colors=['#ff4444', '#ff8844', '#ffcc44', '#88cc44', '#44cc44']
        )])
        fig.update_layout(title='Rating Proportions')
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Reviews over time
    df_timeline = df.copy()
    df_timeline['date'] = df_timeline['timestamp'].dt.date
    daily_reviews = df_timeline.groupby('date').agg({
        'rating': ['count', 'mean']
    }).reset_index()
    daily_reviews.columns = ['date', 'count', 'avg_rating']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_reviews['date'],
        y=daily_reviews['count'],
        mode='lines+markers',
        name='Number of Reviews',
        line=dict(color='#1f77b4', width=2)
    ))
    fig.update_layout(
        title='Reviews Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Reviews'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔥 Most Common Issues")
        critical_df = df[df['rating'] <= 2]
        if len(critical_df) > 0:
            for idx, row in critical_df.head(3).iterrows():
                st.warning(f"**{row['rating']}⭐**: {row['ai_summary']}")
        else:
            st.success("No critical issues reported!")
    
    with col2:
        st.markdown("#### ⭐ Recent Highlights")
        positive_df = df[df['rating'] == 5]
        if len(positive_df) > 0:
            for idx, row in positive_df.head(3).iterrows():
                st.success(f"**5⭐**: {row['ai_summary']}")
        else:
            st.info("No 5-star reviews yet")

st.markdown("---")

# ============================================================================
# FILTERS
# ============================================================================

st.markdown("### 🔍 Review Filters")

col1, col2, col3 = st.columns(3)

with col1:
    rating_filter = st.multiselect(
        "Filter by Rating",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
        format_func=lambda x: f"{x} ⭐"
    )

with col2:
    date_filter = st.selectbox(
        "Filter by Date",
        ["All Time", "Today", "Last 7 Days", "Last 30 Days"]
    )

with col3:
    sort_order = st.selectbox(
        "Sort by",
        ["Newest First", "Oldest First", "Highest Rating", "Lowest Rating"]
    )

# Apply filters
filtered_df = df[df['rating'].isin(rating_filter)]

# Date filtering
if date_filter == "Today":
    filtered_df = filtered_df[filtered_df['timestamp'].dt.date == datetime.now().date()]
elif date_filter == "Last 7 Days":
    filtered_df = filtered_df[filtered_df['timestamp'] > (datetime.now() - timedelta(days=7))]
elif date_filter == "Last 30 Days":
    filtered_df = filtered_df[filtered_df['timestamp'] > (datetime.now() - timedelta(days=30))]

# Sorting
if sort_order == "Newest First":
    filtered_df = filtered_df.sort_values('timestamp', ascending=False)
elif sort_order == "Oldest First":
    filtered_df = filtered_df.sort_values('timestamp', ascending=True)
elif sort_order == "Highest Rating":
    filtered_df = filtered_df.sort_values('rating', ascending=False)
elif sort_order == "Lowest Rating":
    filtered_df = filtered_df.sort_values('rating', ascending=True)

st.markdown(f"Showing **{len(filtered_df)}** reviews")
st.markdown("---")

# ============================================================================
# DETAILED REVIEWS LIST
# ============================================================================

st.markdown("### 📋 All Submissions")
st.markdown("**Live-updating list showing:**")
st.markdown("""
- ⭐ User rating
- 📝 User review  
- 🤖 AI-generated summary
- 💡 AI-suggested recommended actions
""")

if filtered_df.empty:
    st.info("No reviews match your filters.")
else:
    for idx, row in filtered_df.iterrows():
        # Create expandable card for each review
        with st.expander(
            f"{get_rating_emoji(row['rating'])} {row['rating']}⭐ - {row['timestamp'].strftime('%Y-%m-%d %H:%M')} - {row['ai_summary'][:50]}...",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📝 User Review")
                st.markdown(f"**User Rating:** {row['rating']} ⭐")
                st.write(row['review'])
                
                st.markdown("#### 🤖 AI Response (Sent to Customer)")
                st.info(row['ai_response'])
            
            with col2:
                st.markdown("#### 📊 Admin Insights")
                
                # Rating indicator
                rating_color = "green" if row['rating'] >= 4 else "orange" if row['rating'] == 3 else "red"
                st.markdown(f"**Rating:** :{rating_color}[{row['rating']} ⭐]")
                
                # AI-generated Summary (as per requirements)
                st.markdown("**AI-Generated Summary:**")
                st.info(row['ai_summary'])
                
                # AI-suggested Recommended Actions (as per requirements)
                st.markdown("**AI-Suggested Recommended Actions:**")
                st.warning(row['recommended_actions'])
                
                # Timestamp
                st.caption(f"Submitted: {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# EXPORT DATA
# ============================================================================

st.markdown("---")
st.markdown("### 💾 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    # Download CSV
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    # Download critical reviews only
    critical_csv = filtered_df[filtered_df['rating'] <= 2].to_csv(index=False)
    st.download_button(
        label="⚠️ Download Critical Reviews",
        data=critical_csv,
        file_name=f"critical_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col3:
    # Clear all data (with confirmation)
    if st.button("🗑️ Clear All Data", use_container_width=True):
        st.warning("⚠️ This action cannot be undone!")
        if st.button("Confirm Delete"):
            pd.DataFrame(columns=df.columns).to_csv(DATA_FILE, index=False)
            st.success("All data cleared!")
            st.cache_data.clear()
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>Auto-refreshes every 30 seconds | Click 🔄 Refresh for immediate update</small>
    </div>
    """,
    unsafe_allow_html=True
)
