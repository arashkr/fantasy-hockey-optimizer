# Step-by-Step Deployment Guide

## Option 1: Streamlit Cloud (Recommended - Free & Easy)

### Step 1: Create a GitHub Repository

1. Go to [github.com](https://github.com) and sign in (or create an account)
2. Click the **"+"** icon in the top right → **"New repository"**
3. Name it (e.g., `fantasy-hockey-optimizer`)
4. Choose **Public** (free Streamlit Cloud requires public repos)
5. **Don't** initialize with README, .gitignore, or license (we already have files)
6. Click **"Create repository"**

### Step 2: Push Your Code to GitHub

Open Terminal and run these commands:

```bash
cd /Users/arashkr/bpr

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Fantasy Hockey Roster Optimizer"

# Add your GitHub repository (replace YOUR_USERNAME and YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** You'll need to authenticate with GitHub. If prompted, use a Personal Access Token instead of password.

### Step 3: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in"** → Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository:** Select your repository from the dropdown
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Deploy"**
6. Wait 1-2 minutes for deployment
7. Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

### Step 4: Share Your App

Once deployed, you can:
- Share the URL with anyone
- Upload new CSV files anytime
- The app automatically updates when you push code changes

---

## Option 2: Run Locally (For Testing)

If you just want to test it on your computer:

```bash
cd /Users/arashkr/bpr
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## Troubleshooting

### "Repository not found" error
- Make sure the repository is **Public**
- Check that you've pushed all files to GitHub

### "Module not found" error
- Make sure `requirements.txt` is in your repository
- Streamlit Cloud will automatically install dependencies

### Need to update the app
- Make changes to your code
- Run: `git add .`, `git commit -m "Update"`, `git push`
- Streamlit Cloud will automatically redeploy

---

## What Files Need to Be in GitHub?

Make sure these files are in your repository:
- ✅ `app.py` (the web app)
- ✅ `requirements.txt` (dependencies)
- ✅ `README.md` (optional, but recommended)

You can check what will be uploaded:
```bash
git status
```

