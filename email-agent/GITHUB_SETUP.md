# GitHub Authentication for Git CLI

## 🔐 Problem
When you use Google to sign in to GitHub, you can't use a regular password with `git push`. You need a **Personal Access Token (PAT)**.

## ✅ Solution: Create a Personal Access Token

### Step 1: Create a Personal Access Token (2 minutes)

1. **Go to GitHub Settings**:
   - Visit: https://github.com/settings/tokens
   - Or: GitHub.com → Click your profile (top right) → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token**:
   - Click **"Generate new token"** → **"Generate new token (classic)"**
   - Give it a name: `Railway Deployment` or `A2A Project`
   - Set expiration: Choose **90 days** or **No expiration** (for convenience)

3. **Select Scopes** (permissions):
   - ✅ Check **`repo`** (Full control of private repositories)
   - This gives access to push code

4. **Generate and Copy**:
   - Click **"Generate token"** at the bottom
   - **IMPORTANT**: Copy the token immediately! (You won't see it again)
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Use Token with Git

When git asks for credentials:

```bash
Username: YOUR_GITHUB_USERNAME
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # ← Paste your token here
```

**Example**:
```bash
git push origin main

# Git will prompt:
Username for 'https://github.com': harishankar  # Your GitHub username
Password for 'https://harishankar@github.com': ghp_1234567890abcdef...  # Your token
```

### Step 3: Save Credentials (Optional but Recommended)

To avoid entering the token every time:

```bash
# Tell git to remember your credentials
git config --global credential.helper store

# Now push once with your token
git push origin main
# Enter username and token

# Git will save it - you won't need to enter it again!
```

## 🚀 Quick Setup for This Project

```bash
cd /Users/harishankar/Downloads/a2a

# Configure git (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Save credentials for convenience
git config --global credential.helper store

# Initialize repo (if not already done)
git init
git add .
git commit -m "Add email agent for Railway deployment"

# Add remote (replace YOUR-USERNAME and YOUR-REPO)
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git

# Push (will ask for username and token)
git push -u origin main
```

## 🔑 Finding Your GitHub Username

If you're not sure of your GitHub username:

1. Go to https://github.com
2. Click your profile picture (top right)
3. Your username is shown there (e.g., `@harishankar`)
4. Use the part after `@` (e.g., `harishankar`)

## 🆘 Alternative: Use SSH Instead

If you prefer SSH (no tokens needed):

### Setup SSH (One-time)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter for all prompts (use defaults)

# Copy public key
cat ~/.ssh/id_ed25519.pub
# Copy the output

# Add to GitHub:
# 1. Go to https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Paste the key
# 4. Click "Add SSH key"
```

### Use SSH URL

```bash
# Instead of HTTPS:
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git

# Use SSH:
git remote add origin git@github.com:YOUR-USERNAME/YOUR-REPO.git

# Now push works without password:
git push -u origin main
```

## 📝 Summary

**For HTTPS (easier for beginners)**:
1. Create Personal Access Token at https://github.com/settings/tokens
2. Use token as password when git asks
3. Run `git config --global credential.helper store` to save it

**For SSH (more secure, no passwords)**:
1. Generate SSH key: `ssh-keygen -t ed25519`
2. Add public key to GitHub settings
3. Use SSH URL: `git@github.com:username/repo.git`

## 🎯 Recommended for You

Since you're new to this, I recommend:
1. ✅ Use **HTTPS with Personal Access Token**
2. ✅ Save credentials with `git config --global credential.helper store`
3. ✅ This way you only enter the token once

---

**Next**: Once you've pushed to GitHub, continue with Railway deployment in [`DEPLOY_NOW.md`](DEPLOY_NOW.md)