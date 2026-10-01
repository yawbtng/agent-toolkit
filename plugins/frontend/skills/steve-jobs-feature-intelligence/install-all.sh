#!/bin/bash
# Install Steve Jobs Feature Intelligence skill across all AI coding tools
# Source: ~/.agents/skills/steve-jobs-feature-intelligence/

SKILL="$HOME/.agents/skills/steve-jobs-feature-intelligence/SKILL.md"

echo "Installing Steve Jobs Feature Intelligence..."

# Verify source exists
if [ ! -f "$SKILL" ]; then
    echo "Error: Source skill not found at $SKILL"
    exit 1
fi

# Claude Code - symlink to shared .agents
rm -rf ~/.claude/skills/steve-jobs-feature-intelligence 2>/dev/null
ln -s ../../.agents/skills/steve-jobs-feature-intelligence ~/.claude/skills/steve-jobs-feature-intelligence
echo "✓ Claude Code: ~/.claude/skills/steve-jobs-feature-intelligence -> ~/.agents/skills/"

# Cursor - symlink to shared .agents
rm -rf ~/.cursor/skills/steve-jobs-feature-intelligence 2>/dev/null
ln -s ../../.agents/skills/steve-jobs-feature-intelligence ~/.cursor/skills/steve-jobs-feature-intelligence
echo "✓ Cursor: ~/.cursor/skills/steve-jobs-feature-intelligence -> ~/.agents/skills/"

# Codex - symlink to shared .agents
rm -rf ~/.codex/skills/steve-jobs-feature-intelligence 2>/dev/null
ln -s ../../.agents/skills/steve-jobs-feature-intelligence ~/.codex/skills/steve-jobs-feature-intelligence
echo "✓ Codex: ~/.codex/skills/steve-jobs-feature-intelligence -> ~/.agents/skills/"

# OpenCode - direct copy to ~/.config/opencode/skills/
mkdir -p ~/.config/opencode/skills/steve-jobs-feature-intelligence
cp "$SKILL" ~/.config/opencode/skills/steve-jobs-feature-intelligence/SKILL.md
echo "✓ OpenCode: ~/.config/opencode/skills/steve-jobs-feature-intelligence/"

# Gemini CLI - direct copy to ~/.gemini/skills/
mkdir -p ~/.gemini/skills/steve-jobs-feature-intelligence
cp "$SKILL" ~/.gemini/skills/steve-jobs-feature-intelligence/SKILL.md
echo "✓ Gemini CLI: ~/.gemini/skills/steve-jobs-feature-intelligence/"

echo ""
echo "Installation complete!"
echo ""
echo "Usage: /steve-jobs-feature-intelligence"
