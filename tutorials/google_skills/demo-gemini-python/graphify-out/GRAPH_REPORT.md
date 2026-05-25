# Graph Report - demo-gemini-python  (2026-05-04)

## Corpus Check
- 15 files · ~5,234 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 130 nodes · 186 edges · 17 communities (9 shown, 8 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2c45431d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]

## God Nodes (most connected - your core abstractions)
1. `_make_response()` - 24 edges
2. `_make_client()` - 22 edges
3. `TestInsuranceClaims` - 8 edges
4. `TestCLI` - 7 edges
5. `get_current_weather()` - 6 edges
6. `TestFunctionCalling` - 6 edges
7. `TestEmbeddings` - 6 edges
8. `TestSafety` - 5 edges
9. `main()` - 4 edges
10. `cosine_similarity()` - 4 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities (17 total, 8 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.19
Nodes (7): _make_client(), _make_response(), TestCodeExecution, TestSafety, TestSearchGrounding, TestStructuredOutput, TestThinking

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (16): BaseModel, ClaimClassification, ClaimNarrative, CoverageDecision, DocumentChecklist, FraudSignals, _parse_response(), Section 11 — Insurance Claims Intake Workflow Structured extraction + determinis (+8 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (8): _build_stubs(), mock_genai_modules(), Tests for all Gemini API demo modules.  All google.genai calls are fully mocked, Inject google / google.genai / google.genai.types stubs for every test., TestChat, TestGetClient, TestStreaming, TestTextGeneration

### Community 3 - "Community 3"
Cohesion: 0.25
Nodes (5): cosine_similarity(), Section 9 — Text Embeddings Generate vector embeddings for semantic search and s, Compute cosine similarity between two vectors., run(), TestEmbeddings

### Community 4 - "Community 4"
Cohesion: 0.24
Nodes (5): get_current_weather(), Section 6 — Function Calling Let the model decide when to invoke a Python functi, Return the current weather for a city (mock data)., run(), TestFunctionCalling

### Community 5 - "Community 5"
Cohesion: 0.33
Nodes (3): Return a mock response whose .parsed is a plain dict., Five mock responses for the five LLM steps, returned in sequence., TestInsuranceClaims

### Community 6 - "Community 6"
Cohesion: 0.33
Nodes (8): get_client(), _import_demo(), main(), Gemini API demo CLI — exercises 10 capabilities from the tutorial.  Usage:     p, Return a google.genai.Client.      Auth priority:       1. GEMINI_API_KEY  — set, Import a demo module by short name., run_demo(), _separator()

## Knowledge Gaps
- **23 isolated node(s):** `Gemini API demo CLI — exercises 10 capabilities from the tutorial.  Usage:     p`, `Return a google.genai.Client.      Auth priority:       1. GEMINI_API_KEY  — set`, `Import a demo module by short name.`, `Section 2 — Chat (Multi-turn Conversations) Maintain conversation history across`, `Section 8 — Code Execution Let the model write and run Python code to compute a` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_make_response()` connect `Community 0` to `Community 2`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Why does `TestEmbeddings` connect `Community 3` to `Community 2`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `TestFunctionCalling` connect `Community 4` to `Community 2`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `get_current_weather()` (e.g. with `.test_weather_tool_boston()` and `.test_weather_tool_tokyo()`) actually correct?**
  _`get_current_weather()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Gemini API demo CLI — exercises 10 capabilities from the tutorial.  Usage:     p`, `Return a google.genai.Client.      Auth priority:       1. GEMINI_API_KEY  — set`, `Import a demo module by short name.` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._