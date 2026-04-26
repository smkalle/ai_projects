name: Pull Request
description: Submit changes to WardOps Dashboard
labels: [pr]

body:
  - type: markdown
    attributes:
      value: |
        ## Pull Request Checklist

        Before submitting, confirm each item:

  - type: checkboxes
    id: checklist
    attributes:
      options:
        - label: Code passes `python3 -c "import ast; ast.parse(open('streamlit_app.py').read())"`
        - label: `init_db.py` runs without error
        - label: New functions have docstrings
        - label: README updated if user-facing change
        - label: No secrets / API keys in code
        - label: Branch is up-to-date with `main`
        - label: Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
        - label: Related issue linked (if applicable)

  - type: textarea
    id: description
    attributes:
      label: Description
      placeholder: What does this PR do? Why? Link any issues.
    validations:
      required: true

  - type: textarea
    id: test-notes
    attributes:
      label: Testing Notes
      placeholder: How was this tested? Any manual steps needed?
    validations:
      required: false

  - type: markdown
    attributes:
      value: |
        ## Type of Change

  - type: dropdown
    id: change-type
    attributes:
      label: Change Type
      options:
        - feat — New feature
        - fix — Bug fix
        - docs — Documentation only
        - refactor — Code restructuring (no behavior change)
        - test — Adding / updating tests
        - chore — Maintenance / tooling
      default: feat
    validations:
      required: true
