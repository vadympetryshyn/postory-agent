# Postory plugin for AI coding agents

**Run your social media with your AI coding agent.** This is the plugin that connects
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

## Sign in once

After the install your agent lists the Postory plugin (or the `postory` server) as needing sign-in or authentication.
That is normal: sign in to Postory once in the browser and pick what your agent may do.

- **Claude Code:** `/mcp` → `plugin:postory:postory` → Authenticate (or ask a Postory question: the agent gives you
  the sign-in link).
- **Codex:** run `codex mcp login postory` in a terminal (it opens the browser), then start a new Codex session.
- **Cursor:** Settings → MCP → postory → sign in.
- **Gemini CLI:** `/mcp auth postory`.
- **Any other agent:** sign in to the `postory` MCP server your agent lists as needing authentication.

If you ask a Postory question before signing in, your agent tells you the same step.

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
/plugin install postory@postory-agent
```

Then sign in once ([above](#sign-in-once)).

### Codex

```sh
codex plugin marketplace add vadympetryshyn/postory-agent
codex plugin add postory@postory-agent
```

Then sign in once ([above](#sign-in-once)): `codex mcp login postory`, then a new session. Only the connection, without the plugin:
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

- **Claude Code:** `claude plugin marketplace update postory-agent`, then `claude plugin update postory@postory-agent`
  (restart the session), or turn on auto-update for it (`/plugin` → Marketplaces → postory-agent → auto-update; off by
  default for third-party marketplaces), or keep it current automatically (below).
- **Codex:** `codex plugin marketplace upgrade postory-agent`, then `codex plugin add postory@postory-agent`.
- **Cursor:** `git -C ~/.cursor/plugins/local/postory pull`, then reload the window.
- **Gemini CLI:** `gemini extensions update postory` (or install with `--auto-update`), then restart the session.
- **Grok Build and other agents:** update the plugin or skill the way your agent updates its sources.

### Claude Code: keep it current automatically

Put this in `~/.claude/settings.json` (or a project's `.claude/settings.json`). Claude Code then refreshes the
marketplace and updates the plugin in the background after startup:

```json
{
  "extraKnownMarketplaces": {
    "postory-agent": {
      "source": { "source": "github", "repo": "vadympetryshyn/postory-agent" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "postory@postory-agent": true }
}
```

## Without a plugin

The HTTP API (`https://postory.io/docs/api`, a `pst_` key from Postory Settings → API keys) reaches the same operations
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
