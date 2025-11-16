#!/bin/zsh
# Weekly Sync Script for Skill_Seekers Fork
# Purpose: Safely pull upstream changes into a sandbox branch for review
# Usage: ./.claude/scripts/weekly-sync.sh
# When: Run weekly or when you hear about important upstream updates

set -e  # Exit if any command fails

echo "🔄 Starting weekly upstream sync..."

# Step 1: Make sure we're up to date with our own fork
echo "\n📥 Fetching latest from your fork (origin)..."
git fetch origin

# Step 2: Download latest upstream changes (doesn't change your code yet)
echo "\n📥 Fetching latest from upstream (original repo)..."
git fetch upstream

# Step 3: Create or reset the sync-inbox branch
# This is a sandbox where we test upstream changes before merging to development
echo "\n🌿 Creating/resetting sync-inbox branch..."
git checkout -B sync-inbox origin/development

# Step 4: Try to merge upstream changes
echo "\n🔀 Merging upstream/development into sync-inbox..."
if git merge upstream/development --no-edit; then
  echo "✅ Clean merge! No conflicts."
else
  echo "⚠️  Conflicts detected. Don't worry - this is normal."
  echo "    Next steps:"
  echo "    1. Ask @precision-editor to help resolve conflicts"
  echo "    2. Run: git add <resolved-files>"
  echo "    3. Run: git commit"
  echo "    4. Continue with the checklist"
  exit 1
fi

# Step 5: Show what changed
echo "\n📊 Summary of changes from upstream:"
git log --oneline origin/development..sync-inbox | head -10

# Step 6: Push the sync-inbox branch
echo "\n📤 Pushing sync-inbox to your fork..."
git push -f origin sync-inbox

echo "\n✅ Sync complete! Next steps:"
echo "   1. Ask @code-analyzer: 'Explain the upstream changes in sync-inbox'"
echo "   2. Ask @test-generator: 'Generate tests for changed files'"
echo "   3. Run tests: python3 cli/run_tests.py"
echo "   4. Ask @security-analyst: 'Scan for secrets and misconfigs'"
echo "   5. Open PR: gh pr create --base development --head sync-inbox"
echo "\n   Or ask @orchestrator-agent to handle steps 1-5 automatically."
