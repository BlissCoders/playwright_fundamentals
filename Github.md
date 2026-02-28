# Git & PyCharm Integration Guide

This guide provides a step-by-step workflow for integrating GitHub with PyCharm, covering everything from account creation to terminal commands.

---

## 🚀 1. GitHub Account & Local Setup

### Create a GitHub Account
1. Go to [GitHub.com](https://github.com) and click **Sign up**.
2. Follow the prompts to verify your email and secure your account.

### Set Global Git Configurations
Open the **Terminal** tab in PyCharm and run these commands to link your local actions to your identity:

```bash
# Set your global identity
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# Verify your configuration
git config --list
```
---

## 🛠 2. PyCharm Integration
### Connect GitHub Account

1. Open Settings (Ctrl+Alt+S on Windows or Cmd+, on macOS).
2. Navigate to Version Control > GitHub.
3. Click the + (Add) icon and select Log In via GitHub... to authorize JetBrains.

### Set Global Git Configuration 
Before your first commit, you must identify yourself so Git can attribute your work. Open the Terminal tab at the bottom of PyCharm and run: 
* **Set Name:** git config --global user.name "Your Name"
* **Set Email:** git config --global user.email "your-email@example.com"
* **Verify:** git config --list to confirm your settings are saved.

## 💻 3. Essential Git Commands
### Clone a Repository
To bring a remote project to your local machine:
* **Command:** git clone <repository-url>
* **Example:** git clone https://github.com
* **Specific Folder:** To clone into a folder with a different name, use git clone <url> <folder-name>.

```bash
git clone https://github.com/BlissCoders/playwright_fundamentals.git
```

### Pulling Updates
To sync your local repository with the latest changes from GitHub:
* **Command:** git pull origin <branch-name> (usually master).
* This command fetches the latest data and automatically merges it into your current local branch. 

```bash
git pull origin master
```

### Committing & Pushing
Committing saves a snapshot of your progress locally.
1. **Stage Files:** Use git add . to prepare all changed files for the commit.
2. **Commit:** Use git commit -m "Your descriptive message" to save the snapshot.
3. **Shortcut:** Use git commit -am "message" to stage and commit tracked files in one step.

2. Commit with a message
```bash
git commit -m "Explain what you changed"
```

3. Push to GitHub
```bash
git push origin develop
```

## 🔃 4. Pull Requests (PRs)
Standard Git does not have a "pull request" command because PRs are a platform-specific feature (GitHub, GitLab, etc.). 
* **Push First:** You must push your branch to GitHub before creating a PR:
```bash
git push origin <your-branch-name>
```
* **Option A (CLI):** Install the GitHub CLI (gh) and run gh pr create to initiate the PR directly from the terminal.
* **Option B (Web):** After pushing, GitHub will often provide a direct URL in the terminal output. Copy and paste that link into your browser to complete the PR.
* **Option C (PyCharm):** Use the built-in UI via Git > GitHub > Create Pull Request for a more visual experience.
* **Web Browser:** After pushing a new branch, visit your [GitHub Dashboard](https://github.com/) and click the Compare & pull request button.

