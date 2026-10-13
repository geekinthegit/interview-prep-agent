# Research Record Q&A Agent

## What this app does

This app asks me questions about my research project. I answer in my own words. The app then checks each claim in my answer against my research records. It shows which claims match the records and which do not. It also shows which sections of the records were used for each check. The goal is to help me understand my own project and explain it accurately.

## The project behind the questions

The questions are about my study coding-manual-ablation (<https://github.com/geekinthegit/coding-manual-ablation>). The study asks how replacing specific components of a coding manual with placeholders changes an LLM's agreement with human dialogue coding.

## How a session works

1. I choose all documents or one document. I also choose fixed questions only or fixed and generated questions.
2. The app asks a question.
3. I answer in English.
4. The app splits my answer into claims. Each claim gets one of three labels. The labels are Consistent with the record, Inconsistent with the record, and Not in the record.
5. The app shows the feedback and the sections used for the check. It may ask one follow-up question.
6. When I end the session the app shows a summary and a list of sections to reread.

## Source documents

The app reads only the files in `source_docs/`. They are copied from the coding-manual-ablation repository (<https://github.com/geekinthegit/coding-manual-ablation>). The source commit is recorded in `source_docs/SOURCE.txt`. The fixed questions and their source locations are in `question_bank.md`.

## How the record check works

Each document is split into sections at its Markdown headings. A check uses the question's source sections. It also uses the top 3 other sections found by keyword search on my answer. A claim that goes beyond a claim boundary in the study's scoring record is labeled Not in the record. The app does not fill gaps by guessing. If a claim is not found in the checked sections the app says so.

## How to run

This project used my personal OpenAI API key. It did not use the API key provided by the course. To run the app yourself put your own OpenAI API key in the environment variable `OPENAI_API_KEY_ABLATION`. The app needs Python with the `openai` and `streamlit` packages. Then run this command from the repository root.

```bash
streamlit run app.py
```

The app uses the model `gpt-5.5-2026-04-23`. Each answer check is one API call. The tests run without API calls.

```bash
python3 -m pytest
```

## Demo video

<https://drive.google.com/file/d/1V_jS2COTiqaqYtEyRNG6MLw6Pdy2_mf9/view?usp=sharing>

## Limitations

- Answers must be in English. Keyword search does not match answers in other languages to the English documents.
- Keyword search can miss a relevant section when the wording differs. Therefore Not in the record means the claim was not found in the checked sections. It does not prove that the records lack it.
- The session summary shows claim labels but not the claim text.
- The claim boundary check was not tested in the trial run.
- A generated question can come from a very large section such as a whole document.
- Only one short trial session was run. Label accuracy was not evaluated.

## Repository layout

- `app.py` is the Streamlit interface.
- `prep_agent/` holds the section index, retrieval, prompts, API calls, and session logic.
- `tests/` holds tests that run without API calls.
- `docs/spec.md` is the specification.
- `WORKFLOW.md` is the development plan and its progress.
- `AGENTS.md` and `CLAUDE.md` are instructions for coding agents.
- `question_bank.md` holds the fixed questions.
- `source_docs/` holds the research documents.

## How it was built

Claude Code wrote the code by following `docs/spec.md` and `WORKFLOW.md`. I made the design decisions and reviewed each step before committing.
