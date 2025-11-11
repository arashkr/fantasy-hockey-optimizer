# Deployment Guide

This guide covers multiple ways to deploy the Fantasy Hockey Roster Optimizer web app.

## Option 1: Streamlit Cloud (Recommended - Easiest)

Streamlit Cloud offers free hosting with automatic deployments from GitHub.

### Steps:

1. **Create a GitHub repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository and branch
   - Set the main file path to `app.py`
   - Click "Deploy"

3. **Your app will be live at:** `https://your-app-name.streamlit.app`

## Option 2: Local Development

### Installation:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Option 3: Docker Deployment

### Create Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and run:

```bash
docker build -t fantasy-roster-optimizer .
docker run -p 8501:8501 fantasy-roster-optimizer
```

## Option 4: Heroku

1. **Create Procfile:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy:**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## Option 5: AWS/Azure/GCP

For cloud platforms, you can:
- Use container services (ECS, Azure Container Instances, Cloud Run)
- Use serverless functions (Lambda, Azure Functions, Cloud Functions)
- Use virtual machines with Docker

## Environment Variables

No environment variables are required for basic functionality.

## Performance Notes

- The backtracking algorithm is optimized but may take a few seconds for large leagues
- Streamlit Cloud free tier has resource limits
- For production, consider caching results for the same CSV file

## Troubleshooting

- **Import errors:** Ensure all dependencies are in `requirements.txt`
- **File upload issues:** Check file size limits (Streamlit Cloud: 200MB)
- **Slow performance:** The algorithm is computationally intensive for large datasets

