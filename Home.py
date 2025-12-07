import streamlit as st

st.set_page_config(
    page_title="Two-Dashboard AI System",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Feedback System")

st.markdown("""
### Welcome!

This application demonstrates a **Two-Dashboard System** powered by LLMs.

---

#### 👈 Select a Dashboard from the Sidebar

1. **User Dashboard**: 
   - Public-facing interface for customers.
   - Submit reviews and receive instant AI responses.
   
2. **Admin Dashboard**:
   - Internal interface for teams.
   - Monitor reviews in real-time.
   - View AI-generated summaries and action items.

---

### How it works
- **Data Sharing**: Both dashboards share a common data source (CSV).
- **AI Integration**: Uses Groq Llama 3 to analyze text and generate responses.
- **Real-time**: Updates in the User Dashboard appear instantly in the Admin Dashboard.
""")

st.info("💡 Note: On this demo deployment, data may reset if the app restarts.")
