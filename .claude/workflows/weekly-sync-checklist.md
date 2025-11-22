# Weekly Upstream Sync Checklist

**Purpose:** Safely integrate upstream improvements into your fork  
**Frequency:** Weekly (or when critical upstream updates are announced)  
**Time:** 10-15 minutes (if no conflicts)  
**Agents involved:** @orchestrator-agent coordinates; specialists handle details

---

## Pre-Flight Checks

- [ ] **Current branch:** Should be on `development`
  ```zsh
  git checkout development
  git pull origin development
  ```

- [ ] **Clean working tree:** No uncommitted changes
  ```zsh
  git status  # Should show "nothing to commit, working tree clean"
  ```

- [ ] **Tests passing:** Your current code is healthy
  ```zsh
  python3 cli/run_tests.py
  ```

---

## Phase 1: Fetch & Merge (Automated)

- [ ] **Run the sync script**
  ```zsh
  ./.claude/scripts/weekly-sync.sh
  ```

**If it succeeds:** ✅ Skip to Phase 3  
**If conflicts occur:** ⚠️ Continue to Phase 2

---

## Phase 2: Conflict Resolution (Agent-Assisted)

### 2.1 Understand the conflicts

- [ ] **Ask @code-analyzer:**
  > "Explain what upstream changed in sync-inbox vs our development. Highlight conflict areas."

- [ ] **List conflicted files:**
  ```zsh
  git status | grep "both modified"
  ```

### 2.2 Resolve conflicts file-by-file

- [ ] **Ask @precision-editor for each conflicted file:**
  > "Help me resolve conflicts in `<file>`. Preserve our tests and feature flags. Show me the safest option."

- [ ] **Stage resolved files:**
  ```zsh
  git add <resolved-file>
  ```

### 2.3 Complete the merge

- [ ] **Commit the resolution:**
  ```zsh
  git commit  # Will auto-fill merge commit message
  ```

- [ ] **Push sync-inbox:**
  ```zsh
  git push -f origin sync-inbox
  ```

---

## Phase 3: Validation (Agent-Assisted)

### 3.1 Test coverage

- [ ] **Ask @test-generator:**
  > "Generate tests for files changed in sync-inbox that lack coverage."

- [ ] **Run full test suite:**
  ```zsh
  python3 cli/run_tests.py
  ```
  - **If tests fail:** Ask @precision-editor to fix breaking changes

### 3.2 Security scan

- [ ] **Ask @security-analyst:**
  > "Scan sync-inbox for secrets, misconfigs, and security issues."

- [ ] **Fix any findings:**
  - Follow agent recommendations
  - Commit fixes to sync-inbox

### 3.3 Performance check

- [ ] **Ask @performance-auditor:**
  > "Check for obvious performance regressions in sync-inbox."

- [ ] **Address critical issues** (defer optimizations to follow-up PRs)

### 3.4 Architecture review

- [ ] **Ask @architectural-critic:**
  > "Did upstream changes introduce structural drift or phase boundaries?"

- [ ] **Note any technical debt** for future cleanup

---

## Phase 4: Integration (Human Decision Point)

### 4.1 Create PR

- [ ] **Open PR from sync-inbox → development:**
  ```zsh
  gh pr create --base development --head sync-inbox \
    --title "Weekly sync: upstream improvements" \
    --body "$(git log --oneline origin/development..sync-inbox)"
  ```

### 4.2 Review & merge

- [ ] **Ask @referee-agent-csp:**
  > "Review the sync-inbox PR. Is it safe to merge?"

- [ ] **Merge if green:**
  ```zsh
  gh pr merge --squash --delete-branch
  ```

### 4.3 Update your working branch

- [ ] **Pull latest development:**
  ```zsh
  git checkout development
  git pull origin development
  ```

---

## Phase 5: Cleanup & Record

- [ ] **Tag the sync (optional):**
  ```zsh
  git tag -a sync-$(date +%Y%m%d) -m "Weekly upstream sync"
  git push origin --tags
  ```

- [ ] **Update CHANGELOG.md:**
  - Note upstream version/commit merged
  - List key improvements pulled in

- [ ] **Schedule next sync:**
  - Add calendar reminder for next week
  - Or ask @orchestrator-agent to remind you

---

## Emergency: Aborting a Sync

If things go wrong and you need to start over:

```zsh
# If merge in progress
git merge --abort

# Delete sync-inbox and start fresh
git checkout development
git branch -D sync-inbox
git push origin --delete sync-inbox

# Re-run the script when ready
./.claude/scripts/weekly-sync.sh
```

---

## Agent Quick Reference

| Phase | Agent | Query |
|-------|-------|-------|
| Conflict summary | @code-analyzer | "Explain upstream changes and conflicts" |
| Resolve conflicts | @precision-editor | "Resolve conflicts in `<file>` safely" |
| Generate tests | @test-generator | "Add tests for changed files" |
| Security scan | @security-analyst | "Scan for secrets and misconfigs" |
| Performance check | @performance-auditor | "Check for regressions" |
| Architecture review | @architectural-critic | "Check for structural drift" |
| Final decision | @referee-agent-csp | "Is sync-inbox PR safe to merge?" |
| Orchestrate all | @orchestrator-agent | "Run weekly sync ritual end-to-end" |

---

## Tips for Success

- **Start small:** First sync might take longer; subsequent syncs are faster
- **Don't panic on conflicts:** They're normal; agents will help
- **Test thoroughly:** Better to catch issues in sync-inbox than after merge
- **Ask questions:** Agents explain jargon in plain terms via @cognitive-resonator
- **Keep notes:** Document patterns you see for faster future syncs
