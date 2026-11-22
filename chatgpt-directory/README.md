# ChatGPT plugin directory package

The ZIP uploaded at https://platform.openai.com/plugins contains only root `plugin.json`, `mcp.json`, and `assets/`.
Reviewer credentials belong in the dashboard's Review details, never in this package.

Validate draft metadata (requires [uv](https://docs.astral.sh/uv/)):

```sh
uv run --script agent/chatgpt-directory/validate.py --allow-missing-video
```

After recording the five positive cases in ChatGPT, host the walkthrough at a public HTTPS URL and build:

```sh
uv run --script agent/chatgpt-directory/validate.py --demo-url 'https://YOUR-VERIFIED-VIDEO-URL' --zip /tmp/postory-plugin.zip
```

Use the actual reviewer-accessible recording URL. Final validation and ZIP creation fail without it; draft validation
is explicitly incomplete. The script validates both published Agent Plugins schemas and the OpenAI field types,
listing limits, 5/3 review cases, icon dimensions, and included paths. Only deduplicated manifest-referenced icons
are packaged; stray assets and dotfiles are excluded. It does not replace portal validation or
real web/mobile test runs.

The app name is Postory; the publisher is Vadym Petryshyn, matching the approved individual verification. The
directory derives its publisher name from the verified identity selected during upload. A company publisher needs
business verification.

For the remote server, select **With MCP** and **OAuth / Dynamic Client Registration**. Postory advertises OAuth
endpoints and its registration endpoint through discovery; no client ID, secret, token, or headers are packaged.
The current OpenAI authentication-extension example conflicts with the portable MCP 1.0.0 schema, which rejects
server extensions. This package keeps the canonical portable schema valid and uses discovery; verify the imported
OAuth settings in the portal after upload rather than claiming the untested import already passed.

Process and current evidence: `agentOS/domains/integrations/docs/directories.md`.
Official field reference: https://developers.openai.com/plugins/deploy/submission
