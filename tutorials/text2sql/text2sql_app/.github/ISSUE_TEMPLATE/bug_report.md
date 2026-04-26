name: Bug Report
description: Report a bug in the WardOps Dashboard app
labels: [bug]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        ## Bug Report

  - type: textarea
    id: description
    attributes:
      label: Bug Description
      placeholder: Describe the bug clearly. What did you expect? What happened instead?
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      placeholder: |
        1. Go to '...'
        2. Enter '...'
        3. Click '...'
        4. See error
    validations:
      required: true

  - type: input
    id: streamlit-version
    attributes:
      label: Streamlit Version
      placeholder: e.g. 1.35.0
    validations:
      required: false

  - type: input
    id: python-version
    attributes:
      label: Python Version
      placeholder: e.g. 3.11.0
    validations:
      required: false

  - type: textarea
    id: error
    attributes:
      label: Error Message / Screenshot
      placeholder: Paste full error traceback or attach screenshot
    validations:
      required: false

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
    validations:
      required: false

  - type: textarea
    id: environment
    attributes:
      label: Environment
      placeholder: OS, browser, any relevant config
    validations:
      required: false
