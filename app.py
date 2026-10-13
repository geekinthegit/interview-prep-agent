"""Interview practice agent — Streamlit chat interface (docs/spec.md).

Run from the repository root:  streamlit run app.py

Model requests are made only inside the callback of a user action (an answer
submitted, "Next question" for a generated question, or "Retry"). Every
received response is stored in st.session_state, and reruns only render the
stored state, so a stored response is never requested again.
"""

from __future__ import annotations

import random

import streamlit as st

from prep_agent import llm, session
from prep_agent.prompts import CONSISTENT, INCONSISTENT, NOT_IN_RECORD
from prep_agent.questions import (
    BOUNDARY_SECTION_ANCHOR, SCORING_RECORD_PATH, fixed_questions_in_scope,
    load_boundaries, load_question_bank, pick_generation_section,
)
from prep_agent.retrieval import KeywordIndex
from prep_agent.sections import build_index, document_paths, index_by_location

ALL_DOCUMENTS = "All documents"
MODE_FIXED = "Fixed questions only"
MODE_BOTH = "Fixed and generated questions"
LABEL_ICONS = {CONSISTENT: "✅", INCONSISTENT: "❌", NOT_IN_RECORD: "❔"}


@st.cache_resource
def load_resources():
    sections = build_index()
    return {
        "sections": sections,
        "by_location": index_by_location(sections),
        "keywords": KeywordIndex(sections),
        "questions": load_question_bank(),
        "boundaries": load_boundaries(sections),
        "documents": document_paths(),
    }


R = load_resources()
BOUNDARY_IDS = [b.bid for b in R["boundaries"]]
BOUNDARY_LOCATIONS = {b.bid: b.location for b in R["boundaries"]}
BOUNDARY_TEXT = {b.bid: b.text for b in R["boundaries"]}
ss = st.session_state


def reset_state():
    for key in list(ss.keys()):
        del ss[key]
    ss.stage = "setup"
    ss.api_calls = 0
    ss.call_log = []
    ss.turns = []
    ss.generation = None  # pending or failed question generation
    ss.notice = None
    ss.used_generation_sections = []
    ss.rng = random.Random()


if "stage" not in ss:
    reset_state()

# A request that was still pending when this run started was cut off by a rerun
# before its response was stored. It is not re-sent automatically.
for turn in ss.turns:
    for ex in turn["exchanges"]:
        if ex["status"] == "pending":
            ex["status"] = "interrupted"
            ex["error"] = "The request was interrupted before a response was stored."
if ss.generation and ss.generation["status"] == "pending":
    ss.generation["status"] = "interrupted"
    ss.generation["error"] = "The request was interrupted before a response was stored."


# --- Model calls -----------------------------------------------------------

def counted_call(purpose: str, func, *args, **kwargs):
    """Send one request. Raises MissingKeyError before counting if no key is set."""
    client = llm.make_client()
    ss.api_calls += 1
    entry = {"n": ss.api_calls, "purpose": purpose, "status": "sent"}
    ss.call_log.append(entry)
    try:
        result = func(client, *args, **kwargs)
    except Exception:
        entry["status"] = "error"
        raise
    entry["status"] = "ok"
    return result


def run_check(turn: dict, ex: dict):
    allow_follow_up = ex["role"] == "main"
    ctx = ex["context"]
    sources = [R["by_location"][l] for l in ctx["source_sections"]]
    retrieved = [R["by_location"][l] for l in ctx["retrieved_sections"]]
    if not sources and not retrieved:
        ex["status"] = "no_sections"
        ex["error"] = "No source section was found for this question, so the answer was not checked."
        turn["phase"] = "done"
        return
    ex["status"] = "pending"
    try:
        result = counted_call(
            f"Record check ({turn['question']['qid']}, {ex['role']})",
            llm.check_answer, ex["question"], ex["answer"], sources, retrieved,
            R["boundaries"], allow_follow_up,
        )
    except llm.MissingKeyError as e:
        ex["status"], ex["error"] = "error", f"{e} No request was sent."
        return
    except Exception as e:  # noqa: BLE001 - shown to the user as is
        ex["status"], ex["error"] = "error", f"{type(e).__name__}: {e}"
        return
    output = result["output"]
    allowed = ctx["source_sections"] + ctx["retrieved_sections"]
    ex.update(status="done", output=output, response_id=result["response_id"],
              problems=session.validate_check_output(output, allowed, BOUNDARY_IDS))
    if allow_follow_up and output.get("follow_up_question"):
        follow_sources = [l for l in output.get("follow_up_source_locations", []) if l in allowed]
        turn["follow_up"] = {
            "question": output["follow_up_question"],
            "sources": follow_sources or ctx["source_sections"],
        }
        turn["phase"] = "follow_up"
    else:
        turn["phase"] = "done"


def submit_answer(answer: str):
    turn = ss.turns[-1]
    if turn["phase"] == "answer":
        role, question, sources = "main", turn["question"]["text"], turn["question"]["sources"]
    else:
        role, question, sources = "follow_up", turn["follow_up"]["question"], turn["follow_up"]["sources"]
    ex = {
        "role": role, "question": question, "answer": answer,
        "context": session.build_check_context(sources, answer, R["by_location"], R["keywords"]),
        "status": "new", "output": None, "problems": [], "error": None,
    }
    turn["exchanges"].append(ex)
    run_check(turn, ex)


def asked_ids() -> set[str]:
    return {t["question"]["qid"] for t in ss.turns}


def next_question_kind() -> str | None:
    fixed_left = [q for q in ss.fixed_pool if q.qid not in asked_ids()]
    if ss.mode == MODE_FIXED:
        return "fixed" if fixed_left else None
    n_fixed = sum(t["question"]["kind"] == "fixed" for t in ss.turns)
    n_generated = len(ss.turns) - n_fixed
    if fixed_left and n_fixed <= n_generated:
        return "fixed"
    return "generated"


def start_turn(question: dict):
    ss.turns.append({"question": question, "exchanges": [], "follow_up": None, "phase": "answer"})


def run_generation(section_location: str):
    section = R["by_location"][section_location]
    ss.generation = {"section": section_location, "status": "pending", "error": None}
    try:
        result = counted_call(f"Question generation ({section_location})",
                              llm.generate_question, section)
    except llm.MissingKeyError as e:
        ss.generation.update(status="error", error=f"{e} No request was sent.")
        return
    except Exception as e:  # noqa: BLE001
        ss.generation.update(status="error", error=f"{type(e).__name__}: {e}")
        return
    ss.used_generation_sections.append(section_location)
    ss.generation = None
    output = result["output"]
    if not output.get("question"):
        ss.notice = (f"No question could be generated from `{section_location}`: "
                     f"{output.get('reason_if_null') or 'no reason given'}")
        return
    n = sum(t["question"]["kind"] == "generated" for t in ss.turns) + 1
    start_turn({"qid": f"G{n}", "text": output["question"], "sources": [section_location],
                "kind": "generated"})


def next_question():
    ss.notice = None
    kind = next_question_kind()
    if kind is None:
        ss.notice = "There are no more fixed questions in this scope. End the session to see the summary."
        return
    if kind == "fixed":
        q = next(q for q in ss.fixed_pool if q.qid not in asked_ids())
        start_turn({"qid": q.qid, "text": q.text, "sources": q.sources, "kind": "fixed"})
        return
    exclude = set(ss.used_generation_sections)
    for t in ss.turns:
        exclude.update(t["question"]["sources"])
    section = pick_generation_section(R["sections"], ss.scope, exclude, ss.rng)
    if section is None:
        ss.notice = "No section in this scope is left to generate a question from."
        return
    run_generation(section.location)


def on_answer_submitted():
    answer = (ss.get("answer_input") or "").strip()
    if answer:
        submit_answer(answer)


def skip_follow_up():
    ss.turns[-1]["phase"] = "done"


def start_session():
    scope = ss.setup_scope
    ss.scope = None if scope == ALL_DOCUMENTS else scope
    ss.mode = ss.setup_mode
    ss.fixed_pool = fixed_questions_in_scope(R["questions"], ss.scope)
    ss.stage = "session"


def end_session():
    ss.stage = "summary"


# --- Rendering -------------------------------------------------------------

def render_context(ex: dict):
    ctx = ex["context"]
    lines = ["**Sections used for the check**"]
    lines += [f"- `{l}` (question source)" for l in ctx["source_sections"]]
    lines += [f"- `{l}` (keyword match)" for l in ctx["retrieved_sections"]]
    if not ctx["retrieved_sections"]:
        lines.append("- No other section matched the answer by keyword; only the question's source sections were used.")
    for l in ctx["missing_sources"]:
        lines.append(f"- Source section not found in the section index: `{l}`")
    if BOUNDARY_IDS:
        lines.append(f"\n**Claim boundary statements checked:** {', '.join(BOUNDARY_IDS)} "
                     f"(`{SCORING_RECORD_PATH}#{BOUNDARY_SECTION_ANCHOR}`)")
    else:
        lines.append("\n**Claim boundary statements:** not found in the section index.")
    st.markdown("\n".join(lines))


def render_exchange_result(turn: dict, ex: dict, key: str):
    if ex["status"] == "no_sections":
        st.warning(ex["error"])
        render_context(ex)
        return
    if ex["status"] in ("error", "interrupted"):
        st.error(ex["error"])
        st.button("Retry (sends 1 request)", key=f"retry-{key}", on_click=run_check, args=(turn, ex))
        return
    output = ex["output"]
    claims = output.get("claims", [])
    st.markdown("**Claims**" if claims else "**Claims:** no checkable claim was found in the answer.")
    for i, c in enumerate(claims, start=1):
        locs = c.get("source_locations") or []
        loc_text = ", ".join(f"`{l}`" for l in locs) if locs else "no source section found in the checked sections"
        text = (f"{i}. {LABEL_ICONS.get(c.get('label'), '')} **{c.get('label')}** — {c.get('claim')}\n"
                f"   - Source: {loc_text}\n")
        bid = c.get("boundary_id")
        if bid:
            text += f"   - Claim boundary {bid}: {BOUNDARY_TEXT.get(bid, 'identifier not found in section 12')}\n"
        text += f"   - {c.get('explanation')}"
        st.markdown(text)
    st.markdown(f"**Feedback**\n\n{output.get('feedback', '')}")
    render_context(ex)
    if ex["problems"]:
        st.warning("Output check:\n" + "\n".join(f"- {p}" for p in ex["problems"]))


def render_turn(t_index: int, turn: dict):
    q = turn["question"]
    with st.chat_message("assistant"):
        st.markdown(f"**{q['qid']}.** {q['text']}")
    for e_index, ex in enumerate(turn["exchanges"]):
        if ex["role"] == "follow_up":
            with st.chat_message("assistant"):
                st.markdown(f"**Follow-up.** {ex['question']}")
        with st.chat_message("user"):
            st.markdown(ex["answer"])
        with st.chat_message("assistant"):
            if ex["role"] == "main":
                st.caption("Question source: " + (", ".join(f"`{s}`" for s in q["sources"]) or "none"))
            else:
                st.caption("Follow-up source: " + ", ".join(f"`{s}`" for s in turn["follow_up"]["sources"]))
            render_exchange_result(turn, ex, f"{t_index}-{e_index}")
    if turn["phase"] == "follow_up":
        with st.chat_message("assistant"):
            st.markdown(f"**Follow-up.** {turn['follow_up']['question']}")


def render_sidebar():
    with st.sidebar:
        st.metric("API calls this session", ss.api_calls)
        if ss.stage != "setup":
            st.caption(f"Scope: {ss.scope or ALL_DOCUMENTS}")
            st.caption(f"Questions: {ss.mode}")
        if not llm.api_key_available():
            st.warning(f"{llm.API_KEY_ENV} is not set. Answers cannot be checked.")
        if ss.call_log:
            with st.expander("Request log"):
                for entry in ss.call_log:
                    st.caption(f"{entry['n']}. {entry['purpose']} — {entry['status']}")
        if ss.stage == "session":
            st.button("End session", on_click=end_session)


def setup_screen():
    st.title("Interview practice: coding-manual-ablation")
    scope = st.radio("Documents", [ALL_DOCUMENTS] + R["documents"], key="setup_scope")
    st.radio("Questions", [MODE_FIXED, MODE_BOTH], key="setup_mode")
    scope_value = None if scope == ALL_DOCUMENTS else scope
    pool = fixed_questions_in_scope(R["questions"], scope_value)
    st.caption(f"Fixed questions in this scope: {len(pool)}")
    st.button("Start session", type="primary", on_click=start_session)


def session_screen():
    st.title("Interview practice")
    for t_index, turn in enumerate(ss.turns):
        render_turn(t_index, turn)
    if ss.generation and ss.generation["status"] in ("error", "interrupted"):
        st.error(f"Question generation failed for `{ss.generation['section']}`: {ss.generation['error']}")
        st.button("Retry question generation (sends 1 request)",
                  on_click=run_generation, args=(ss.generation["section"],))
        return
    if ss.notice:
        st.info(ss.notice)
    turn = ss.turns[-1] if ss.turns else None
    if turn is None or turn["phase"] == "done":
        st.button("Next question", type="primary", on_click=next_question)
        return
    if turn["phase"] == "follow_up":
        st.button("Skip follow-up", on_click=skip_follow_up)
    last = turn["exchanges"][-1] if turn["exchanges"] else None
    if last is not None and last["status"] in ("error", "interrupted") and (
            (turn["phase"] == "answer" and last["role"] == "main")
            or (turn["phase"] == "follow_up" and last["role"] == "follow_up")):
        return  # waiting for Retry on the failed check
    st.chat_input("Your answer", key="answer_input", on_submit=on_answer_submitted)


def summary_screen():
    st.title("Session summary")
    st.caption(f"API calls this session: {ss.api_calls}")
    exchanges = []
    for turn in ss.turns:
        q = turn["question"]
        st.markdown(f"### {q['qid']}. {q['text']}")
        st.caption("Source: " + ", ".join(f"`{s}`" for s in q["sources"]))
        if not turn["exchanges"]:
            st.markdown("- Not answered.")
        for ex in turn["exchanges"]:
            exchanges.append(ex)
            prefix = "Answer" if ex["role"] == "main" else f"Follow-up ({ex['question']})"
            if ex["output"] is None:
                st.markdown(f"- {prefix}: not checked ({ex['status']}).")
                continue
            labels = [c.get("label") for c in ex["output"].get("claims", [])]
            counts = session.label_counts(ex["output"])
            detail = "; ".join(f"{LABEL_ICONS[l]} {l}: {n}" for l, n in counts.items())
            st.markdown(f"- {prefix}: {len(labels)} claim(s) — {detail}")
            for i, label in enumerate(labels, start=1):
                st.markdown(f"  - Claim {i}: {label}")
    st.markdown("### Sections to reread")
    reread = session.sections_to_reread(exchanges, BOUNDARY_LOCATIONS)
    st.markdown("\n".join(f"- `{l}`" for l in reread) if reread else "- None.")
    st.button("Start a new session", on_click=reset_state)


render_sidebar()
if ss.stage == "setup":
    setup_screen()
elif ss.stage == "session":
    session_screen()
else:
    summary_screen()
