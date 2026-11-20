# Postory plugin for AI coding agents

**Plan, draft, schedule and publish your social media posts from your AI coding agent.** This is the plugin that connects
[Postory](https://postory.io) to Claude Code, Codex, Cursor, Gemini CLI, Grok Build and any other agent that reads
skills. Ask in plain words ("write three posts about our launch and schedule them next week") and your agent does it in
your Postory account on X, Threads, Bluesky and LinkedIn: drafts, scheduling, images, your calendar, replies and post
stats. Nothing is published without your yes in the chat.

## Fastest way: let your agent install it

Open your coding agent and paste this:

```text
Install the Postory plugin for this agent from https://github.com/vadympetryshyn/postory-agent — follow the install steps for your agent in its README, then tell me how to sign in to Postory.
```

The agent picks the right commands for itself. When it is done, sign in to Postory in the browser once (the agent tells you
how); you need a free [Postory](https://postory.io) account with your social accounts connected.

## Where it works

| Your agent | What you get |
|---|---|
| Claude Code | the plugin: Postory connection, skill and slash commands |
| Codex | the plugin: Postory connection and skill |
| Cursor | the plugin: Postory connection, skill and commands |
| Gemini CLI | the extension: Postory connection, skill and context |
| Grok Build | the plugin: Postory connection, skill and commands |
| Any agent that reads skills | the skill, plus the Postory connection you add |

**ChatGPT, Claude.ai and other chat apps do not use this plugin.** They connect with one URL, `https://postory.io/mcp`:
see the step-by-step guides at <https://postory.io/features/mcp>.

## What is inside

- **The Postory connection:** the hosted server `https://postory.io/mcp` (you sign in to Postory in the browser; no key,
  nothing to run locally). It gives your agent the Postory tools.
- **The `postory` skill:** tells your agent which tool to use when, and the rules (nothing goes out without your yes).
- **Four slash commands:** `/postory:plan-week`, `/postory:reply-inbox`, `/postory:weekly-review`, `/postory:daily-brief`.

## Install, by agent

### Claude Code

```sh
/plugin marketplace add vadympetryshyn/postory-agent
/plugin install postory@postory
```

Then `/mcp` → `plugin:postory:postory` → Authenticate, and sign in to Postory.

### Codex

```sh
codex plugin marketplace add vadympetryshyn/postory-agent
codex plugin add postory@postory
```

Then `codex mcp login postory` and sign in to Postory. Only the connection, without the plugin:
`codex mcp add postory --url https://postory.io/mcp`.

### Cursor

Clone the plugin into Cursor's local plugins folder, then restart Cursor (or run **Developer: Reload Window**):

```sh
git clone https://github.com/vadympetryshyn/postory-agent ~/.cursor/plugins/local/postory
```

Only the connection:
[Add to Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=postory&config=eyJ1cmwiOiJodHRwczovL3Bvc3RvcnkuaW8vbWNwIn0=),
or in `~/.cursor/mcp.json`:

```json
{ "mcpServers": { "postory": { "url": "https://postory.io/mcp" } } }
```

### Gemini CLI

```sh
gemini extensions install https://github.com/vadympetryshyn/postory-agent
```

Gemini CLI opens the browser to sign in on first use; `/mcp auth postory` signs in again.

### Grok Build

Add `vadympetryshyn/postory-agent` as a plugin marketplace source in Grok Build, then install `postory`.

### Any other agent that reads skills

```sh
npx skills add vadympetryshyn/postory-agent
```

The skill needs the Postory connection: add `https://postory.io/mcp` to your agent as a remote (Streamable HTTP) MCP
server.

## Update

The Postory connection (tools, prices, rules) is always current; only the skill and the slash commands are copied to your
machine.

- **Claude Code:** `claude plugin marketplace update postory`, then `claude plugin update postory@postory` (restart the
  session), or turn on auto-update for it (`/plugin` → Marketplaces → postory → auto-update; off by default for
  third-party marketplaces).
- **Codex:** `codex plugin marketplace upgrade postory`, then `codex plugin add postory@postory`.
- **Cursor:** `git -C ~/.cursor/plugins/local/postory pull`, then reload the window.
- **Gemini CLI:** `gemini extensions update postory` (or install with `--auto-update`), then restart the session.
- **Grok Build and other agents:** update the plugin or skill the way your agent updates its sources.

## Without a plugin

The HTTP API (`https://postory.io/docs/api`, a `pst_` key from Postory → MCP → API keys) reaches the same operations
with the same permissions, limits and credit prices.

## For maintainers

This repository is published from the `agent/` folder of Postory's source by `back/scripts/publish_agent_repo.sh`;
change it there. The commands are generated from the server's MCP prompts (`back/app/mcp/prompts.py`) by
`back/scripts/build_agent_bundle.py`; never edit them by hand. After a prompt change, from the source root:

```sh
docker compose run --rm --no-deps -T -v "$PWD:/out" back python -m scripts.build_agent_bundle --write /out
```

`back/tests/unit/mcp/test_agent_bundle.py` fails while a command is stale or the manifests disagree (version, server
URL, paths). The publish step stamps every manifest's version `<major>.<minor>.<number of commits touching agent/>`, so
each change reaches installed plugins. Check the Claude Code manifests with `claude plugin validate ./agent`.
