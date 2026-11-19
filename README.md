# Postory agent kit

[Postory](https://postory.io) for AI agents: draft, schedule and publish X, Threads and Bluesky posts, attach images,
see your calendar, answer replies and read your post stats from Claude Code, Cursor, Codex, Gemini CLI, Grok Build or
any agent that reads skills.

This kit holds:

- the Postory MCP server, `https://postory.io/mcp` (hosted; you sign in to Postory in the browser on first use, no
  key or local install);
- the `postory` skill (`skills/postory/SKILL.md`): which tool when, and the rules (nothing is published without your
  yes in the chat);
- four slash commands: `/postory:plan-week`, `/postory:reply-inbox`, `/postory:weekly-review`, `/postory:daily-brief`.

## Install

### Claude Code

```sh
/plugin marketplace add vadympetryshyn/postory-agent
/plugin install postory@postory
```

Then `/mcp` → `plugin:postory:postory` → Authenticate, and sign in to Postory.

### Cursor

Clone the kit into Cursor's local plugins folder, then restart Cursor (or run **Developer: Reload Window**):

```sh
git clone https://github.com/vadympetryshyn/postory-agent ~/.cursor/plugins/local/postory
```

It adds the MCP server, the skill and the commands (`.cursor-plugin/plugin.json`). The server alone:
[Add to Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=postory&config=eyJ1cmwiOiJodHRwczovL3Bvc3RvcnkuaW8vbWNwIn0=),
or in `~/.cursor/mcp.json`:

```json
{ "mcpServers": { "postory": { "url": "https://postory.io/mcp" } } }
```

### Codex

```sh
codex plugin marketplace add vadympetryshyn/postory-agent
codex plugin add postory@postory
```

The plugin (`.codex-plugin/plugin.json`) adds the MCP server and the skill. The server alone:

```sh
codex mcp add postory --url https://postory.io/mcp
codex mcp login postory
```

or in `~/.codex/config.toml`, then `codex mcp login postory`:

```toml
[mcp_servers.postory]
url = "https://postory.io/mcp"
```

### Gemini CLI

```sh
gemini extensions install https://github.com/vadympetryshyn/postory-agent
```

Gemini CLI opens the browser to sign in on first use; `/mcp auth postory` signs in again.

### Grok Build

Add `vadympetryshyn/postory-agent` as a plugin marketplace source in Grok Build (`.grok-plugin/`), then install
`postory`.

### Any agent that reads skills

```sh
npx skills add vadympetryshyn/postory-agent
```

The skill uses the Postory MCP server: add `https://postory.io/mcp` to your agent as a remote (Streamable HTTP) MCP
server.

### Claude.ai, ChatGPT, Grok and other chat apps

Add a custom connector with the URL `https://postory.io/mcp` and sign in to Postory. Step-by-step guides per app:
<https://postory.io/features/mcp>.

## Without MCP

The HTTP API (`https://postory.io/docs/api`, a `pst_` key from Postory → MCP → API keys) reaches the same operations
with the same permissions, limits and credit prices.

## Where this comes from

This repository is published from the `agent/` folder of Postory's source by `back/scripts/publish_agent_repo.sh`;
change it there. The commands are generated from the server's MCP prompts (`back/app/mcp/prompts.py`) by
`back/scripts/build_agent_bundle.py`; never edit them by hand. After a prompt change, from the source root:

```sh
docker compose run --rm --no-deps -T -v "$PWD:/out" back python -m scripts.build_agent_bundle --write /out
```

`back/tests/unit/mcp/test_agent_bundle.py` fails while a command is stale or the manifests disagree (version, server
URL, paths). Check the Claude Code manifests with `claude plugin validate ./agent`.
