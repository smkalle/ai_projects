---
name: hr-onboarding-manager
description: Guides HR teams and managers through complete employee onboarding following SHRM's 4 C's framework (Compliance, Clarification, Culture, Connection). Use when anyone says "onboard a new employee", "new hire starting", "create a 30-60-90 day plan", "new hire checklist", "what paperwork does a new hire need", "help me onboard someone", or "onboarding plan for". Produces phase-by-phase plans, compliance checklists (I-9, W-4, state forms), IT provisioning, buddy assignments, check-in agendas, and 90-day trackers. Always use this skill when the goal involves starting a new employee — even if the user only mentions first-day tasks or new hire paperwork.
license: MIT
compatibility: Claude.ai, Claude Code
metadata:
  author: skill-master-builder
  version: 1.0.0
  category: workflow-automation
---

# HR Onboarding Manager

Runs complete employee onboarding for HR teams and managers — from offer acceptance through 90-day milestone close — following SHRM's 4 C's: Compliance, Clarification, Culture, Connection.

CRITICAL: Before generating any onboarding plan, collect these inputs from the user:
1. **New hire name, title, and department**
2. **Start date** (to calculate pre-boarding timeline)
3. **Work type:** On-site | Remote | Hybrid
4. **State of employment** (for state-specific compliance)

If any input is missing, ask before proceeding. Do not generate a plan with unknown compliance jurisdiction.

---

## Phase 0: Intake

Ask the user for:
- New hire name, title, department
- Start date
- Work type (on-site / remote / hybrid)
- State of employment
- Buddy/mentor program in use? (yes/no)
- HRIS system (Workday, BambooHR, Rippling, other, none)

Summarize as a **New Hire Card** and confirm before generating the plan:

```
NEW HIRE CARD
━━━━━━━━━━━━━━━━━━━━━━━━━
Name:        [name]
Role:        [title] — [department]
Start Date:  [date]
Work Type:   [on-site/remote/hybrid]
State:       [state]
Buddy Prog:  [yes/no]
HRIS:        [system or "not specified"]
━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Phase 1: Pre-Boarding (T-14 to T-1 Days)

Generate a pre-boarding task list with owner and due date for every item.

### HR Actions
- Send welcome email from hiring manager (within 48 hours of offer acceptance)
- Distribute paperwork packet: I-9, W-4, state tax form, direct deposit, emergency contact, handbook
- File state new hire report (required in all 50 states — due within 20 days of hire)
- Register new hire in HRIS and initiate benefits enrollment session
- For full compliance list → see `references/compliance-requirements.md`

### Manager Actions
- Assign buddy/mentor using `assets/buddy-assignment-form.md`
- Block first two weeks of new hire's calendar: orientation, 1:1s, team intros
- Send logistics email: first-day time, location or login link, dress code, parking/badge pickup
- Brief existing team on new hire's role before start date

### IT / Facilities Actions
- Use `assets/it-provisioning-checklist.md` to track hardware and software setup
- Provision: email, Slack/Teams, HRIS access, VPN, role-specific software
- Remote hires: ship equipment with tracking; confirm delivery by T-3 days

CRITICAL: Verify IT provisioning is complete by T-2 days. Equipment not ready on Day 1 is the #1 onboarding failure point.

**Output:** Pre-Boarding Checklist table (Item | Owner | Due Date | Status).

---

## Phase 2: Day 1 Execution

Generate a Day 1 run-of-show schedule for the hiring manager.

### Morning Block (9:00 AM – 12:00 PM)
1. Manager greets new hire as first point of contact
2. Office tour OR virtual platform walkthrough (remote)
3. Introduce to buddy/mentor
4. Verify all system access: email, Slack, HRIS, VPN — fix issues before afternoon
5. Complete I-9 Section 2 (MUST be done by end of Day 3 — federal law)
6. Team introduction meeting: 15–30 min icebreaker activity

### Afternoon Block (1:00 PM – 5:00 PM)
1. Manager 1:1: role overview, 30-day expectations, communication preferences
2. Walk through first-week schedule together
3. Assign first quick-win task (completable in 1–2 days)
4. End-of-day check-in: "How did Day 1 feel? Any questions or blockers?"

CRITICAL: I-9 Section 2 must be completed by END of Day 3. Fines start at $272 per violation. Never defer this.

**Output:** Day 1 Run-of-Show with time blocks, owner, and success indicator for each item.

---

## Phase 3: Week 1 Plan (Days 2–7)

Generate a Week 1 daily schedule across four parallel tracks.

### Compliance Track (HR owns)
- Launch mandatory training: EEOC/anti-harassment, security awareness, safety (role-specific)
- Collect any outstanding paperwork: W-4, state tax, direct deposit, emergency contact
- Confirm I-9 Section 2 completion (if not done Day 1 — escalate immediately)
- Target: 100% mandatory training completion by Day 30

### Role Track (Manager owns)
- Daily 15-minute check-ins (short, consistent — do not skip)
- Role-specific sessions: tools, key processes, stakeholder map
- Deliver written 30-60-90 day expectations document by Day 5

### Culture Track (Buddy + Team own)
- Buddy daily check-ins: informal, 15–20 minutes each
- Team lunch or virtual coffee chat (schedule by Day 3)
- Cross-functional intro meetings: max 2–3 per week to avoid overload

### Connection Track (Manager + HR own)
- Lock in 30-day check-in meeting on calendar now
- Share org chart and "who's who" guide
- Add new hire to team Slack channels, distribution lists, and shared calendars

**Output:** Mon–Fri daily schedule grid (Time | Activity | Owner | Track).

---

## Phase 4: 30-Day Checkpoint

Generate a check-in agenda and assessment form.

### Pre-Meeting (HR sends 3 days before)
- Mandatory training completion status report
- Week 1 pulse survey results (if used)

### Check-In Agenda (30 min) — full template in `assets/30-day-checkin-template.md`
1. How are you feeling overall? (5 min — open-ended, listen first)
2. Role clarity: Do you understand your responsibilities and priorities? (10 min)
3. Tools and access: Anything missing or broken? (5 min)
4. Culture and team: How are relationships developing? (5 min)
5. Feedback: What could we improve in your onboarding? (5 min)

### Manager Assessment (document in HRIS)
Rate new hire 1–5 on:
- **Task Mastery** — performs basic job functions with guidance
- **Culture Fit** — aligns with team values and communication style
- **Initiative** — proactively asks questions and seeks to contribute

Flag any rating of 1–2 for immediate HR discussion.

**Output:** 30-day agenda, assessment form, recommended actions if ratings are low.

---

## Phase 5: 60-Day Progress Review

### Focus: Independent Performance
By Day 60, new hire should work independently on most tasks.

### Review Topics
1. Performance against 30–60 day milestones (from expectations doc)
2. Career development interests and growth path discussion
3. Any role-scope adjustments needed
4. Team integration assessment from buddy and peer feedback
5. Outstanding training completion check

### Manager Assessment — add to Day 60 HRIS record
Same 1–5 scale plus:
- **Independence** — works without step-by-step guidance
- **Quality** — output meets team standards consistently

**Output:** 60-day review form. If any rating is 1–2, generate a 30-day improvement plan outline.

---

## Phase 6: 90-Day Formal Review and Onboarding Close

CRITICAL: The 90-day review is a legal document. It must be signed by both parties and retained in HRIS.

### Steps (in order — do not skip)
1. Manager completes written 90-day performance evaluation
2. HR schedules formal review meeting (30–45 min)
3. New hire completes self-assessment (optional but recommended)
4. Both parties review, discuss, and sign evaluation
5. Goals set for months 4–12
6. Onboarding record marked COMPLETE in HRIS
7. All compliance documentation verified and filed

### Onboarding Closure Checklist (all must be confirmed)
- [ ] I-9 on file, verified, stored per retention rules (3 yrs from hire OR 1 yr post-separation)
- [ ] W-4 and state tax forms filed
- [ ] State new hire report submitted
- [ ] All mandatory training completed and logged
- [ ] 30-day and 60-day reviews documented in HRIS
- [ ] 90-day evaluation signed by both parties and stored
- [ ] Benefits enrollment confirmed

**Output:** 90-day evaluation form, onboarding completion certificate, HRIS close checklist.

---

## Examples

### Example 1: Standard hire with time to plan
**User says:** "I need to onboard a new software engineer starting in two weeks, hybrid, New York."
**What Claude does:**
1. Confirms New Hire Card
2. Generates Pre-Boarding Checklist with NY-specific state forms flagged
3. Produces Day 1 Run-of-Show and Week 1 plan (hybrid tracks for in-person + remote days)
4. Creates 30/60/90-day checkpoint templates pre-filled for engineering role
**Result:** Complete 6-phase onboarding package, NY-compliant.

### Example 2: Compressed timeline (starts in 3 days)
**User says:** "Our new marketing manager starts Thursday — help!"
**What Claude does:**
1. Flags compressed timeline — identifies pre-boarding items at risk
2. Sorts checklist by urgency: IT provisioning (critical), I-9 preparation, welcome email
3. Notes equipment may need overnight shipping or remote-first workaround
4. Produces emergency Day 1–5 plan with daily manager touch points
**Result:** Triage plan prioritized by legal deadline and business impact.

### Example 3: 30-60-90 day plan only
**User says:** "Create a 30-60-90 day onboarding plan for a new sales rep in Texas."
**What Claude does:**
1. Skips full intake, asks only: name, start date, work type
2. Generates sales-specific milestone plan (quota ramp, pipeline building, tool certification)
3. Includes Texas-specific compliance notes
**Result:** Role-specific milestone plan with compliance callouts.

---

## Error Handling

### Missing Start Date
**Cause:** User didn't provide start date.
**Fix:** Ask: "What is the new hire's first day? I need this to calculate the pre-boarding timeline and compliance deadlines."

### Compressed Pre-Boarding (Less Than 5 Business Days)
**Cause:** New hire starts before standard 14-day window.
**Fix:** Flag items at risk. Reprioritize by urgency: (1) IT provisioning, (2) I-9 preparation, (3) welcome communication. Note risks explicitly.

### Unknown State of Employment
**Cause:** User didn't specify state.
**Fix:** Apply federal minimums only. Note: "State-specific requirements vary — consult `references/compliance-requirements.md` and confirm your state's new hire reporting deadline."

### Manager Unavailable on Day 1
**Cause:** Hiring manager is traveling or out.
**Fix:** Assign a designated Day 1 host (HR or team lead). Manager must complete 1:1 within first 3 days. Flag this as a culture risk.

---

## Quality Checklist

Before delivering any onboarding plan, verify:
- [ ] New Hire Card confirmed before plan generation
- [ ] I-9 Day 3 deadline explicitly called out
- [ ] State compliance noted or flagged as unknown
- [ ] IT provisioning checklist included
- [ ] All 6 phases present with owner assigned to every action
- [ ] 30/60/90-day agendas included
- [ ] Closure checklist included in Phase 6

## Performance Notes

Take time to do this thoroughly. A missed compliance step — especially I-9 — can result in federal fines starting at $272 per violation. Quality matters more than speed here.

---

## Reference Files

- `references/domain-notes.md` — SHRM 4 C's, key HR concepts, success metrics
- `references/compliance-requirements.md` — Federal and state compliance rules, retention requirements
- `assets/it-provisioning-checklist.md` — IT setup tracking template
- `assets/buddy-assignment-form.md` — Buddy/mentor assignment and briefing template
- `assets/30-day-checkin-template.md` — Full 30-day check-in agenda with discussion guides
