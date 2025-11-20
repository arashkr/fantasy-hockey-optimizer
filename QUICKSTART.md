# Quick Start Guide

## Running the Web App Locally

1. **Install dependencies** (if not already done):
   ```bash
   pip3 install streamlit pandas
   ```

2. **Run the app**:
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to the URL shown (typically `http://localhost:8501`)

4. **Upload your CSV file** using the file uploader on the page

## Deploying to Streamlit Cloud (Free)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Sign in with GitHub**

4. **Click "New app"**

5. **Configure:**
   - Repository: Select your repo
   - Branch: `main` (or your default branch)
   - Main file path: `app.py`

6. **Click "Deploy"**

Your app will be live in a few minutes!

## What the App Does

- Upload a Fantrax CSV export
- Automatically calculates optimal rosters for all teams
- Shows summary table with total FPts per team
- Allows you to view detailed roster breakdowns by team
- Export results as CSV

## File Structure

- `app.py` - Streamlit web application
- `fantasy_roster_optimizer.py` - Command-line tool (standalone)
- `requirements.txt` - Python dependencies
- `README.md` - Full documentation
- `DEPLOYMENT.md` - Detailed deployment options

