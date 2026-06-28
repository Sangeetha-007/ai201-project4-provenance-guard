
(1) submission flow — POST /submit → signal 1 → signal 2 → confidence scoring → transparency label → audit log → response

(2) appeal flow — POST /appeal → status update → audit log → response


Detection signals: 
<!--What are your 2+ signals? What does each one measure? What does each signal's output look like (a score between 0–1? a binary flag?), and how will you combine them into a single confidence score? -->
- LLM-based classification (Groq): ask the model to assess whether text reads as human or AI-generated. Captures semantic and stylistic coherence holistically.
- Stylometric heuristics: measurable statistical properties that differ between human and AI writing — sentence length variance, type-token ratio (vocabulary diversity), punctuation density, or average sentence complexity. AI text tends to be more uniform; human writing is more variable. Computable in pure Python.

These two signals are complementary: one is semantic, one is structural. Blending them is more informative than either alone because they capture different failure modes — the LLM classifier may miss stylistically unusual AI text; the heuristics may miss semantically coherent but structurally normal AI text.

Uncertainty representation: 
<!--What does a confidence score of 0.6 mean to your system? How will you map raw signal outputs to a calibrated score? What threshold separates "likely AI" from "uncertain" from "likely human"?-->
Each signal produces a score in [0, 1] where 1 = maximally AI-like:
- LLM classifier (Groq): the model returns a structured response with an explicit probability or label ("ai"/"human") which is mapped to a 0–1 float. Weight: 0.6 (semantic signal is more informative for holistic judgment).
- Stylometric heuristics: normalized composite of sentence-length variance, type-token ratio, and punctuation density. Low variance + high uniformity → score near 1. Weight: 0.4.

Final confidence = 0.6 × llm_score + 0.4 × stylometric_score.

A score of 0.6 means the combined evidence leans AI but is not strong enough to be definitive — both signals partially agree, or one is neutral while the other is positive.

Thresholds:
- ≥ 0.75 → "likely AI"
- 0.40–0.74 → "uncertain"
- < 0.40 → "likely human"

These bounds keep the uncertain band wide enough to avoid false high-confidence calls on borderline content (e.g., heavily templated human writing or lightly edited AI output).

Transparency label design: 
<!--What exact text will the label show for a high-confidence AI result? A high-confidence human result? An uncertain result? Write out the three label variants now, before you build the UI. -->

Appeals workflow: 
<!--Who can submit an appeal? What information do they provide? What does the system do when an appeal is received — what status changes, what gets logged? What would a human reviewer see when they open the appeal queue? -->

<!--Anticipated edge cases: What types of content will your system handle poorly? Name at least two specific scenarios — not generic risks like "inaccurate detection," but specific cases like "a poem with heavy use of repetition and simple vocabulary that your heuristics might score as AI-generated."-->


