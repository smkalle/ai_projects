# Aging Cognitive Omnimedia Use Case Recommendation

## Recommendation

Build **Memory Bridge: a reminiscence and daily-orientation media kit for older adults with mild cognitive impairment, early dementia, and their caregivers**.

This should not diagnose, treat, or claim to slow dementia. Its job is humane and practical: help a person stay connected to identity, family, routines, and care conversations through personalized, low-friction media.

The core workflow:

1. A caregiver uploads interview notes, photos, a life timeline, favorite places, routines, names, and optional clinician-approved care instructions.
2. The agent creates a personalized kit:
   - printable memory cards,
   - a one-page daily orientation board,
   - family/person timeline infographic,
   - short narrated reminiscence video script or clip,
   - conversation prompts for visits,
   - caregiver handoff summary,
   - safety-reviewed evaluation report.
3. The evaluator checks factual consistency, dignity, privacy risk, readability, emotional tone, and whether medical content is clearly non-diagnostic.

This is a better fit than generic "brain training." It is more human, less clinically overclaiming, and better matched to the notebooks' strengths in image generation, storytelling, evaluation, and ADK workflow orchestration.

## Research Signals

The need is large and emotionally loaded:

- The Alzheimer's Association reports more than 7 million Americans living with Alzheimer's, with an estimated 7.4 million age 65+ in 2026. Nearly 13 million Americans provide unpaid care, and unpaid caregivers provided more than 19 billion hours in 2025.
- Dementia care is usually dyadic: the person and caregiver function as an interdependent unit. A 2026 Frontiers scoping review of digital dyadic interventions found reported benefits across cognition, emotional well-being, quality of life, caregiver burden, and relationship quality, while highlighting access, literacy, privacy, and security barriers.
- A 2024 JMIR systematic review of VR-based reminiscence therapy found the approach safe, engaging, acceptable, and satisfying. Personalized stimulus materials tied to youth experiences were more effective than generic stimuli. Evidence quality was heterogeneous, so the product should avoid clinical efficacy claims.
- A 2022 systematic review of digital storytelling in older adults, MCI, and dementia found common use cases around memory, reminiscence, identity, and self-confidence, but also noted low clinical evidence.
- A 2025 JMIR Aging scoping review of older adults with MCI and technology perspectives recommends better usability, personalization, multimodal interaction, and integration into daily routines.
- A 2024 npj Digital Medicine meta-analysis supports computerized cognitive training as a non-pharmacologic cognitive intervention area, but this direction is more clinical and less directly suited to a fast MVP.

Sources:

- Alzheimer's Association Facts and Figures: https://www.alz.org/alzheimers-dementia/facts-figures
- Frontiers Psychiatry, digital dyadic interventions, 2026: https://www.frontiersin.org/journals/psychiatry/articles/10.3389/fpsyt.2026.1726605/full
- JMIR, VR-based reminiscence therapy systematic review, 2024: https://www.jmir.org/2024/1/e53348
- Journal of Applied Gerontology, digital storytelling systematic review, 2022: https://journals.sagepub.com/doi/10.1177/07334648211015456
- JMIR Aging, technology perspectives of older adults with MCI, 2025: https://aging.jmir.org/2025/1/e78229
- npj Digital Medicine, computerized cognitive training meta-analysis, 2024: https://www.nature.com/articles/s41746-023-00987-5

## Objective Framework

Scores are 1 to 5. Weighted score is out of 5.

| Criterion | Weight | Meaning |
| --- | ---: | --- |
| Human value | 25% | Helps dignity, identity, connection, caregiver relief, or independence. |
| Clinical safety | 20% | Avoids diagnosis/treatment claims and can be bounded as support. |
| Evidence adjacency | 15% | Aligns with studied interventions such as reminiscence, storytelling, routine support, or dyadic care. |
| Notebook fit | 15% | Reuses image, video, evaluation, brand/style, and ADK patterns. |
| Implementation ease | 15% | Can be prototyped with current repo tools and limited new infrastructure. |
| Adoption realism | 10% | Works for older adults/caregivers with low technical burden. |

## Shortlist

| Rank | Use case | Human | Safety | Evidence | Fit | Ease | Adoption | Weighted |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Memory Bridge reminiscence and orientation kit | 5 | 5 | 4 | 5 | 4 | 4 | **4.65** |
| 2 | Caregiver handoff and visit-prep kit | 5 | 4 | 4 | 4 | 5 | 4 | **4.40** |
| 3 | Daily routine visual coach | 4 | 4 | 4 | 4 | 4 | 5 | **4.05** |
| 4 | Cognitive wellness micro-lessons | 3 | 3 | 4 | 4 | 4 | 3 | **3.45** |
| 5 | Early-warning symptom diary explainer | 4 | 2 | 3 | 3 | 3 | 3 | **3.05** |

## Why Memory Bridge Wins

### It is emotionally real

The central problem is not "generate content." It is: a person is losing access to parts of their memory, and the people who love them are trying to preserve connection without turning every interaction into care administration.

The product creates artifacts that can sit on a fridge, beside a bed, in a care binder, or on a phone:

- "This is my family" card.
- "My day today" orientation board.
- "Stories I like to tell" prompt sheet.
- "How to help me when I am confused" caregiver card.
- "A short film about my life in three scenes."

### It avoids the trap of fake medicine

Brain-training products often drift into overclaiming. Memory Bridge can be explicitly positioned as psychosocial, caregiver-support, and communication support. It should say:

- not a diagnostic tool,
- not a treatment,
- not a substitute for medical advice,
- does not monitor or predict decline,
- all care instructions must come from caregivers or clinicians.

### It fits omnimedia naturally

The same personal source material can become multiple media forms:

- infographic timeline from `L_2` image-generation patterns,
- reminiscence video/storyboard from `L_3` and `L_6`,
- structured quality and safety scoring from `L_4`,
- personalized style and visual identity from `L_5`,
- ADK workflow and retry loop from `L_8` and the current repo.

## MVP

Build a local ADK agent that takes a structured JSON or Markdown profile, not free-form medical records.

Input fields:

- preferred name,
- family member names and relationships,
- 6-10 life events,
- 3 favorite places,
- 3 favorite songs, hobbies, or foods,
- daily routine,
- confusion triggers,
- calming phrases,
- privacy exclusions,
- optional photos,
- optional caregiver notes.

Outputs:

- `orientation_board.png`: name, date placeholder, today's routine, key contacts.
- `memory_timeline.png`: respectful illustrated timeline.
- `visit_prompts.md`: conversation prompts for family and care staff.
- `caregiver_handoff.md`: concise non-medical support notes.
- `storyboard.md`: 3-scene narrated reminiscence video plan.
- optional `memory_clip.mp4`: phase-two Veo output.
- `evaluation.json`: pass/fail plus criteria scores.

Evaluation schema:

- factual_consistency,
- dignity_and_tone,
- privacy_safety,
- readability_for_older_adults,
- caregiver_usefulness,
- medical_safety_boundary,
- hallucination_risk,
- overall_passed,
- revision_feedback.

## Product Guardrails

- Require consent from the older adult where possible, or caregiver attestation where not possible.
- No diagnosis, prognosis, medication advice, emergency triage, or claims about improving cognition.
- Do not infer family relationships, medical facts, trauma history, or preferences.
- Do not generate fake family photos or impersonate deceased/absent relatives.
- Mark uncertain facts as "caregiver-provided" or "needs confirmation."
- Keep outputs printable, high contrast, large type, and low visual clutter.
- Prefer caregiver-reviewed regeneration over autonomous publishing.

## Implementation Path

Phase 1: static kit generator.

- Add `aging_memory_agent/` or extend the current agent with a new workflow.
- Implement `load_profile`, `generate_orientation_board`, `generate_memory_timeline`, `generate_visit_prompts`, and `evaluate_memory_kit`.
- Use `gemini-3-flash-preview` for summarization/evaluation and `gemini-3.1-flash-image-preview` for image artifacts.

Phase 2: optional video.

- Add `plan_memory_scenes` using the `L_6` scene-planning pattern.
- Generate reference images first.
- Add Veo only after the still-image and text artifacts pass safety review.

Phase 3: caregiver loop.

- Add a revision step where the caregiver can correct names, relationships, tone, and privacy exclusions.
- Save each version with clear timestamps and no cloud sharing by default.

## Final Recommendation

Prioritize **Memory Bridge**.

It is the strongest human endeavor: preserving identity and connection under cognitive decline. It is evidence-adjacent without pretending to be clinical treatment. It is easy enough to implement from the notebooks, and it turns omnimedia generation into something a family or caregiver might actually treasure.
