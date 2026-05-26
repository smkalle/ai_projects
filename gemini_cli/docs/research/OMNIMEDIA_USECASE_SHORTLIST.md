# Omnimedia Use Case Shortlist

## Recommendation

Build a **URL-to-Omnimedia Content Kit** for technical and product marketing teams.

The user provides a blog post, announcement, documentation page, or research article URL, plus an optional brand guide image. The agent produces a small campaign kit:

- One factual infographic PNG.
- One short-form video plan or 8-second generated teaser.
- Platform-ready post copy for LinkedIn, X, and newsletter blurbs.
- A structured evaluation report for factual accuracy, spelling, brand fit, and channel readiness.

This is the strongest use case because it is compelling, easy to implement from the notebooks, and closely aligned with the current `infographic_agent` code. The repo already has blog scraping, infographic generation, image evaluation, logging, and retry logic. The notebooks add the missing pieces: prompt expansion from `L_2`, video prompt/storyboard flow from `L_3` and `L_6`, structured evaluation from `L_4`, and brand analysis from `L_5`.

## Research Signals

The market signal favors content repurposing and short-form video, especially for marketing and education workflows:

- Sprout Social's 2026 video statistics report says 91% of businesses use video as a marketing tool, 69% of video marketers favor social videos, and 63% of video marketers have used AI tools to create or edit marketing videos. It also names lack of time and lack of a starting point as video adoption barriers.
- Adobe's 2025 content creation and management report positions content creation as one of the accessible generative AI pilot areas for marketing and customer experience teams.
- Adobe's 2025 creator research says 86% of global creators use creative generative AI, with common use cases including editing/enhancing media, generating new assets, and ideation.
- The 2026 CHI paper `PaperTok` studies transforming academic papers into short-form videos and finds a similar unmet need: domain experts often lack time and production skills, while AI can automate initial script and audiovisual creation.

Sources:

- Sprout Social, "80+ Social media video statistics marketers need to know in 2026": https://sproutsocial.com/insights/social-media-video-statistics/
- Adobe, "AI and Digital Trends in Content Creation and Management": https://business.adobe.com/resources/reports/content-management-digital-trends.html
- Adobe News, "Inaugural Adobe Creators' Toolkit Report": https://news.adobe.com/news/2025/10/adobe-max-2025-creators-survey
- Cristobal et al., "PaperTok: Exploring the Use of Generative AI for Creating Short-form Videos for Research Communication": https://arxiv.org/abs/2601.18218

## Objective Scoring Framework

Scores are 1 to 5, where 5 is best. Weighted total is out of 5.

| Criterion | Weight | Definition |
| --- | ---: | --- |
| User pain and demand | 25% | Clear, recurring need with budget or workflow urgency. |
| Notebook fit | 20% | Reuses the observed notebook patterns directly. |
| Implementation ease | 20% | Can be built with the existing repo and minimal new infrastructure. |
| Differentiation | 15% | More than a thin wrapper around a generic image/video generator. |
| Evaluability | 10% | Output quality can be judged with structured criteria and retries. |
| Risk control | 10% | Low legal, factual, brand, and operational risk for an MVP. |

## Shortlist

| Rank | Use case | Demand | Fit | Ease | Diff. | Eval. | Risk | Weighted score |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | URL-to-Omnimedia Content Kit | 5 | 5 | 5 | 4 | 5 | 4 | **4.75** |
| 2 | Research Paper-to-Short Explainer Kit | 4 | 4 | 4 | 4 | 4 | 4 | **4.00** |
| 3 | Brand-Guided Product Launch Kit | 5 | 4 | 3 | 4 | 4 | 3 | **3.95** |
| 4 | Internal Training Micro-Lesson Generator | 4 | 4 | 3 | 3 | 4 | 4 | **3.65** |
| 5 | Webinar/Event Recap-to-Social Campaign | 4 | 3 | 2 | 3 | 4 | 3 | **3.10** |

## Use Case Notes

### 1. URL-to-Omnimedia Content Kit

Target user: product marketers, developer advocates, content marketers, founders, agencies.

Input: URL, optional audience, optional brand guide image, preferred channels.

Output: infographic, social captions, newsletter blurb, short video script/storyboard, optional generated reference frame or teaser clip, and an evaluation JSON.

Why it wins: it extends the existing blog-to-infographic agent with low-risk adjacent outputs. Text repurposing is straightforward with `gemini-3-flash-preview`; image generation already exists via `gemini-3.1-flash-image-preview`; video can start as script and storyboard before adding `veo-3.1-fast-generate-001`.

### 2. Research Paper-to-Short Explainer Kit

Target user: researchers, labs, universities, technical communities.

Input: paper URL or abstract.

Output: plain-English summary, infographic, 3-scene explainer script, short-form video plan, and social copy.

Why it is attractive: the `PaperTok` research validates the pain. The risk is that scholarly summarization needs stronger citation preservation and factual checks than a marketing blog workflow.

### 3. Brand-Guided Product Launch Kit

Target user: startups, SMB marketers, agencies.

Input: launch brief, product URL, brand guide image.

Output: hero infographic, launch social posts, product teaser storyboard, and brand compliance scoring.

Why it is attractive: `L_5.ipynb` maps well to brand analysis and branded asset generation. It is slightly harder than the top pick because brand consistency is stricter and may need more controls.

### 4. Internal Training Micro-Lesson Generator

Target user: enablement, HR, customer success, technical training.

Input: policy, process doc, or support article.

Output: one-page visual summary, 3-scene explainer, quiz questions, and internal announcement copy.

Why it is attractive: it has a clear productivity story and lower public-brand risk. It is less compelling for this repo because the current code is optimized around external blog URLs and public marketing output.

### 5. Webinar/Event Recap-to-Social Campaign

Target user: event marketers, community teams, podcast/webinar producers.

Input: transcript or recording notes.

Output: key takeaways infographic, quote cards, short clips or clip prompts, and follow-up posts.

Why it is lower priority: it is commercially strong, but the MVP needs transcript ingestion and possibly media clipping. That is more implementation work than the existing notebook and repo patterns require.

## MVP Definition

The first shippable MVP should avoid full video rendering unless credentials and runtime are already stable. Produce video-ready outputs first, then add Veo generation as phase two.

MVP tools:

- `extract_source_content(url)`: upgrade current scraping into structured title, summary, key claims, and source snippets.
- `generate_infographic(summary, feedback=None)`: keep current implementation.
- `generate_social_pack(summary, channels)`: create LinkedIn post, X thread, newsletter blurb, and alt text.
- `plan_video_teaser(summary)`: create 1-3 short scenes with narration, visual description, camera motion, and captions.
- `evaluate_content_kit(...)`: return JSON scores for factuality, spelling, brand fit, visual quality, channel fit, and pass/fail.
- Optional phase two: `generate_teaser_frame(...)` and `generate_teaser_video(...)`.

Success metric for the MVP: from one URL, the agent should produce a usable campaign kit in one run, with no invented facts and with evaluation feedback specific enough to drive one regeneration.

## Why This Is Easy To Implement Here

The current code already contains the hardest starting point: URL ingestion, image generation, evaluation, retry, logs, and an ADK agent wrapper. The notebook sequence supplies the exact missing recipes:

- `L_2`: prompt expansion and reference-image style conditioning.
- `L_3`: video prompt construction and image-to-video flow.
- `L_4`: structured evaluation and JSON cleanup.
- `L_5`: brand guide analysis and brand-fit scoring.
- `L_6`: scene planning and video evaluation.
- `L_8`: the direct ancestor of the current infographic workflow.

The lowest-risk implementation is not a generic "make every media format" agent. It is a focused repurposing agent that turns one source URL into a bounded, evaluated set of campaign assets.
