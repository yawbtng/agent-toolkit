#!/bin/bash
# Install Steve Jobs Design System as a skill across all AI coding tools
# Source: ~/.agents/skills/steve-jobs-design/

SKILL="$HOME/.agents/skills/steve-jobs-design/SKILL.md"

echo "Installing Steve Jobs Design System..."

# Verify source exists
if [ ! -f "$SKILL" ]; then
    echo "Error: Source skill not found at $SKILL"
    exit 1
fi

# Claude Code - symlink to shared .agents
rm -rf ~/.claude/skills/steve-jobs-design 2>/dev/null
ln -s ../../.agents/skills/steve-jobs-design ~/.claude/skills/steve-jobs-design
echo "✓ Claude Code: ~/.claude/skills/steve-jobs-design -> ~/.agents/skills/"

# Cursor - symlink to shared .agents
rm -rf ~/.cursor/skills/steve-jobs-design 2>/dev/null
ln -s ../../.agents/skills/steve-jobs-design ~/.cursor/skills/steve-jobs-design
echo "✓ Cursor: ~/.cursor/skills/steve-jobs-design -> ~/.agents/skills/"

# Codex - symlink to shared .agents
rm -rf ~/.codex/skills/steve-jobs-design 2>/dev/null
ln -s ../../.agents/skills/steve-jobs-design ~/.codex/skills/steve-jobs-design
echo "✓ Codex: ~/.codex/skills/steve-jobs-design -> ~/.agents/skills/"

# OpenCode - direct copy to ~/.config/opencode/skills/
mkdir -p ~/.config/opencode/skills/steve-jobs-design
cp "$SKILL" ~/.config/opencode/skills/steve-jobs-design/SKILL.md
echo "✓ OpenCode: ~/.config/opencode/skills/steve-jobs-design/"

# Gemini CLI - direct copy to ~/.gemini/skills/
mkdir -p ~/.gemini/skills/steve-jobs-design
cp "$SKILL" ~/.gemini/skills/steve-jobs-design/SKILL.md
echo "✓ Gemini CLI: ~/.gemini/skills/steve-jobs-design/"

echo ""
echo "Installation complete!"
echo ""
echo "Usage: /steve-jobs-design"
