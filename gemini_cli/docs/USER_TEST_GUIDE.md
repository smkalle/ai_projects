# Memory Bridge User Test Guide

## Purpose

This guide supports early prototype testing of Memory Bridge with fictional or caregiver-approved profiles. The prototype creates non-clinical orientation, reminiscence, and caregiver communication artifacts.

Memory Bridge is not a diagnostic tool, treatment tool, medical device, emergency service, or substitute for clinical advice.

## Before A Test

Use fictional or lightly anonymized data unless the older adult, or an authorized caregiver when appropriate, has explicitly approved use of the information.

Do not include:

- medication instructions,
- diagnostic questions,
- emergency scenarios,
- disputed family history,
- financial details,
- information the caregiver marked private.

## Test Command

From the repository root:

```bash
python3 -m memory_bridge_agent
```

Choose option `1` to run the sample profile. Choose option `5` to show the
latest generated kit.

With ADK installed, the agent can also be run through:

```bash
adk run memory_bridge_agent
```

Then provide a local profile path and ask it to create a Memory Bridge kit.

## What To Review

Open the generated output directory and review:

- `orientation_board.png`
- `memory_timeline.png`
- `visit_prompts.md`
- `caregiver_handoff.md`
- `storyboard.md`
- `evaluation.json`

## Caregiver Review Checklist

Rate each item from 1 to 5:

- The artifacts feel respectful and adult.
- The artifacts avoid unsupported medical claims.
- The artifacts avoid private or excluded information.
- The orientation board is readable and printable.
- The timeline reflects only caregiver-provided events.
- The visit prompts would help a family visit.
- The handoff would help a care staff member understand the person.
- The storyboard feels emotionally appropriate.

## Interview Questions

- What would you print or use first?
- What feels useful?
- What feels wrong, awkward, or uncomfortable?
- Did the kit invent or over-assume anything?
- Did it miss anything important?
- Did it expose anything that should stay private?
- Would this help a family visit, care binder, or care handoff?
- What would prevent you from using it?

## Stop Conditions

Stop the test and fix the prototype if any artifact:

- gives diagnosis, prognosis, medication advice, or emergency guidance,
- invents a relationship, event, or medical fact,
- includes a privacy exclusion,
- uses childish or patronizing language,
- is unreadable when viewed at normal size,
- makes the caregiver review requirement unclear.

## Feedback Capture

```text
Tester role:
Profile used:
Output directory:
Usefulness rating 1-5:
Dignity/tone rating 1-5:
Readability rating 1-5:
Privacy/safety concern found? yes/no:
Unsupported fact found? yes/no:
Would use in real care context? yes/no/maybe:
Most useful artifact:
Least useful artifact:
Required changes before next test:
```
