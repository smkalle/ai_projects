# Repository Guidelines

## Project Structure & Module Organization

This repository contains a Vite + React frontend and Streamlit helper.

- `src/` contains React code. `src/main.jsx` mounts the app and `src/App.jsx` holds the main UI.
- `src/assets/` stores bundled frontend assets imported by React.
- `public/` stores static files served directly by Vite.
- `agylity.py` is a Streamlit workspace for Gemini Managed Agents.
- `agylity_runs/` is runtime output; avoid committing generated logs unless intentionally useful.
- `dist/` is production build output and is ignored by ESLint.

## Build, Test, and Development Commands

- `npm install` installs dependencies from `package-lock.json`.
- `npm run dev` starts the Vite dev server.
- `npm run build` creates the production bundle in `dist/`.
- `npm run preview` serves the production bundle locally.
- `npm run lint` runs ESLint over JavaScript and JSX files.

For the Streamlit app:

```bash
pip install streamlit requests
export GEMINI_API_KEY="<your Gemini API key>"
streamlit run agylity.py
```

## Coding Style & Naming Conventions

Use ES modules and React function components. Keep JSX component files in `src/` with PascalCase names such as `App.jsx`; use camelCase for variables, functions, and helpers. Follow the existing style: two-space indentation, semicolon-free JavaScript, and single quotes where practical.

`eslint.config.js` applies recommended JavaScript rules plus React Hooks and React Refresh checks. For Python, group imports by standard library, third-party packages, then local code. Use clear constants for configuration values, as in `agylity.py`.

## Testing Guidelines

No automated test framework is configured yet. For frontend changes, run `npm run lint` and `npm run build`, then verify the affected flow in the browser. If adding tests, prefer Vitest and name files `*.test.jsx` near the component or in `src/test/`.

For `agylity.py`, validate startup with `streamlit run agylity.py` and avoid making real API calls unless `GEMINI_API_KEY` is intentionally configured.

## Commit & Pull Request Guidelines

This checkout has no Git history, so no project-specific convention can be inferred. Use concise imperative commit messages, for example `Add agent run history panel` or `Fix Vite asset path`.

Pull requests should include a short summary, verification commands, linked issues when applicable, and screenshots or recordings for visible UI changes. Note required environment variables, especially `GEMINI_API_KEY`.

## Security & Configuration Tips

Never commit API keys, generated secrets, or local environment files. Keep `GEMINI_API_KEY` in the shell environment or a local ignored file. Treat files in `agylity_runs/` as potentially sensitive because they may contain prompts or model output.
