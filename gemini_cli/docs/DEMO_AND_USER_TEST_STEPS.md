# Memory Bridge Demo and User Testing Steps

## Console UI

Run the interactive console from the repository root:

```bash
python3 -m memory_bridge_agent
```

Console options:

- `1`: run the sample caregiver profile.
- `2`: demonstrate missing-consent blocking.
- `3`: demonstrate unsafe-medical-request blocking.
- `4`: run a custom JSON profile.
- `5`: show the latest generated kit and evaluation status.
- `6`: print user-testing steps.
- `q`: quit.

For a one-command demo without the menu:

```bash
python3 -m memory_bridge_agent examples/memory_profiles/maria_valid.json
```

## Five-Minute Demo Script

1. State the product boundary:
   - Memory Bridge creates caregiver-reviewed support artifacts.
   - It is not diagnosis, treatment, medication advice, emergency guidance, monitoring, or cognitive scoring.
2. Start the console:
   ```bash
   python3 -m memory_bridge_agent
   ```
3. Choose option `1`.
4. Read the output directory path from the console.
5. Choose option `5` to show generated files and evaluation status.
6. Open the output directory and show:
   - `orientation_board.png`
   - `memory_timeline.png`
   - `patient_onboarding_summary.md`
   - `storyboard_image_prompts.md`
   - `storyboard_scene_1.png`
   - `storyboard_scene_2.png`
   - `storyboard_scene_3.png`
   - `visit_prompts.md`
   - `caregiver_handoff.md`
   - `storyboard.md`
   - `evaluation.json`
7. Choose option `2` to show consent blocking.
8. Choose option `3` to show unsafe medical request blocking.
9. Close by reiterating: caregiver review is required before use.

## User Testing Session

Use fictional or caregiver-approved profiles only.

Recommended flow:

1. Explain the safety boundary and local-output behavior.
2. Run the sample kit with option `1`.
3. Ask the tester to review the output artifacts in this order:
   - `orientation_board.png`
   - `memory_timeline.png`
   - `caregiver_handoff.md`
   - `visit_prompts.md`
   - `storyboard.md`
   - `evaluation.json`
4. Ask the tester:
   - What would you print or use first?
   - What feels useful?
   - What feels wrong, awkward, or uncomfortable?
   - Did the kit invent or over-assume anything?
   - Did it expose anything that should stay private?
   - Would this help a family visit, care binder, or care handoff?
   - What would prevent you from using it?
5. Run options `2` and `3` to demonstrate safety blocks.
6. Capture ratings:
   - usefulness 1-5,
   - dignity/tone 1-5,
   - readability 1-5,
   - trust 1-5,
   - would use in real care context: yes/no/maybe.

## Stop Conditions

Stop testing and fix the prototype if an output:

- gives diagnosis, prognosis, medication advice, or emergency guidance,
- invents a family member, event, medical fact, or relationship,
- exposes a private exclusion,
- uses childish or patronizing language,
- is unreadable at normal viewing size,
- fails to make caregiver review clear.

## Cleanup

Generated kit folders are ignored by git. To remove local generated kits:

```bash
find generated_memory_kits -mindepth 1 ! -name .gitkeep -exec rm -rf {} +
```
