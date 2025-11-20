#!/bin/bash
# Quick deployment script for Fantasy Hockey Roster Optimizer

echo "🏒 Fantasy Hockey Roster Optimizer - Deployment Helper"
echo "======================================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
    echo ""
fi

# Check if remote is set
if ! git remote | grep -q origin; then
    echo "⚠️  No GitHub remote configured yet."
    echo ""
    echo "Please create a GitHub repository first:"
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository (make it PUBLIC)"
    echo "3. Copy the repository URL"
    echo ""
    read -p "Enter your GitHub repository URL (or press Enter to skip): " repo_url
    
    if [ ! -z "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "✅ Remote added: $repo_url"
    else
        echo "⚠️  Skipping remote setup. You can add it later with:"
        echo "   git remote add origin YOUR_REPO_URL"
        exit 1
    fi
    echo ""
fi

# Add all files
echo "📝 Adding files..."
git add .
echo "✅ Files added"
echo ""

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    read -p "Enter commit message (or press Enter for default): " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Update Fantasy Hockey Roster Optimizer"
    fi
    
    echo "💾 Committing changes..."
    git commit -m "$commit_msg"
    echo "✅ Committed"
    echo ""
fi

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git branch -M main 2>/dev/null
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to https://share.streamlit.io"
    echo "2. Sign in with GitHub"
    echo "3. Click 'New app'"
    echo "4. Select your repository"
    echo "5. Set main file to: app.py"
    echo "6. Click 'Deploy'"
    echo ""
else
    echo ""
    echo "❌ Push failed. You may need to:"
    echo "   - Set up GitHub authentication"
    echo "   - Check your repository URL"
    echo "   - Make sure the repository exists and is accessible"
fi

