# Question Bank

| ID | Question | Source |
|---|---|---|
| Q01 | Why did you sample 300 utterances? | source_docs/decisions/02-3-sampling-design.md#235-sample-size-rationale |
| Q02 | Why did you not use stratified sampling? | source_docs/decisions/02-3-sampling-design.md#233-alternative-considered-disproportionate-stratification-without-population-weighting ; source_docs/decisions/02-3-sampling-design.md#234-alternative-considered-disproportionate-stratification-with-population-standardization |
| Q03 | How did you handle the rare categories? | source_docs/decisions/02-3-sampling-design.md#236-rare-category-representation-and-scope-of-inference ; source_docs/decisions/02-3-sampling-design.md#238-limitation-of-the-sampling-design |
| Q04 | Why did you not run the held-out evaluation? | source_docs/docs/research-workflow.md#stage-2-develop-and-validate-the-computational-instrument ; source_docs/reports/heldout-evaluation-decision-2026-09-24.md#decision |
| Q05 | How could prior model exposure to TalkMoves affect your results? | source_docs/decisions/02-2-development-and-held-out-sets.md#224-prior-model-exposure-and-direction-of-bias |
| Q06 | Why did you include the names-only condition? | source_docs/decisions/03-1-manual-component-definition.md#316-selection-of-replacement-targets ; source_docs/decisions/03-3-names-only-diagnostic.md#33-names-only-reference |
| Q07 | Why did you replace components with placeholders instead of deleting them? | source_docs/decisions/03-2-placeholder-specification.md#321-purpose-and-scope-of-placeholder-replacement |
| Q08 | How is this study related to few-shot prompting? | source_docs/decisions/03-1-manual-component-definition.md#318-assignment-rulings |
| Q09 | Why did you choose the TalkMoves dataset? | source_docs/decisions/02-1-dataset-selection-and-scope.md#211-dataset-selection ; source_docs/decisions/01-research-question.md#123-position-of-the-study |
| Q10 | What did you do yourself and what did the AI tools do? | source_docs/AI_WORKFLOW.md#2-division-of-work |
| Q11 | Why did you use a paired bootstrap for Δκ, and how were the resamples drawn? | source_docs/decisions/06-analysis.md#621-bootstrap-specification ; source_docs/decisions/02-3-sampling-design.md#237-paired-resampling-for-uncertainty-estimation |
| Q12 | Why did you resample utterances rather than transcripts? | source_docs/decisions/02-3-sampling-design.md#237-paired-resampling-for-uncertainty-estimation ; source_docs/decisions/06-analysis.md#63-non-independence-and-uncertainty-interpretation |