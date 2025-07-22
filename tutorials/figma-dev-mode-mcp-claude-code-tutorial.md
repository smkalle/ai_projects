# Accelerating Design‑to‑Code with **Figma Dev Mode MCP Server** + **Claude Code**

> **Last updated:** 2025-07-22  

---

## 🚀 Key Points
- **Up to 30 % faster** dev cycles by letting Claude Code read structured design data via Figma’s Dev Mode MCP server.  
- Direct MCP access *improves accuracy* versus screenshot‑based prompting, though **manual polish** is still required.  
- Supports modern editors (VS Code, Cursor, Claude CLI) starting **June 2025** open beta.  
- Workflow = **Set up server → Configure project → Authenticate → Generate → Refine**.

---

## 1 | Overview

This guide shows how to wire up Figma’s Dev Mode **Model Context Protocol** (MCP) server with **Anthropic Claude Code** (powered by _Claude Sonnet 3.5_, the top‑scoring coding LLM in recent benchmarks) to turn pixel‑perfect designs into production‑ready code.  
The workflow has been demonstrated live by Anthropic designer **Meaghan Choi** on YouTube and is already reducing hand‑off friction for early adopters.

> **Beta notice:** the Dev Mode MCP server is _still in open beta_. Expect occasional breaking changes and missing endpoints.

---

## 2 | Prerequisites

| Requirement | Notes |
|-------------|-------|
| Figma account | **Dev** or **Full** seat (Pro, Org, or Enterprise). |
| Claude Code CLI | `npm i -g @anthropic-ai/claude` or grab the desktop build. |
| Node ≥ 18 LTS  | Needed for the MCP helper (`npx`). |
| Basic CLI & web auth | You’ll paste generated commands and auth URLs. |

---

## 3 | Step‑by‑Step Setup

### ✨ Step 1 – Generate the MCP setup command

1. Visit **[mcp.composio.dev](https://mcp.composio.dev)** ➜ _Figma_.
2. Click **“Generate command”** next to your Figma file or team.
3. Copy the resulting `npx @composio/mcp@latest setup …` string.

Example:
```bash
npx @composio/mcp@latest setup   "https://mcp.composio.dev/partner/composio/figma/mcp?customerId=<YOUR_ID>"   "figma-605dcr-13" --client claude
```

> Replace `<YOUR_ID>` with your customer ID.  
> Using **Cursor**? Switch `--client claude` → `--client cursor`.

---

### 🔧 Step 2 – Run the setup command

```bash
# anywhere in your shell
npx @composio/mcp@latest …     # paste the full command
```

This writes the global config to:<br>
`~/.config/Claude/claude_desktop_config.json`

---

### 📂 Step 3 – Make it project‑local (optional)

```bash
cp ~/.config/Claude/claude_desktop_config.json .mcp.json
```
Committed configs keep team settings version‑controlled.

---

### 🚀 Step 4 – Launch Claude Code

```bash
cd path/to/your/project
claude            # or open the desktop app
```

Inside Claude, confirm connectivity:
```
/mcp
```
The tool list should include `figma‑605dcr‑13 ✓ connected`.

---

### 🔑 Step 5 – Authenticate with Figma via Composio

Type in Claude:
```
Please connect to the Figma MCP server.
```
Follow the browser link ➜ grant access ➜ return to terminal.

---

### 🎨 Step 6 – Generate code from a design

Prompt Claude:
```
Clone the dashboard from this Figma file:
https://www.figma.com/file/ABC123/Design-System.
Use React + Tailwind. Pixel‑match the layout.
```

Generation may take **3‑5 min** depending on file size.

---

### 🛠️ Step 7 – Refine & integrate

1. **Run locally** – check for missing interactions.
2. Ask Claude follow‑up prompts, e.g.  
   *“Make buttons hover‑animate using Tailwind.”*
3. Manually clean “magic numbers” or redundant CSS.

---

## 4 | Best Practices

| Area | Tip |
|------|-----|
| **Context** | Store design system docs in `/docs/*.md` and reference them in prompts. |
| **Granularity** | Select a single Figma component → generate → commit, rather than whole pages. |
| **IDE tooling** | Use Cursor or VS Code MCP plugins for inline previews. |
| **Review** | Pair AI output with visual diff tools (e.g., Builder.io **Fusion**) to catch drift. |
| **Versioning** | Commit generated code to a feature branch; request design review before merge. |

---

## 5 | Known Limitations (July 2025)

- **No rendered viewport** inside Claude ➜ needs external preview.
- Occasional `404 design node` errors for variant components.
- Large Figma files (>1 k layers) may hit _timeout_.
- Beta API surface subject to change without notice.

---

## 6 | Further Reading

- **Figma Help – Dev Mode MCP Server**  
  <https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server>
- **Composio Blog – How to use Figma MCP with Claude Code**  
  <https://composio.dev/blog/how-to-use-figma-mcp-with-claude-code-to-build-pixel-perfect-designs>
- **Anthropic News – Claude 3.5 Sonnet**  
  <https://www.anthropic.com/news/claude-3-5-sonnet>

---

## 7 | License

Released under the **MIT License**.  
Feel free to fork, star, and submit PRs!

---

_Generated with ❤️ by Google AI PM + Claude Code_
