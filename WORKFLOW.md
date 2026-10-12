# WORKFLOW

This workflow is a revisable work plan. If changes are needed, propose them with reasons and identify the affected steps. Update the plan after the user approves.

Follow AGENTS.md throughout all work. Keep unresolved decisions open until the user explicitly approves them.

## 0. Repository Setup — Completed

0.1 Create a new repository and connect it to GitHub.

0.2 Copy the research documents and project introduction into source_docs/. Record the source commit in SOURCE.txt.

0.3 Make the initial commit and push.

## 1. Define the Functional Scope — Planning Chat — Completed

1.1 Confirm the interview flow: scope selection → question → answer → comparison with records → feedback → follow-up question → session summary. — Decided

1.2 Decide the unresolved settings. — Decided. At most one follow-up question per main question. The user chooses fixed questions only or fixed and generated questions at the start of each session. Feedback is given after every answer.

1.3 Define the answer classification criteria: consistent with the records / inconsistent with the records / not found in the records. — Decided. Each claim in an answer is labeled separately. A claim that goes beyond a claim boundary statement in §12 is labeled not found in the records, and the feedback cites the statement identifier.

1.4 Finalize the list of input documents. — Decided. All files in source_docs/. The final research report will be added after it is revised.

1.5 Write docs/spec.md and commit. — Completed

## 2. Select the Technology — Planning Chat — Completed

2.1 Choose the LLM API and model. — Decided. OpenAI, gpt-5.5-2026-04-23.

2.2 Choose the interface. — Decided. Streamlit chat interface run locally. Model responses are stored and never requested again on a rerun.

2.3 Define how to split documents into sections and retrieve relevant sections. — Decided. Split at Markdown headings with GitHub anchors. The record check uses the question's source section plus the top 3 keyword matches. If nothing matches, it uses the source section only. Feedback lists the sections used. The app calls the model in a fixed sequence without a tool-calling loop.

2.4 Decide how to store the API key. — Decided. The app reads the key only from the environment variable OPENAI_API_KEY_ABLATION and passes it to the client explicitly. It never reads OPENAI_API_KEY.

2.5 Add these decisions to docs/spec.md and commit. — Completed

## 3. Create the Fixed Question Bank — Completed

3.1 Write the question list, starting with the 10 questions previously discussed. — Completed. 12 questions in question_bank.md.

3.2 Link each question to its supporting source location using filename#anchor. — Completed. A question may have several locations separated by " ; ".

3.3 Verify that each source location points to the intended section. — Coding workspace, read-only — Completed

3.4 Commit. — Completed

## 4. Implement the App

Implementation takes place in the coding workspace. Implementation prompts are prepared in the planning chat.

4.1 Implement document section splitting and an anchor index.

4.2 Implement question selection using the fixed question bank and document-based generation.

4.3 Create the prompts for comparing answers with records and generating feedback.

4.4 Implement the interface.

4.5 Review each completed unit in the planning chat before committing.

## 5. Run Trial Sessions

5.1 Check the expected number of API calls.

5.2 Deliberately test answers consistent with the records, incorrect answers, and answers that exceed the claim boundaries in §12.

5.3 Review the classifications and cited source locations in the planning chat.

5.4 Compile a list of issues to fix.

## 6. Revise — Coding Workspace

6.1 Fix only the issues identified in Step 5.4.

6.2 Rerun the same inputs to check the fixes.

6.3 Commit.

## 7. Prepare the Demonstration Video

The user will not attend the final presentation. The video is how the app is shown to evaluators.

7.1 Select the demonstration sequence and questions. Include one answer consistent with the records, one incorrect answer, and one answer that exceeds a claim boundary in §12.

7.2 Record the screen.

## 8. Submit

8.1 Write the README, covering the purpose, source documents, how to run the app, limitations, and the video link.

8.2 Make the final commit and push.

8.3 Submit the repository link on the assignment registration page.