name: Feature Request
description: Suggest a new feature or improvement for WardOps Dashboard
labels: [enhancement]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        ## Feature Request

  - type: textarea
    id: problem
    attributes:
      label: Problem / Pain Point
      placeholder: What problem does this solve for hospital ops staff?
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: Proposed Solution
      placeholder: Describe the feature and how it should work
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      placeholder: Any other approaches you considered?
    validations:
      required: false

  - type: markdown
    attributes:
      value: |
        ## Context

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      options:
        - P0 (Critical — blocks launch)
        - P1 (High — important)
        - P2 (Medium — nice to have)
        - P3 (Low — stretch goal)
      default: P1
    validations:
      required: true

  - type: dropdown
    id: domain
    attributes:
      label: Domain
      options:
        - Staffing / Scheduling
        - Bed Management
        - Supply / Inventory
        - Admin UI
        - Security / Compliance
        - Other
      default: Other
    validations:
      required: true

  - type: textarea
    id: brd-link
    attributes:
      label: BRD Reference
      placeholder: Link to BRD section or user story if applicable
    validations:
      required: false
