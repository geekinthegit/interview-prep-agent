# Coding-Manual Replacement and LLM–Human Agreement in Dialogue Coding

Jiwon Choi | Independent Research Project | August–September 2026

Repository: https://github.com/geekinthegit/coding-manual-ablation

## 1. Research Question and Purpose

**How does replacing specific components of a coding manual with placeholders change an LLM’s agreement with human dialogue coding?**

My proposed graduate research examines how people respond when AI suggestions agree or conflict with their prior judgments. Coding the dialogue records between participants and AI may involve LLM assistance. This raises a methodological question: How do the instructions given to the model affect its coding results?

I investigated this question using an existing human-coded dialogue corpus. The project measured changes in agreement with human labels under specified manual replacements.

## 2. Data and Experimental Design

I used TalkMoves, a mathematics classroom dialogue corpus with a coding manual and human-assigned labels. The task involved classifying teacher utterances into six instructional dialogue categories plus “Not coded.”

I sampled 300 teacher utterances randomly without replacement from the eligible development data. Each utterance was evaluated under six conditions, with three initial calls per condition, requiring 5,400 API calls in total before any tie-breaking calls. The sample size was prespecified under resource constraints. The six conditions were:

- **Full-manual baseline**
- **Definition replacement**
- **Example replacement**
- **Exclusion-rule replacement**
- **Negative control:** replacement of the theoretical-background text of section 1.1, to examine whether replacing task-irrelevant text also changed agreement
- **Names-only:** a supplementary reference in which the prompt contained no manual text

LLMs process inputs as tokens, and both input length (Levy et al., 2024) and the position of information within the input (Liu et al., 2024) can affect model performance. Deleting a manual component would change both its information content and the prompt's length, and would shift the content that follows it to earlier positions. To avoid these confounds, I replaced each component instance with a placeholder containing the same number of tokens. These placeholders consisted of "%" symbols repeated with spaces. The token count was verified for all 300 × 4 replacement inputs.

Each target utterance was marked and shown with up to seven utterances before and after it in the same transcript. This context included both teacher and student speech. The target utterance and surrounding dialogue were identical across conditions. Human labels were excluded from model inputs. The output schema allowed only one of the seven category names.

All conditions used the same dated model snapshot, GPT-5.5 (gpt-5.5-2026-04-23), to hold the model version constant across comparisons. Temperature was set to 0. Each utterance was submitted three times under each condition, and the most frequent label was selected. Ties were handled using a predefined procedure. A final label was obtained for every utterance in each of the six conditions.

## 3. Analysis and Findings

The primary outcome was unweighted Cohen’s κ against the existing human labels. The main estimate was Δκ: replacement-condition κ minus baseline κ. Uncertainty was estimated using 10,000 paired bootstrap resamples at the utterance level. Each resample retained the human label and all condition outputs for each selected utterance.

Baseline agreement was **κ = 0.6085**, with exact label agreement of **78.7%**.

| Replacement condition | Δκ | 95% confidence interval |
|---|---:|---|
| Definitions | −0.0018 | [−0.0384, 0.0360] |
| Examples | −0.0611 | [−0.1047, −0.0191] |
| Exclusion rules | −0.1062 | [−0.1576, −0.0556] |
| Negative control | −0.0232 | [−0.0581, 0.0118] |

The intervals are pointwise and were not adjusted for multiple comparisons. The names-only reference yielded κ = 0.2727.

Example and exclusion-rule replacement lowered agreement under the tested procedure. The intervals for definition replacement and the negative control included zero. These results do not establish equivalence or show that definitions are unnecessary.

## 4. Scope and Interpretation

The study identifies sensitivity to the implemented replacements. Related information remained elsewhere in the manual, and placeholder effects were not isolated. The results therefore do not establish the independent contribution of each component.

The findings concern one model configuration and the sampled TalkMoves development data. No separate held-out evaluation was conducted. TalkMoves is a public dataset, so pretraining contamination cannot be excluded. Applying LLM-assisted coding to the proposed human–AI study would require validation for its own data and coding manual.

## 5. Contributions and AI Use

**Researcher contributions:** I developed and refined the research question and study design with AI assistance. For each unit of work, I set its scope, reviewed the resulting changes before committing them, and adjudicated any audit findings. I executed the experimental API calls and determined how the results should be interpreted.

**AI assistance:** Claude (Claude Fable 5.1; Claude Opus 5.5 for part of the study) and ChatGPT (GPT-5.6 Sol; GPT-6 Astra for the statistical-analysis proposal) supported methodological discussion, decision drafting, prompt preparation and review, and interpretation review. Claude Code (Claude Fable 5.1; Claude Opus 5.5 for part of the study) and Codex (GPT-6 Astra) implemented code, executed checks and statistical analyses, and conducted cross-audits. Coding agents worked within assigned scopes and were instructed not to change research decisions or commit repository changes. The model queried in the experiment, GPT-5.5 (gpt-5.5-2026-04-23), was the object of study and not one of these tools; the tools above did not generate the experimental labels.

The repository preserves the code, decision documents, and execution and scoring records. It also documents the AI tools used, their instructions, and the division of work.

## References

Levy, M., Jacoby, A., & Goldberg, Y. (2024). Same task, more tokens: The impact of input length on the reasoning performance of large language models. Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics.

Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). Lost in the middle: How language models use long contexts. Transactions of the Association for Computational Linguistics, 12, 157–173.
