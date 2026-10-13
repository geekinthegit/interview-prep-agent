# Interview Practice Agent Specification

## Purpose

This agent asks the user questions about the coding-manual-ablation study. The user answers in their own words. The agent checks each answer against the research records and gives feedback with the source location. The goal is to help the user understand the project and explain it accurately.

## Source documents

The files in `source_docs/` are the only sources. The commit they were copied from is recorded in `source_docs/SOURCE.txt`.

- `README.md`
- `DECISIONS.md` and `decisions/`
- `AI_WORKFLOW.md`
- `docs/research-workflow.md` and `docs/ai-assisted-workflow.md`
- `reports/main-scoring-record-2026-09-24.md`
- `reports/heldout-evaluation-decision-2026-09-24.md`
- `Coding-Manual-Replacement_Project-Summary_Jiwon-Choi.md` (the application introduction)

The final research report is not included. It will be added after it is revised.

## Question types

- Fixed questions come from `question_bank.md`. Each question is paired with one or more source locations. Multiple locations are separated by ` ; `.
- Generated questions are created by the agent from one section of a source document. That section is the source location.

## Session flow

1. Scope selection. The user chooses all documents or one document. The user also chooses fixed questions only or fixed and generated questions.
2. Question. The agent asks one question. Each question has a source location in the form `file#anchor`. The location stays hidden until the user answers.
3. Answer. The user answers in their own words.
4. Record check. The agent splits the answer into claims and classifies each claim.
5. Feedback. The agent reports the label of each claim with its source location. Feedback is given after every answer.
6. Follow-up. The agent asks at most one follow-up question per question. Then it returns to step 2.
7. Session summary. When the user ends the session the agent lists each question with its claim labels. It also lists the sections the user should reread.

## Claim labels

Each claim receives one of three labels.

- Consistent with the record. A checked section states the same content.
- Inconsistent with the record. A checked section states different content.
- Not in the record. No checked section states this content.

A claim that goes beyond a claim boundary statement in section 12 of `reports/main-scoring-record-2026-09-24.md` is labeled Not in the record. The feedback also cites the identifier of that statement.

## Sections and retrieval

- Each source document is split at Markdown headings (`#`, `##`, `###`, `####`). Each section's anchor follows GitHub's anchor rule for that heading.
- A section runs from its heading to the next heading of the same or a higher level, so it includes its subsections. Both a section and its subsections are in the index, and a source location that points to a section also covers its subsections in the record check.
- Interviews are practiced in English. Keyword search assumes English answers.
- Source locations come only from this section index. Links inside the source documents are not followed.
- The record check uses the question's source sections and the top 3 other sections found by keyword search on the answer.
- If no other section matches, the record check uses the question's source sections only.
- The feedback always lists the sections used for the check. Not in the record means the claim was not found in those sections.

## Rules for the agent

- The agent does not fill gaps by guessing.
- If the agent cannot find a source section it says so.
- Every source location must point to a section that exists in `source_docs/`.

## Agent structure

The app calls the model in a fixed sequence. It does not use a tool-calling loop.

## Model and API

- Provider: OpenAI
- Model: `gpt-5.5-2026-04-23`, the snapshot used in the research
- The agent reads the key only from the environment variable `OPENAI_API_KEY_ABLATION`. It passes the key to the client explicitly. It never reads `OPENAI_API_KEY`.

## Interface

- Streamlit chat interface run locally.
- Streamlit reruns the script on every interaction. A model response is stored once it is received. It is never requested again on a rerun.