# Contributing to WardOps Dashboard

Thanks for your interest! Here's how to work on this project.

---

## Dev Setup

```bash
cd text2sql_app
pip install -r requirements.txt
export ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_KEY>
streamlit run streamlit_app.py
```

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, production-ready |
| `feat/*` | New features |
| `fix/*` | Bug fixes |
| `admin/*` | Admin tab / UI improvements |

---

## Code Style

- **Python**: PEP 8, max line length 120
- **Streamlit**: use `st.` prefix consistently; group related calls in `with` blocks
- **Type hints**: preferred for new functions
- **Docstrings**: Google style for all public functions

---

## Commit Format

```
<type>(<scope>): <description>

Types: feat | fix | docs | refactor | test | chore
Scope: streamlit | admin | schema | db | ci
```

**Examples:**
```
feat(admin): add SQL translation verifier panel
fix(schema): correct overtime threshold logic in init_db
docs(readme): add quick start section
```

---

## Testing

```bash
# Syntax check (no dependencies needed)
python3 -c "import ast; ast.parse(open('streamlit_app.py').read())"
python3 -c "import ast; ast.parse(open('init_db.py').read())"
```

---

## Reporting Issues

Use the [issue tracker](../../issues). Label bugs with `bug`, features with `enhancement`.

When reporting, include:
- Streamlit version (`pip show streamlit`)
- Python version (`python3 --version`)
- Exact error message / screenshot
- Steps to reproduce

---

## Pull Request Checklist

- [ ] `streamlit_app.py` passes syntax check (`ast.parse`)
- [ ] `init_db.py` runs without error
- [ ] New features have docstrings
- [ ] README updated if user-facing change
- [ ] No secrets / API keys in code
