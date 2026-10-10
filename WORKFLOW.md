# Development Workflow

This workflow is a revisable work plan. If changes are needed, propose them with reasons and identify the affected steps. Update the plan after the user approves.

Follow AGENTS.md throughout all work. Keep unresolved decisions open until the user explicitly approves them.

## 0. Repository Setup — Completed

0.1 Create a new repository and connect it to GitHub.

0.2 Copy the research documents and project introduction into source_docs/. Record the source commit in SOURCE.txt.

0.3 Make the initial commit and push. — Jiwon

## 1. Define the Functional Scope — Planning Chat

1.1 Confirm the interview flow: scope selection → question → answer → comparison with records → feedback → follow-up question → session summary.

1.2 Decide the unresolved settings: number of follow-up questions per main question, proportion of fixed and generated questions, and whether to provide feedback after each answer or at the end.

1.3 Define the answer classification criteria: consistent with the records / inconsistent with the records / not found in the records. Decide how to apply the claim boundaries in §12.

1.4 Finalize the list of input documents.

1.5 Write docs/spec.md and commit. — Jiwon

## 2. Select the Technology — Planning Chat

2.1 Choose the LLM API and model.

2.2 Choose the interface: a Streamlit web interface or a terminal interface.

2.3 Define how to split documents into sections and retrieve relevant sections.

2.4 Decide how to store the API key.

2.5 Add these decisions to docs/spec.md and commit. — Jiwon

## 3. Create the Fixed Question Bank

3.1 Write the question list, starting with the 10 questions previously discussed. — Jiwon

3.2 Link each question to its supporting source location using filename#anchor. — Jiwon

3.3 Verify that each source location points to the intended section. — Coding workspace, read-only

3.4 Commit. — Jiwon

## 4. Implement the App

Implementation takes place in the coding workspace. Implementation prompts are prepared in the planning chat.

4.1 Implement document section splitting and an anchor index.

4.2 Implement question selection using the fixed question bank and document-based generation.

4.3 Create the prompts for comparing answers with records and generating feedback.

4.4 Implement the interface.

4.5 Review each completed unit in the planning chat before committing. — Jiwon

## 5. Run Trial Sessions — Jiwon

5.1 Check the expected number of API calls.

5.2 Deliberately test answers consistent with the records, incorrect answers, and answers that exceed the claim boundaries in §12.

5.3 Review the classifications and cited source locations in the planning chat.

5.4 Compile a list of issues to fix.

## 6. Revise — Coding Workspace

6.1 Fix only the issues identified in Step 5.4.

6.2 Rerun the same inputs to check the fixes. — Jiwon

6.3 Commit. — Jiwon

## 7. Submit

7.1 Write the README, covering the purpose, source documents, how to run the app, and limitations.

7.2 Make the final commit and push. — Jiwon

7.3 Submit the repository link on the assignment registration page. — Jiwon

## 8. Prepare the Presentation

8.1 Create the presentation materials.

8.2 Select the demonstration sequence and questions.

8.3 Rehearse the demonstration. — Jiwon