---
title: "Git Things That Are Easy to Mess Up (Until They Bite You)"
date: 2026-07-14T08:00:00.000Z
categories:
  - System administration
  - Version control
tags:
  - git
  - version control
  - devops
  - sysadmin
  - common mistakes
  - troubleshooting
description: "A practical list of Git habits and gotchas that bite you the 10th, 50th, or 1000th time. From 'git commit -A' footguns to force-pushing to main, to that stash you forgot about."
keywords:
  - git gotchas
  - git mistakes
  - git force push
  - git revert vs reset
  - git detached HEAD
  - git stash
  - git workflow
author: "Pragmatic Sysadmin"
ShowShareButtons: true
ShowReadingTime: true
aliases:
  - /posts/2026-07-14-git-things-easy-to-mess-up/

---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Git Things That Are Easy to Mess Up (Until They Bite You)",
  "description": "A practical list of Git habits and gotchas that bite you the 10th, 50th, or 1000th time. From 'git commit -A' footguns to force-pushing to main, to that stash you forgot about.",
  "author": {"@type": "Person", "name": "Pragmatic Sysadmin"},
  "publisher": {"@type": "Organization", "name": "Pragmatic Tech"},
  "datePublished": "2026-07-14",
  "dateModified": "2026-07-14",
  "mainEntityOfPage": {"@type": "WebPage", "id": "https://pragmaticsysadmin.help/sysadmin/2026-07-14-git-things-easy-to-mess-up/"},
  "image": {"@type": "ImageObject", "url": "https://pragmaticsysadmin.help/og/2026-07-14-git-things-easy-to-mess-up.png", "width": 1200, "height": 630}
}
</script>

# Git Things That Are Easy to Mess Up (Until They Bite You)

Following up on last week's [Linux Things That Are Easy to Miss](/sysadmin/2026-07-13-linux-things-easy-to-miss/) — same idea, different tool. Git is the second thing every sysadmin and dev uses daily, and like the Linux shell, it's full of footguns that don't bite until they really bite.

This is the post I wish I'd had at year two of using Git, when I realized I'd been doing several things the hard way.

If you've been using Git for more than a year, you'll recognize most of these. If you're newer, **bookmark this**.

---

## 1. The `git add .` / `git commit -A` shortcut

The classic mistake. You're in a hurry, you run:

```bash
git add .
git commit -m "fix"
```

Five minutes later you realize you committed your `.env` file with the database password. Or that test output file. Or the binary someone dropped in `tmp/`.

**Why it's bad:** `git add .` adds everything modified, including files you don't want tracked (secrets, build artifacts, local config). `-A` is even worse — it catches deletions and modifications across the entire repo.

**Better pattern:**
```bash
# Review what's about to be committed
git status
git diff
# Stage specific files
git add src/auth/login.ts
git add tests/auth.test.ts
# Then commit
git commit -m "fix: handle expired token in login flow"
```

**Defence in depth:** put this in your project's `.gitignore` from day one:
```
.env
.env.local
*.log
node_modules/
dist/
build/
.DS_Store
```

And consider using [`gitleaks`](https://github.com/gitleaks/gitleaks) as a pre-commit hook to catch secrets before they're committed. Once they're in, they're in for a long time.

---

## 2. Force-pushing to `main`

The single most common way to ruin your team's day:

```bash
git push --force origin main
# Or, worse, "force-with-lease" used incorrectly
```

This rewrites remote history. If anyone else has pulled the old version, their next pull either silently throws away their work, or they get a confusing "diverged" state.

**Why it's bad:** Git's distributed model means remote history is shared. Rewriting it breaks everyone.

**Better pattern:**
```bash
# On a feature branch, force-push is fine
git checkout feature/my-thing
git commit --amend
git push --force-with-lease origin feature/my-thing
# --force-with-lease is safer than --force: it checks remote hasn't moved

# NEVER force-push to main, master, develop, or any shared branch
```

**How to prevent:** most Git hosting platforms (GitHub, GitLab) let you set branch protection rules:
- Require pull request reviews before merging to `main`
- Block force-pushes to protected branches
- Require status checks to pass

If your team isn't using these, you have a culture problem more than a Git problem.

---

## 3. `.gitignore` after the fact

You add `.env` to `.gitignore`. Push. Realize the file is still in the repo, because `.gitignore` only ignores **untracked** files. Once a file is tracked, it stays tracked until you `git rm --cached` it.

```bash
# Stop tracking a file (but keep it locally)
git rm --cached .env
git commit -m "stop tracking .env"

# For directories
git rm --cached -r node_modules/
git commit -m "stop tracking node_modules/"
```

**The bad news:** the file is still in your Git history. Even after you remove it from HEAD, anyone can `git log --all --full-history -- .env` and find the old version with the password.

**The real fix:** treat secrets like they're radioactive. Use a secret manager (Vault, AWS Secrets Manager, GitHub Secrets, etc.) and rotate any secret that's ever been in a repo. There are tools to find them — `gitleaks --log-opts="--all"` scans the entire history.

---

## 4. Detached HEAD surprise

```bash
git checkout 1a2b3c4   # check out a specific commit
# Do some work, commit it...
git checkout main
# Your work is now "lost" — it's in a dangling commit, not on any branch
```

This is one of Git's "WTF" moments. The commits are still in the reflog (`git reflog`) for 90 days by default, but you have to know to look there.

**Defence:** create a branch before you commit on a detached HEAD:

```bash
# Instead of git checkout <hash>, then doing work:
git checkout -b investigate-old-version 1a2b3c4
# Now commits land on a real branch
```

**Recovery** if you already lost work:
```bash
# Find the dangling commit
git reflog
# Look for "checkout: moving from <hash> to <hash>" entries
# Then create a branch pointing to your work
git branch recovered-work <commit-hash>
```

`git reflog` is your safety net. Check it whenever something weird happens.

---

## 5. `git reset` vs `git revert` vs `git checkout`

Three commands that all look like "undo" but do very different things:

```bash
# reset: moves HEAD and your branch to a different commit
# DEFAULT MODE: --mixed (keeps changes as uncommitted)
git reset HEAD~1
# Result: branch is one commit earlier, your changes are uncommitted

# reset --hard: throws away changes entirely
git reset --hard HEAD~1
# DANGEROUS. Your work is GONE (recoverable via reflog for 90 days)

# revert: creates a NEW commit that undoes an old one
git revert HEAD
# Result: a new commit "Revert: ..." that undoes the last commit
# SAFE: doesn't rewrite history

# checkout: moves HEAD to a different commit/branch, doesn't move branch
git checkout HEAD~1
# Result: HEAD is now at the older commit, branch is unchanged
# This is the detached HEAD state from #4
```

**Rule of thumb:**
- Already pushed to shared branch? Use `revert`.
- Haven't pushed yet, want to undo last commit but keep changes? `git reset HEAD~1`.
- Haven't pushed yet, want to throw away last commit entirely? `git reset --hard HEAD~1` (careful!).
- Want to look at an older commit but stay on your branch? `git show <hash>` (read-only, doesn't change anything).

---

## 6. The "I deleted the wrong branch" panic

```bash
git branch -D feature/oops-not-this-one
# Wait, that was the branch with the work I needed
```

**Recovery** (within 30 days usually):
```bash
# Find the dangling commit
git reflog --all
# Look for the last commit on the deleted branch
# Look for "checkout: moving from feature/oops-not-this-one to..."
# Then:
git branch feature/recovered <commit-hash>
```

The commit isn't gone until Git's garbage collection runs (usually 30 days, configurable with `gc.reflogExpireUnreachable` and `gc.reflogExpire`).

**Prevention:** when you delete a branch, double-check with `git branch -d` (lowercase, refuses to delete unmerged) instead of `-D` (force). And use `git push origin --delete <branch>` so the remote is also cleaned up.

---

## 7. Conflicts on files you didn't touch

You run `git pull` and suddenly there are conflicts on `package-lock.json` or `Cargo.lock` or that big generated `schema.graphql`. You didn't even edit it.

**Why:** these are files that get modified by tooling, not by humans. Two people ran `npm install` and got slightly different lockfile changes. Or two people ran the same code generator and got different timestamps.

**Fix:**
```bash
# For lockfiles (always regenerate from package.json)
git checkout --theirs package-lock.json
rm package-lock.json
npm install  # regenerate
git add package-lock.json

# For generated files (regenerate)
rm schema.graphql
# run the generator
git add schema.graphql
```

**Prevention:** add generated files to `.gitignore` where possible, and add the generators themselves with their own lock. Or use tools like [turborepo](https://turborepo.org/) that handle this automatically.

---

## 8. Submodules: the rabbit hole

```bash
git submodule add https://github.com/some/lib
# Now your "simple" clone is broken
git clone <repo>           # doesn't pull submodules
cd repo
# Stuff is empty
git submodule init
git submodule update
# And they're on whatever commit the parent pinned, not main
```

Submodules add three failure modes:
1. People forget to clone with `--recursive` or run `submodule update --init`
2. The pinned commit gets stale, so you have outdated code that compiles
3. Branch tracking in submodules is fundamentally different — they're on detached HEADs by default

**Modern alternative:** use **Git submodules** only if you must, but consider [git subtree](https://www.atlassian.com/git/tutorials/git-subtree) or [monorepo tools](https://monorepo.tools/) instead. They have less footgun potential.

If you must use submodules, add this to your README:
```bash
git clone --recursive https://github.com/you/repo
# or, after clone:
git submodule update --init --recursive
```

---

## 9. Shallow clone that bites you

```bash
git clone --depth 1 https://github.com/some/repo
# Now: faster, smaller
# But: git log only shows the latest commit
# And: git blame doesn't work for older lines
# And: git describe can't find old tags
```

Shallow clones save time and disk space but break several normal workflows. CI runners often use `--depth 1` for speed, which then breaks any tooling that needs full history.

**When to use shallow:**
- CI build steps that just need the code
- Initial clone on a machine that just needs the latest
- Anything that won't ever need history

**When NOT to use shallow:**
- Day-to-day development
- Anything that needs to bisect (`git bisect` doesn't work in shallow clones)
- Anything that runs `git describe` for version info

If you must work in a shallow clone and need history:
```bash
git fetch --unshallow
# Now you have the full history
```

---

## 10. The "this commit has sensitive data" problem

```bash
# Oh no, I committed the AWS access key
git log --all --full-history -- "*.env"
# Found it
# Now what?
```

`git filter-branch` and `git filter-repo` can rewrite history to remove the file. But every clone of the repo has the bad commit. **Once a secret is in Git, it's effectively public** — GitHub scans for known credential formats and revokes them, but that's a safety net, not a fix.

**The right order:**
1. **Rotate the secret immediately** (don't try to clean it up first)
2. **Then** rewrite history if you want a clean log
3. **Audit** the secret's usage in the time it was exposed
4. **Set up detection** so it doesn't happen again

**Tools:**
- `git filter-repo` (the modern replacement for `git filter-branch`)
- `bfg-repo-cleaner` (faster for "remove this file from all history")
- GitHub/GitLab's own secret scanning (rotates known leaked keys automatically)

**Don't** use `git filter-branch` — it's slow, dangerous, and deprecated.

---

## 11. Rebase vs merge for shared branches

You and your teammate are both on `feature/foo`. You `git rebase main` to clean up your commits, they `git merge main` to update theirs. Now you can't merge without conflicts or force-push.

**Two philosophies, both valid:**

**Always rebase (clean history, but conflicts at push time):**
```bash
git pull --rebase origin main
# Rewrites your local commits to be on top of latest main
git push --force-with-lease origin feature/foo
```

**Always merge (true history, but messy log):**
```bash
git pull origin main
git merge main
# Creates a merge commit, no rewriting
git push origin feature/foo
```

**What most teams do (the "no surprises" rule):**
- **Feature branch?** Use rebase freely. It's YOUR work.
- **Shared branch (main, develop, release)?** Always merge. Never rebase.
- **Pushing to remote?** `--force-with-lease` is safe, plain `--force` is dangerous.

Pick one and write it down in your `CONTRIBUTING.md`. Saves arguments later.

---

## 12. The stash you forgot about

```bash
# You're in the middle of work
# "Oh, gotta switch branches real quick"
git stash
git checkout other-branch
# ... do work ...
# Come back
git stash pop
# CONFLICT, but I forgot what was in that stash
# Where did my work go?
```

**Recovery:**
```bash
git stash list
# Find the stash
git stash show -p stash@{0}
# Or apply without removing
git stash apply stash@{0}
```

`stash` is just a stack of commits in a special ref. It's recoverable as long as you haven't run `git stash drop` or `git stash clear`.

**Prevention:** name your stashes:
```bash
git stash push -m "WIP on auth refactor, do not lose"
# Later:
git stash list
# WIP on auth refactor, do not lose - clear what's there
```

Better still: just commit your WIP. A messy commit is recoverable. A lost stash isn't.

---

## 13. Hooks that break on Windows / cross-platform

```bash
#!/bin/sh
# pre-commit hook
npm test
```

This works on Linux/macOS. On Windows, `sh` might not exist. The hook fails. Your developers on Windows can't commit.

**Fix:** use portable syntax or detect the platform:

```bash
#!/usr/bin/env bash
# Works on macOS and Linux
set -e
npm test
```

For Windows compatibility, consider:
- Use Python for hooks (`#!/usr/bin/env python`) — available everywhere
- Document the requirement and skip hooks for non-Linux devs (`git config --global core.hooksPath /dev/null` is a hack but it works)
- Use a hook manager like [Husky](https://github.com/typicode/husky) (Node) or [pre-commit](https://pre-commit.com/) (Python) that handles cross-platform

Or just keep hooks simple — if it can't be done in 5 lines, move it to CI.

---

## 14. Big files in git history (the blob problem)

You accidentally committed a 2GB log file. `git rm` removes it from HEAD but the blob stays in history. Every clone of the repo still pulls 2GB.

**The right tool is `git filter-repo`** (or `bfg-repo-cleaner`):
```bash
# Install
pip install git-filter-repo

# Remove a file from all history
git filter-repo --invert-paths --path big-file.log

# Force-push
git push --force origin main

# But anyone with old clones has the bad blob. They'll need to reclone.
```

**Prevention:** use **Git LFS** for files > 1MB:
```bash
# Track .psd files with LFS
git lfs install
git lfs track "*.psd"
git add .gitattributes
git add design.psd
git commit -m "add design file (LFS)"
```

Other big-file solutions:
- **`.gitattributes` exclude rules** for known binary folders
- **`git-fat`** for very large binaries
- **External storage** (S3 + URL) for things that don't need version history

The worst thing you can do: ignore it. It'll compound.

---

## 15. The LFS that wasn't

You set up Git LFS. You commit your 500MB design files. Everything's fine.

Then you change machines, `git clone` the repo, and the files are tiny placeholder files with a "this file is stored in LFS, download with git lfs pull" message.

**What happened:** LFS files are pointers. The actual content lives on the LFS server. If you don't `git lfs pull` (or `git lfs install && git lfs fetch && git lfs checkout`), you get the pointers.

**Prevention:**
```bash
# In your README, document:
git lfs install
git lfs pull
```

And in your CI:
```yaml
# GitHub Actions example
- uses: actions/checkout@v4
  with:
    lfs: true
```

Same problem if LFS storage gets rate-limited or the LFS server goes down. The files just vanish (or rather, become unusable placeholders). Keep a backup of your LFS files outside Git.

---

## Defend against all of these

The pattern across all of these: **Git does what you told it to, not what you meant.** A few habits that catch most issues:

1. **Read the output.** Git tells you what it's about to do. Most "disasters" are because someone didn't read a warning.
2. **`git status` is your friend.** Before any commit, push, or branch delete. Before anything.
3. **Use `git config --global core.hooksPath` to install pre-commit hooks** that catch the easy stuff: secrets, huge files, wrong files.
4. **Never force-push to a shared branch.** Use `git push --force-with-lease` on your own branches, never `--force` on main.
5. **Commit often, push when stable.** Small commits = small rollbacks.
6. **Have a Git "playground" repo** where you practice destructive operations (`git reset --hard`, `git rebase -i`, `git filter-repo`) on copies of your real code. Build muscle memory for recovery.

Most Git disasters are recoverable. Knowing that takes the panic out, and reduces the chance you'll make a panicked decision that makes things worse.

What's the worst Git moment you've had? [Drop me a line](mailto:pragmatic@pragmaticsysadmin.help) — I read every response.

---

*Related reads:*
- *[Linux Things That Are Easy to Miss](/sysadmin/2026-07-13-linux-things-easy-to-miss/) — the Linux companion to this post*
- *[Setting Up a Home Lab](/sysadmin/2025-10-29-setting-up-a-home-lab-a-beginner-s-guide/) — practice all of these safely before they hit production*
- *[The 5-Minute Server Health Check](/sysadmin/2025-12-09-the-5-minute-server-health-check-that-could-save-your-career/)*
- *[Why Your Monitoring is Broken](/sysadmin/2025-11-06-why-your-monitoring-is-broken-and-how-to-fix-it-before-your-boss-notices/)*