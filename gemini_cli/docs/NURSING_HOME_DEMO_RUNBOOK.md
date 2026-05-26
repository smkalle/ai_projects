# Memory Bridge Nursing Home Demo Runbook

## Who Runs This

A staff member, activities coordinator, social worker, care manager, or family caregiver runs the prototype. The older adult should not need to operate the software.

## Start The Staff UI

From the repository root:

```bash
streamlit run memory_bridge_staff_app.py --server.port 8502
```

Open:

```text
http://localhost:8502
```

## Fifteen-Minute Demo

1. Open the staff UI.
2. Read the safety banner aloud:
   - not diagnosis,
   - not treatment,
   - not medication advice,
   - not emergency guidance,
   - caregiver review required.
3. Go to **Run Demo**.
4. Click **Run sample Memory Bridge kit**.
5. Go to **Review Latest Kit**.
6. Review:
   - orientation board,
   - memory timeline,
   - storyboard images,
   - caregiver handoff,
   - visit prompts,
   - storyboard,
   - evaluation JSON.
7. Go to **Safety Checks**.
8. Run both safety checks:
   - missing consent,
   - unsafe medical request.
9. Ask staff whether the board, timeline, and handoff would be useful in a care binder, family visit, or room orientation context.

## Realistic Pilot Flow

Use fictional or consent-approved resident data only.

1. Ask staff to choose one resident profile they are allowed to use.
2. Use **Patient Onboarding**.
3. Enter only:
   - preferred name,
   - authorized caregiver/provider,
   - key contact,
   - observed symptoms or concerns,
   - context around symptoms,
   - 3-6 life events,
   - daily routine,
   - calming phrases,
   - triggers,
   - private topics to exclude.
4. Click **Create Kit**.
5. Review outputs with staff before showing anyone else.
6. Mark corrections directly in the feedback form from `docs/USER_TEST_GUIDE.md`.

## What To Observe

For staff:

- Does this reduce time creating orientation or care-binder materials?
- Is the output respectful enough for real use?
- Are the artifacts readable at a glance?
- Which artifact would they actually use first?
- What information was missing from the intake form?

For family caregivers:

- Does this feel like the person?
- Did it avoid sensitive topics?
- Did it invent anything?
- Would this help a visit?

For the older adult, only if appropriate and consented:

- Do they recognize familiar places, routines, or names?
- Do they seem comfortable with the artifact?
- Is anything upsetting, confusing, or too busy?

## Stop Conditions

Stop the pilot immediately if an artifact:

- includes medical advice,
- invents a family fact or life event,
- leaks a private excluded topic,
- feels patronizing,
- causes distress,
- is used without caregiver/staff review.

## After The Session

Capture:

- staff role,
- profile type: fictional, anonymized, real consented,
- generated output directory,
- audit-log event count,
- usefulness 1-5,
- dignity/tone 1-5,
- readability 1-5,
- trust 1-5,
- artifact most likely to be used,
- artifact least likely to be used,
- must-fix issues before next test.

Generated outputs stay local in `generated_memory_kits/`.
