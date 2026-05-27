# agylity

Minimal agent workspace for experimenting with Gemini Managed Agents. The repo includes a Streamlit app for day-to-day agent runs and a Vite/React prototype UI.

## Features

- Gemini Managed Agent calls through the beta Interactions API.
- Environment-based API key loading with optional in-app override.
- Multi-turn sessions with `previous_interaction_id`.
- Remote sandbox continuity through `environment_id`.
- Step inspection, history export, and sandbox command probing.
- High-contrast teal Streamlit UI with escaped output rendering.

## Repository Layout

```text
agylity.py          # Streamlit app
src/                # React prototype source
public/             # Static frontend assets
package.json        # Vite/React scripts
AGENTS.md           # Contributor guide
```

Generated files are intentionally ignored, including `node_modules/`, `dist/`, local `.env` files, Python caches, and `agylity_runs/`.

## Requirements

- Python 3.10+
- Node.js 20+ for the React prototype
- A Gemini API key with Managed Agents access

## Streamlit App

Use an environment variable rather than committing credentials:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit requests
export GEMINI_API_KEY="<your Gemini API key>"
streamlit run agylity.py
```

Open the local URL printed by Streamlit. The app will show `connected env` when it loaded the key from `GEMINI_API_KEY`.
You can also copy `.env.example` to `.env` for local notes, but the Streamlit app reads the shell environment directly.

## React Prototype

```bash
npm install
npm run dev
```

Useful checks:

```bash
npm run lint
npm run build
python3 -m py_compile agylity.py
```

## Security

Do not commit API keys, `.env` files, Streamlit secrets, browser storage exports, or `agylity_runs/` logs. Run logs can contain prompts, model output, tool calls, and identifiers.

If a secret is accidentally committed, rotate it before publishing the repository.

## Contributing

Keep changes focused and include the verification commands you ran. For UI changes, include a screenshot or a short description of the tested flow.

## License

No license file is included yet. Add a `LICENSE` file before publishing if you want external users to have explicit open-source reuse rights.
