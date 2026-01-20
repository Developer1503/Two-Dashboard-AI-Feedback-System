# Streamlit Cloud Deployment Guide

## Quick Fix for Module Errors

If you're getting module errors on Streamlit Cloud but it works locally, follow these steps:

### 1. Verify Files Are Committed

Make sure these files are in your Git repository:
```bash
git add .python-version
git add .streamlit/config.toml
git add requirements.txt
git commit -m "Fix Streamlit Cloud deployment"
git push
```

### 2. Configure Secrets in Streamlit Cloud

1. Go to your app on [share.streamlit.io](https://share.streamlit.io)
2. Click the three dots menu (⋮) → **Settings**
3. Go to the **Secrets** section
4. Add your secrets in TOML format:

```toml
GROQ_API_KEY = "your_api_key_here"
```

5. Click **Save**

### 3. Reboot the App

After adding secrets:
1. Go back to your app settings
2. Click **Reboot app** button
3. Wait for the app to restart (usually 1-2 minutes)

### 4. Check Logs

If still getting errors:
1. Click **Manage app** from the three dots menu
2. View the **Logs** tab
3. Look for specific error messages

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'langchain_groq'"

**Solution:** The requirements.txt now uses flexible version constraints (`>=` instead of `==`). Make sure you've pushed the updated requirements.txt.

### Issue: "GROQ_API_KEY not found"

**Solution:** Add the API key in Streamlit Cloud Secrets (see step 2 above).

### Issue: "App keeps restarting"

**Solution:** Check the logs for errors. Usually caused by missing dependencies or incorrect secrets format.

### Issue: Data not persisting

**Expected behavior:** Streamlit Cloud uses ephemeral storage. Data in `data/reviews.csv` will reset when the app restarts. This is normal for the free tier.

## Files Required for Deployment

✅ `Home.py` - Main app file  
✅ `pages/1_User_Dashboard.py` - User dashboard  
✅ `pages/2_Admin_Dashboard.py` - Admin dashboard  
✅ `requirements.txt` - Python dependencies  
✅ `.python-version` - Python version (3.11)  
✅ `.streamlit/config.toml` - Streamlit configuration  
✅ `.env` - Local only (NOT pushed to Git)  

## Testing Locally Before Deploy

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run Home.py
```

## Support

If you continue to have issues:
1. Check Streamlit Community Forum: https://discuss.streamlit.io/
2. Review Streamlit Cloud docs: https://docs.streamlit.io/streamlit-community-cloud
