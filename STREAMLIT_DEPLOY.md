# Deploy to Streamlit Cloud - Step by Step

## ✅ Step 1: Verify Your Code is on GitHub
Your code should now be at: https://github.com/arashkr/fantasy-hockey-optimizer

## 🚀 Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Open: https://share.streamlit.io
   - Click **"Sign in"** (top right)
   - Sign in with your **GitHub account**

2. **Create New App:**
   - Click **"New app"** button
   - You'll see a form with these fields:

3. **Fill in the Form:**
   - **Repository:** Select `arashkr/fantasy-hockey-optimizer` from the dropdown
   - **Branch:** Select `main`
   - **Main file path:** Type `app.py`
   - **App URL (optional):** Leave blank or choose a custom name like `fantasy-hockey-optimizer`

4. **Deploy:**
   - Click the **"Deploy"** button
   - Wait 1-2 minutes for deployment

5. **Your App is Live!**
   - Once deployed, you'll see a URL like:
     `https://fantasy-hockey-optimizer.streamlit.app`
   - Click the URL to open your app
   - You can share this URL with anyone!

## 📝 What Happens Next

- Streamlit Cloud automatically installs dependencies from `requirements.txt`
- Your app will be live and accessible to anyone with the URL
- You can upload CSV files through the web interface
- When you update code and push to GitHub, Streamlit Cloud automatically redeploys

## 🔄 Updating Your App

To update your app in the future:
1. Make changes to your code
2. Run: `git add .`, `git commit -m "Update"`, `git push`
3. Streamlit Cloud automatically redeploys (usually takes 1-2 minutes)

