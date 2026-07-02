# titanic

## gstack (optional)

gstack is a toolkit of AI "skills" for Claude Code. It's **optional** here — nothing is
blocked if it's missing, and you never have to stop work to install it.

If you want the skills (`/office-hours`, `/review`, `/ship`, `/investigate`, etc.),
install once:

```bash
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

Then restart your AI coding tool. `/browse` and the browser skills need open network
and a display, so they only work on a local machine (not a locked-down cloud sandbox).
