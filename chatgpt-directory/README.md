# ChatGPT plugin directory package

Source of the ZIP uploaded at platform.openai.com/plugins (plugin.json, mcp.json, assets/). Build:
`cd agent/chatgpt-directory && zip -r /tmp/postory-plugin.zip plugin.json mcp.json assets`.
Before uploading add `review.demo_recording_url` (the hosted demo video) to a copy of plugin.json. Reviewer
credentials never go in the ZIP (dashboard "Review details"). Process: agentOS/domains/mcp/docs/directories.md.
