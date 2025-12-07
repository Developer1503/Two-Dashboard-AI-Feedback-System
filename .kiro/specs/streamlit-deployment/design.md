# Design Document: Streamlit Cloud Deployment

## Overview

This design outlines the deployment strategy for the Two-Dashboard AI Feedback System to Streamlit Cloud. The application uses Streamlit for the UI, Groq's Llama 3 LLM for AI responses, and CSV-based data storage. The deployment will ensure secure handling of API keys, proper configuration for cloud hosting, and seamless user access.

## Architecture

### Current Application Structure
```
project/
├── Home.py                      # Main entry point
├── pages/
│   ├── 1_User_Dashboard.py     # Public review submission
│   └── 2_Admin_Dashboard.py    # Internal analytics dashboard
├── data/
│   └── reviews.csv             # Data storage (auto-created)
├── requirements.txt            # Python dependencies
└── .env                        # Local environment variables (not deployed)
```

### Deployment Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Cloud                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Application Container                                │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │   Home.py   │  │ User Dash    │  │ Admin Dash  │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────┘  │  │
│  │         │                │                  │         │  │
│  │         └────────────────┴──────────────────┘         │  │
│  │                          │                            │  │
│  │                    ┌─────▼──────┐                     │  │
│  │                    │ data/      │                     │  │
│  │                    │ reviews.csv│                     │  │
│  │                    └────────────┘                     │  │
│  │                          │                            │  │
│  │                    ┌─────▼──────┐                     │  │
│  │                    │ Secrets    │                     │  │
│  │                    │ (GROQ_KEY) │                     │  │
│  │                    └────────────┘                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│                  ┌──────────────┐                           │
│                  │  Public URL  │                           │
│                  └──────────────┘                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │  Groq API    │
                  │  (External)  │
                  └──────────────┘
```

## Components and Interfaces

### 1. Configuration Files

#### .streamlit/config.toml
Purpose: Configure Streamlit app behavior and appearance
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

#### .streamlit/secrets.toml.example
Purpose: Document required secrets (not committed to Git)
```toml
# Copy this file to secrets.toml for local development
# For Streamlit Cloud, add these in the dashboard

GROQ_API_KEY = "your_groq_api_key_here"
```

#### .gitignore additions
Purpose: Prevent sensitive files from being committed
```
.env
.streamlit/secrets.toml
data/*.csv
```

### 2. Environment Variable Handling

The application already has dual support for environment variables:
```python
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
```

This pattern works for both:
- Local development: Uses `.env` file via `python-dotenv`
- Streamlit Cloud: Uses `st.secrets` from dashboard configuration

### 3. Data Persistence Strategy

**Current Implementation:**
- CSV file storage in `data/reviews.csv`
- Auto-creates directory and file if missing
- Works for demo purposes

**Cloud Considerations:**
- Streamlit Cloud uses ephemeral storage (resets on app restart)
- Data persists during active sessions but may be lost on redeployment
- Acceptable for demo/prototype deployments

**Future Enhancement (Optional):**
- For production: Consider external database (PostgreSQL, MongoDB)
- For persistence: Use Streamlit Cloud's persistent storage or external service

### 4. Deployment Configuration

#### Python Version
- Minimum: Python 3.9
- Recommended: Python 3.11 (Streamlit Cloud default)

#### Dependencies
All dependencies are already specified in `requirements.txt`:
- streamlit==1.39.0
- langchain-groq==1.0.0
- langchain-core==1.0.4
- langchain-community==0.4.1
- pandas==2.2.0
- plotly==5.18.0
- python-dotenv==1.2.1

## Error Handling

### API Key Validation
The application already implements proper error handling:
```python
if not api_key:
    st.error("⚠️ GROQ_API_KEY not found. Please set it in .env or Streamlit secrets.")
    st.stop()
```

### File System Errors
Graceful handling of missing data:
```python
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    # Initialize empty DataFrame
```

### LLM Response Errors
Try-catch blocks for AI generation failures with user-friendly messages

## Testing Strategy

### Pre-Deployment Testing
1. **Local Testing with Streamlit Secrets**
   - Create `.streamlit/secrets.toml` locally
   - Test that `st.secrets` access works
   - Verify all pages load correctly

2. **Dependency Verification**
   - Test with fresh virtual environment
   - Ensure all imports resolve
   - Check version compatibility

### Post-Deployment Testing
1. **Smoke Tests**
   - Home page loads
   - User Dashboard accepts submissions
   - Admin Dashboard displays data
   - AI responses generate correctly

2. **Integration Tests**
   - Submit review from User Dashboard
   - Verify it appears in Admin Dashboard
   - Check AI response quality
   - Test data export functionality

3. **Error Scenarios**
   - Invalid/missing API key handling
   - Network timeout handling
   - Large review text handling

## Deployment Process

### Step 1: Prepare Repository
1. Create `.streamlit/config.toml` with app configuration
2. Create `.streamlit/secrets.toml.example` as documentation
3. Update `.gitignore` to exclude secrets
4. Commit and push to Git repository (GitHub/GitLab/Bitbucket)

### Step 2: Connect to Streamlit Cloud
1. Sign in to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select repository, branch, and main file (`Home.py`)
4. Configure advanced settings if needed

### Step 3: Configure Secrets
1. In Streamlit Cloud dashboard, open app settings
2. Navigate to "Secrets" section
3. Add secrets in TOML format:
   ```toml
   GROQ_API_KEY = "gsk_..."
   ```
4. Save secrets

### Step 4: Deploy
1. Streamlit Cloud auto-deploys on commit
2. Monitor deployment logs for errors
3. Wait for "Your app is live!" message

### Step 5: Verify
1. Access public URL
2. Test User Dashboard submission
3. Check Admin Dashboard displays data
4. Verify AI responses work

## Security Considerations

### API Key Protection
- Never commit `.env` or `secrets.toml` to Git
- Use Streamlit Cloud's encrypted secrets storage
- Rotate API keys if accidentally exposed

### Data Privacy
- CSV data is ephemeral on Streamlit Cloud
- No persistent storage of user reviews (resets on restart)
- Consider adding data retention notice for users

### Access Control
- Public URL is accessible to anyone
- Admin Dashboard has no authentication (by design for demo)
- For production: Add authentication layer

## Monitoring and Maintenance

### Streamlit Cloud Logs
- Access via dashboard "Manage app" → "Logs"
- Monitor for errors and exceptions
- Check resource usage

### App Health Checks
- Test public URL periodically
- Verify AI responses are generating
- Check data persistence behavior

### Updates and Redeployment
- Push changes to Git repository
- Streamlit Cloud auto-redeploys
- Monitor logs during redeployment
- Test functionality after updates

## Limitations and Considerations

### Ephemeral Storage
- Data resets on app restart/redeployment
- Acceptable for demo purposes
- Add warning message to users (already present in Home.py)

### Resource Limits
- Streamlit Cloud free tier has resource limits
- Monitor app performance
- Consider upgrading for production use

### Concurrent Users
- Streamlit handles multiple users
- CSV file access is not transaction-safe
- For high traffic: Use proper database

## Future Enhancements

### Database Integration
- Replace CSV with PostgreSQL/MongoDB
- Use Streamlit Cloud's database connections
- Implement proper data persistence

### Authentication
- Add user authentication for Admin Dashboard
- Use Streamlit's authentication components
- Integrate with OAuth providers

### Analytics
- Add Google Analytics or similar
- Track user engagement
- Monitor conversion rates

### Performance Optimization
- Implement caching strategies
- Optimize LLM calls
- Add loading states and progress indicators
