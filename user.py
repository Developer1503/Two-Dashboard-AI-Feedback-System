"""
User Dashboard - Fynd AI Intern Assessment Task 2
Public-facing interface for users to submit reviews
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Leave a Review",
    page_icon="⭐",
    layout="centered"
)

# Initialize LLM
@st.cache_resource
def get_llm():
    """Initialize and cache the LLM"""
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found. Please set it in .env or Streamlit secrets.")
        st.stop()
    
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        groq_api_key=api_key
    )

llm = get_llm()

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)
DATA_FILE = "data/reviews.csv"

# Initialize CSV file if it doesn't exist
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        'timestamp', 'rating', 'review', 'ai_response', 
        'ai_summary', 'recommended_actions'
    ])
    df.to_csv(DATA_FILE, index=False)

def generate_ai_response(rating: int, review: str) -> str:
    """Generate AI response to user's review"""
    prompt = PromptTemplate(
        template="""You are a friendly customer service AI. A customer left a {rating}-star review.

Review: {review}

Generate a warm, professional response that:
- Thanks them for their feedback
- Acknowledges their specific points
- If positive (4-5 stars): Express appreciation
- If negative (1-2 stars): Apologize and show empathy
- If neutral (3 stars): Thank them and ask for more details

Keep it brief (2-3 sentences) and genuine.

Response:""",
        input_variables=["rating", "review"]
    )
    
    chain = prompt | llm
    response = chain.invoke({"rating": rating, "review": review})
    return response.content.strip()

def generate_summary_and_actions(rating: int, review: str) -> tuple:
    """Generate AI summary and recommended actions for admin"""
    prompt = PromptTemplate(
        template="""Analyze this customer review and provide insights for the admin team.

Rating: {rating} stars
Review: {review}

Provide your analysis in this exact JSON format:
{{
    "summary": "One-sentence summary of the review",
    "recommended_actions": "Specific action items for the team (be concrete and actionable)"
}}

Response:""",
        input_variables=["rating", "review"]
    )
    
    chain = prompt | llm
    response = chain.invoke({"rating": rating, "review": review})
    
    try:
        # Parse JSON response
        content = response.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0]
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0]
        
        data = json.loads(content.strip())
        return data.get("summary", "Summary not available"), data.get("recommended_actions", "Actions not available")
    except:
        # Fallback if JSON parsing fails
        summary = f"{rating}-star review requiring attention"
        actions = "Review manually and respond appropriately"
        return summary, actions

def save_review(rating: int, review: str, ai_response: str, ai_summary: str, recommended_actions: str):
    """Save review to CSV file"""
    new_row = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'rating': rating,
        'review': review,
        'ai_response': ai_response,
        'ai_summary': ai_summary,
        'recommended_actions': recommended_actions
    }
    
    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# ============================================================================
# UI LAYOUT
# ============================================================================

# Header
st.title("⭐ Share Your Experience")
st.markdown("We value your feedback! Please take a moment to rate your experience.")

# Create form
with st.form("review_form"):
    st.markdown("### How would you rate your experience?")
    
    # Star rating selector
    rating = st.select_slider(
        "Rating",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: "⭐" * x,
        help="Select from 1 to 5 stars"
    )
    
    # Visual feedback for rating
    if rating == 5:
        st.success("😊 Excellent!")
    elif rating == 4:
        st.info("👍 Good!")
    elif rating == 3:
        st.warning("😐 Average")
    elif rating == 2:
        st.warning("😕 Below Average")
    else:
        st.error("😞 Poor")
    
    st.markdown("### Tell us more")
    review_text = st.text_area(
        "Your review",
        placeholder="Share your experience with us...",
        height=150,
        help="Please provide details about your experience"
    )
    
    # Submit button
    submitted = st.form_submit_button("Submit Review", use_container_width=True)

# Handle form submission
if submitted:
    if not review_text.strip():
        st.error("⚠️ Please write a review before submitting.")
    else:
        with st.spinner("🤖 Generating response..."):
            try:
                # Generate AI response for user
                ai_response = generate_ai_response(rating, review_text)
                
                # Generate summary and actions for admin
                ai_summary, recommended_actions = generate_summary_and_actions(rating, review_text)
                
                # Save to CSV
                save_review(rating, review_text, ai_response, ai_summary, recommended_actions)
                
                # Show success message
                st.success("✅ Thank you for your review!")
                
                # Display AI response
                st.markdown("---")
                st.markdown("### 💬 Our Response")
                st.info(ai_response)
                
                # Show confetti for 5-star reviews
                if rating == 5:
                    st.balloons()
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.error("Please try again or contact support.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>Your feedback helps us improve our service</small>
    </div>
    """,
    unsafe_allow_html=True
)

# Show recent submission count (optional)
try:
    df = pd.read_csv(DATA_FILE)
    total_reviews = len(df)
    if total_reviews > 0:
        st.sidebar.markdown(f"### 📊 Stats")
        st.sidebar.metric("Total Reviews", total_reviews)
        avg_rating = df['rating'].mean()
        st.sidebar.metric("Average Rating", f"{avg_rating:.1f} ⭐")
except:
    pass