# Agent Skills for fortnite-api-sdk

This directory contains an [Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
that helps AI coding agents such as Claude Code write correct code with the `fortnite-api-sdk`
Python package.

```
skills/
└── fortnite-api/
    ├── SKILL.md                       # entry point: setup, clients, tokens, errors, models, pitfalls
    └── references/
        ├── catalog.md                 # shop, cosmetics, weapons, map, news, playlists, calendar,
        │                              # battlepass, sprites, aes, assets, crew
        ├── competitive.md             # tournaments, events, power_rankings, stats, profile
        ├── accounts-and-auth.md       # account, friends, oauth, identity, fn, quests, custom_match
        ├── replays-and-parsing.md     # replays, parsing
        └── recipes.md                 # end-to-end example programs
```

The agent reads `SKILL.md` only when a task involves the SDK, and opens a reference file only
when it needs the details of that area. The reference files list every public method with its
exact signature, return type, HTTP path, required plan and user-token requirement. They were
generated from the SDK source and the bundled OpenAPI specification.

## Installation

### Claude Code: for all of your projects

Please copy (or symlink) the `fortnite-api` folder into your personal skills directory:

```bash
mkdir -p ~/.claude/skills
cp -r skills/fortnite-api ~/.claude/skills/
# or, to pick up future updates from this checkout automatically:
ln -s "$(pwd)/skills/fortnite-api" ~/.claude/skills/fortnite-api
```

### Claude Code: for a single project

To share the skill with everyone who works on a particular project, please place it in that
project's `.claude/skills/` directory and commit it:

```bash
mkdir -p .claude/skills
cp -r /path/to/fortnite-api-sdk/skills/fortnite-api .claude/skills/
```

After installation, please start a new Claude Code session. The skill is then loaded
automatically whenever you work with `fortnite_api`, and you can also invoke it explicitly with
`/fortnite-api`.

### Claude.ai and the Claude desktop app

1. Please create a ZIP archive whose top-level entry is the `fortnite-api` folder:

   ```bash
   cd skills && zip -r fortnite-api.zip fortnite-api
   ```

2. In Claude, please open **Settings → Capabilities → Skills**, choose **Upload skill**, and
   select `fortnite-api.zip`. (Skills must be enabled for your account or organization.)

### Other agents

The skill is plain Markdown with YAML front matter, so it can also be used with any agent that
supports the Agent Skills format. Please refer to your agent's documentation for the location of
its skills directory.

## Keeping the skill up to date

The skill describes fortnite-api-sdk **0.2.0**. When you upgrade the SDK, please update your
installed copy of the skill as well (a symlink keeps it in sync with this repository
automatically).

## Feedback

If the skill leads an agent to incorrect code, we would be grateful if you could open an issue
with the prompt you used and the code that was produced.
