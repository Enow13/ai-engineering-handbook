# Git – Complete Developer Study Notes 🌿💻

> Every lab, notebook, pipeline and agent you build lives in Git. Recruiters look at your GitHub, and MLOps runs on it.

[⬅ Previous: MLOps on AWS](17-mlops-on-aws.md) | [🏠 Home](../README.md)

## 📚 What's covered

✅ [Version control fundamentals](#1-version-control-fundamentals)
✅ [Installation & setup](#2-installation--setup)
✅ [The three areas & basic commands](#3-the-three-areas--basic-commands)
✅ [Branching](#4-branching)
✅ [Merging & merge conflicts](#5-merging--merge-conflicts)
✅ [Remotes: GitHub, push, pull, fetch](#6-remotes)
✅ [Team collaboration: forks, pull requests, code review](#7-team-collaboration)
✅ [Stashing & cleaning](#8-stashing--cleaning)
✅ [Undoing changes: restore, reset, revert, amend](#9-undoing-changes)
✅ [Tags & releases](#10-tags--releases)
✅ [.gitignore & repository hygiene (incl. secrets & ML files)](#11-gitignore--repository-hygiene)
✅ [History: log, diff, show, blame](#12-history)
✅ [Rebasing](#13-rebasing)
✅ [Branching strategies & Git for MLOps](#14-branching-strategies--git-for-mlops)
✅ [Fixing common errors](#15-fixing-common-errors)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** every developer, data scientist, ML/DevOps engineer, and student.

---

## 1. Version control fundamentals

**Git** is a **distributed** version control system: every clone has the full history. It tracks changes as **commits** (snapshots), lets many people work in parallel on **branches**, and merges their work.

| Term | Meaning |
|---|---|
| **Repository (repo)** | A project folder tracked by Git (the `.git` folder holds the history) |
| **Commit** | A snapshot with a unique hash (SHA), author, message and parent |
| **Branch** | A movable pointer to a commit; a line of development |
| **HEAD** | Where you are now (usually the tip of the current branch) |
| **Remote** | A copy on a server (GitHub, GitLab, Azure Repos), usually called `origin` |

## 2. Installation & setup

- **Windows:** https://git-scm.com → install (includes **Git Bash**). **macOS:** `xcode-select --install` or `brew install git`. **Linux:** `sudo apt install git`.

```bash
git --version
git config --global user.name "Your Name"
git config --global user.email "you@example.com"     # use the email on your GitHub account
git config --global init.defaultBranch main
git config --global core.autocrlf true                # Windows (use "input" on macOS/Linux)
git config --list
```

## 3. The three areas & basic commands

```
 Working directory ──git add──► Staging area (index) ──git commit──► Repository (.git)
        ▲                                                                   │
        └────────────────────── git restore / git checkout ─────────────────┘
```

| Command | Does |
|---|---|
| `git init` | Start a new repo in the current folder |
| `git clone <url>` | Copy a remote repo locally |
| `git status` | What's changed, staged or untracked |
| `git add <file>` / `git add .` | Stage changes |
| `git commit -m "message"` | Save a snapshot |
| `git log --oneline --graph` | View history |
| `git diff` / `git diff --staged` | Unstaged / staged changes |

**Good commit messages:** imperative and specific, e.g. `Add sweep job for reg_rate tuning`, not `update`.

## 4. Branching

```bash
git branch                       # list branches
git switch -c feature/rag-eval   # create and switch (older: git checkout -b)
git switch main                  # switch
git branch -m old-name new-name  # rename
git branch -d feature/rag-eval   # delete (merged); -D to force
```

## 5. Merging & merge conflicts

```bash
git switch main
git merge feature/rag-eval
```

| Merge type | When |
|---|---|
| **Fast-forward** | main hasn't moved; Git just moves the pointer |
| **Three-way merge** | Both branches changed; Git creates a merge commit |
| **Squash merge** | All branch commits combined into one (common for PRs) |

**Resolving a conflict:**
```
<<<<<<< HEAD
chunk_size = 500
=======
chunk_size = 800
>>>>>>> feature/rag-eval
```
1. Edit the file: keep the right content and delete the markers.
2. `git add <file>`
3. `git commit` (or `git merge --continue`). To give up: `git merge --abort`.

## 6. Remotes

```bash
git remote -v                                   # list remotes
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main                         # first push; sets upstream
git push                                        # later pushes
git fetch                                       # download changes, don't merge
git pull                                        # fetch + merge (or --rebase)
git remote set-url origin <new-url>             # change the remote URL
```

## 7. Team collaboration

| Concept | Flow |
|---|---|
| **Pull request (PR)** | Push a branch → open a PR on GitHub → review → CI checks → merge |
| **Fork** | Your own copy of someone else's repo; PR back to the original ("upstream") |
| **Code review** | Comment, request changes, approve; protect `main` with **branch protection rules** (required reviews and checks) |

```bash
# Keep a fork up to date
git remote add upstream https://github.com/<original-owner>/<repo>.git
git fetch upstream
git switch main && git merge upstream/main && git push
```

## 8. Stashing & cleaning

```bash
git stash                 # shelve uncommitted changes
git stash list
git stash pop             # re-apply and remove from the stash
git clean -n              # preview deleting untracked files
git clean -fd             # delete untracked files and folders (careful!)
```

## 9. Undoing changes

| Situation | Command |
|---|---|
| Discard unstaged changes in a file | `git restore <file>` |
| Unstage a file | `git restore --staged <file>` |
| Fix the last commit's message or add a forgotten file (not pushed yet) | `git commit --amend` |
| Undo the last commit, keep the changes | `git reset --soft HEAD~1` |
| Undo the last commit and the changes (**dangerous**) | `git reset --hard HEAD~1` |
| Undo a **pushed** commit safely | `git revert <sha>` (makes a new commit that reverses it) |
| Recover "lost" commits | `git reflog` → `git reset --hard <sha>` |

💡 **Rule:** never rewrite history (`reset`, `rebase`, `--amend`, `push --force`) on branches others use. Use `revert` instead.

## 10. Tags & releases

```bash
git tag v1.0.0                                   # lightweight tag
git tag -a v1.1.0 -m "Model v1.1: AUC 0.86"      # annotated tag (recommended)
git push origin --tags
```
Use **semantic versioning** (MAJOR.MINOR.PATCH) and GitHub **Releases** for release notes. In MLOps, tag the code version that trained a production model.

## 11. .gitignore & repository hygiene

```gitignore
# Python
__pycache__/
*.pyc
.venv/
.ipynb_checkpoints/
# Secrets - NEVER commit
.env
*.pem
config.json
# ML artifacts & data (store in cloud storage / DVC / registries instead)
mlruns/
outputs/
*.pkl
*.joblib
data/raw/
```

- ❌ **Never commit secrets** (API keys, passwords, connection strings). If you do: **rotate the key immediately**, then remove it from history (`git filter-repo` or BFG). Turn on **GitHub secret scanning and push protection**.
- Large files: use **Git LFS**; datasets: **DVC** or cloud storage.
- Keep a `README.md`, `requirements.txt` and `LICENSE` in every repo.

## 12. History

```bash
git log --oneline --graph --all        # visual history
git log -p <file>                      # changes to a file over time
git show <sha>                         # one commit in detail
git diff main..feature/x               # compare branches
git blame <file>                       # who changed each line, and when
```

## 13. Rebasing

**Rebase** replays your branch's commits on top of another branch, giving a straight, linear history.

```bash
git switch feature/rag-eval
git rebase main                        # resolve conflicts, then: git add . && git rebase --continue
git rebase -i HEAD~3                   # interactive: squash, reword, reorder the last 3 commits
```

| Merge | Rebase |
|---|---|
| Preserves exact history, adds merge commits | Linear history, rewrites commits |
| Safe on shared branches | Only on **your own, unpushed** (or private) branches |

## 14. Branching strategies & Git for MLOps

| Strategy | Description |
|---|---|
| **GitHub Flow** | `main` is always deployable; short-lived feature branches + PRs. Simple, popular |
| **Trunk-based** | Very short branches, frequent merges to main, feature flags. High-velocity teams |
| **GitFlow** | `main`, `develop`, `feature/*`, `release/*`, `hotfix/*`. Scheduled releases |

**Git in MLOps:**
- Everything as code: training scripts, pipeline YAML, IaC, prompts, evaluation sets.
- PR → **CI** (tests, lint, validate pipelines) → merge → **CD** (train in dev, deploy after approval).
- Tag releases and record the Git commit SHA with each training run (Azure ML and SageMaker capture it automatically when you submit from a repo).

## 15. Fixing common errors

| Error | Fix |
|---|---|
| `fatal: not a git repository` | `cd` into the repo folder (or `git init`) |
| `rejected ... (fetch first)` / non-fast-forward | `git pull --rebase` then `git push` (or `--force` only if you intend to overwrite, on your own repo) |
| `src refspec main does not match any` | No commits yet, or the branch is called `master`: `git branch -M main` |
| `Authentication failed` | Use the Git Credential Manager sign-in, or a personal access token instead of a password |
| `detected dubious ownership` | `git config --global --add safe.directory "<path>"` |
| `Your local changes would be overwritten` | `git stash`, then pull, then `git stash pop` |
| Committed to the wrong branch | `git switch -c correct-branch` (keeps the commit), then reset the old branch |
| `LF will be replaced by CRLF` warning | Harmless; set `core.autocrlf` and a `.gitattributes` file |

---

## 💬 Interview questions & answers

**Q1. Git vs GitHub?**
Git is the version control tool. GitHub is a hosting platform for Git repos, adding pull requests, issues, Actions (CI/CD) and security features.

**Q2. `git fetch` vs `git pull`?**
Fetch downloads remote changes without changing your branch. Pull = fetch + merge (or rebase) into your current branch.

**Q3. Merge vs rebase?**
Merge keeps history as it happened and adds a merge commit. Rebase rewrites your commits onto the new base for a linear history. Rebase only private branches.

**Q4. `reset` vs `revert`?**
Reset moves the branch pointer back (rewrites history: for local, unpushed work). Revert creates a new commit that undoes a previous one (safe for shared branches).

**Q5. How do you resolve a merge conflict?**
Open the conflicted files, choose or combine the changes between the markers, remove the markers, `git add`, then commit or continue the merge or rebase. Run tests before pushing.

**Q6. You committed an API key. What do you do?**
Rotate/revoke the key immediately (assume it's compromised), remove it from the code and history (git filter-repo/BFG), force-push the cleaned history with the team's agreement, and enable secret scanning and push protection.

**Q7. How does Git support MLOps?**
It versions code, configs, pipelines, IaC and prompts; PRs trigger CI tests; merges trigger training and deployment pipelines; tags and commit SHAs give each model full lineage.

---

## ✅ Final revision checklist

- [ ] I can explain working directory, staging area and repository.
- [ ] I can create, switch, merge and delete branches.
- [ ] I can resolve a merge conflict.
- [ ] I can push to and pull from GitHub, and work with a fork.
- [ ] I know when to use restore, reset, revert and amend.
- [ ] I can write a .gitignore that excludes secrets and ML artifacts.
- [ ] I can explain merge vs rebase and the main branching strategies.
- [ ] I can fix the common push/pull errors.

## 🔗 Official docs
- Pro Git book (free): https://git-scm.com/book
- GitHub Docs: https://docs.github.com
- GitHub Skills (interactive): https://skills.github.com

---
*My AI Engineering Study Notes* | [⬅ Previous](17-mlops-on-aws.md) | [🏠 Home](../README.md)
