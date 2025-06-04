import streamlit as st
import json
from pathlib import Path
from dataclasses import dataclass, asdict, fields, is_dataclass
from typing import List
import pandas as pd
import random

# ========== PERSONS (used across all tenses) ==========
PERSONS = ["je", "tu", "il/elle/on", "nous", "vous", "ils/elles"]

# ========== CONJUGATION STRUCTURE ==========

@dataclass
class TenseConjugation:
    je: str
    tu: str
    il_elle_on: str
    nous: str
    vous: str
    ils_elles: str

@dataclass
class VerbConjugations:
    present: TenseConjugation
    imparfait: TenseConjugation
    futur: TenseConjugation
    passe_compose: TenseConjugation
    plus_que_parfait: TenseConjugation
    futur_anterieur: TenseConjugation
    conditionnel: TenseConjugation
    conditionnel_passe: TenseConjugation
    subjonctif_present: TenseConjugation
    subjonctif_passe: TenseConjugation
    imperatif: TenseConjugation

@dataclass
class Verb:
    infinitive: str
    meaning: str
    group: str
    auxiliary: str
    conjugations: VerbConjugations

@dataclass
class Noun:
    word: str
    gender: str
    plural: str
    meaning: str

@dataclass
class Preposition:
    word: str
    meaning: str
    example: str

@dataclass
class Expression:
    phrase: str
    meaning: str
    literal: str
    example: str

# ===== UTILITIES =====

def load_data(filename, cls):
    path = Path(filename)
    if not path.exists():
        return []

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if cls == Verb:
        return [
            Verb(
                infinitive=item["infinitive"],
                meaning=item["meaning"],
                group=item["group"],
                auxiliary=item["auxiliary"],
                conjugations=VerbConjugations(
                    **{
                        k: TenseConjugation(**v)
                        for k, v in item["conjugations"].items()
                    }
                )
            )
            for item in data
        ]
    else:
        return [cls(**item) for item in data]

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([asdict(item) for item in data], f, ensure_ascii=False, indent=2)

# ===== LOAD DATA =====
verbs = load_data('data/verbs.json', Verb)
nouns = load_data('data/nouns.json', Noun)
prepositions = load_data('data/prepositions.json', Preposition)
expressions = load_data('data/expressions.json', Expression)

# ===== SIDEBAR NAVIGATION =====
st.sidebar.title("📚 French Vocab App")
page = st.sidebar.radio("Navigate", ["Verbs", "Nouns", "Prepositions", "Expressions", "Flip Cards", "Verb Meaning Quiz"])

# ===== DISPLAY HELPERS =====

def display_verb(v: Verb):
    st.subheader(f"🔤 {v.infinitive} — {v.meaning}")
    st.text(f"Group: {v.group} | Auxiliary: {v.auxiliary}")

    if is_dataclass(v.conjugations):
        for field in fields(type(v.conjugations)):
            tense_name = field.name
            conjugation = getattr(v.conjugations, tense_name)

            st.markdown(f"#### {tense_name.replace('_', ' ').title()}")

            df = pd.DataFrame.from_dict({
                "Person": ["je", "tu", "il/elle/on", "nous", "vous", "ils/elles"],
                "Conjugation": [
                    conjugation.je,
                    conjugation.tu,
                    conjugation.il_elle_on,
                    conjugation.nous,
                    conjugation.vous,
                    conjugation.ils_elles
                ]
            })

            st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.warning("Conjugations not properly loaded.")

def display_noun(n: Noun):
    st.subheader(f"📙 {n.word} — {n.meaning}")
    st.text(f"Gender: {n.gender} | Plural: {n.plural}")

def display_preposition(p: Preposition):
    st.subheader(f"📌 {p.word} — {p.meaning}")
    st.markdown(f"**Example:** {p.example}")

def display_expression(e: Expression):
    st.subheader(f"💬 {e.phrase} — {e.meaning}")
    st.markdown(f"**Literal:** {e.literal}<br>**Example:** {e.example}", unsafe_allow_html=True)

# ===== PAGE VIEWS =====

def show_item_list(items, display_fn, label_fn):
    names = [label_fn(item) for item in items]
    choice = st.selectbox("Select an item to view details:", names)
    if choice:
        item = next(i for i in items if label_fn(i) == choice)
        display_fn(item)

def label_verb(v: Verb):
    return f"{v.infinitive} ({v.meaning})"

def label_noun(n: Noun):
    return f"{n.word} ({n.meaning})"

def label_prep(p: Preposition):
    return f"{p.word} ({p.meaning})"

def label_expr(e: Expression):
    return f"{e.phrase} ({e.meaning})"

if page == "Verbs":
    st.title("🔤 Verbs")
    show_item_list(verbs, display_verb, label_verb)

elif page == "Nouns":
    st.title("📙 Nouns")
    show_item_list(nouns, display_noun, label_noun)

elif page == "Prepositions":
    st.title("📌 Prepositions")
    show_item_list(prepositions, display_preposition, label_prep)

elif page == "Expressions":
    st.title("💬 Expressions")
    show_item_list(expressions, display_expression, label_expr)

elif page == "Flip Cards":
    st.title("🎴 Flip Cards — Verb Practice")

    if not verbs:
        st.info("No verbs loaded.")
    else:
        if "current_card" not in st.session_state:
            st.session_state.current_card = {
                "verb": random.choice(verbs),
                "tense": random.choice(fields(VerbConjugations)).name,
                "person": random.choice(PERSONS),
                "revealed": False,
            }

        card = st.session_state.current_card
        verb = card["verb"]
        tense = card["tense"]
        person = card["person"]
        revealed = card["revealed"]

        st.markdown(f"""
        ### ❓ Conjugate au **_{tense.replace('_', ' ').title()}_**
        🧠 **{person}** + <span style='color:#2b90d9; font-weight:bold;'>{verb.infinitive}</span> (*{verb.meaning}*)
        """, unsafe_allow_html=True)

        if not revealed:
            if st.button("Reveal Answer", key="reveal_btn"):
                st.session_state.current_card["revealed"] = True
                st.rerun()  # Force immediate refresh to show answer
        else:
            tense_conj = getattr(verb.conjugations, tense)
            key = person.replace("il/elle/on", "il_elle_on").replace("ils/elles", "ils_elles")
            answer = getattr(tense_conj, key)
            st.success(f"✅ {person} **{answer}**")

            if st.button("Next", key="next_btn"):
                st.session_state.current_card = {
                    "verb": random.choice(verbs),
                    "tense": random.choice(fields(VerbConjugations)).name,
                    "person": random.choice(PERSONS),
                    "revealed": False,
                }
                st.rerun()

elif page == "Verb Meaning Quiz":
    st.title("📝 Verb Meaning Quiz")

    if not verbs:
        st.info("No verbs loaded.")
    else:
        if "quiz_card" not in st.session_state:
            correct = random.choice(verbs)
            choices = random.sample([v for v in verbs if v != correct], k=3)
            options = choices + [correct]
            random.shuffle(options)
            st.session_state.quiz_card = {
                "verb": correct,
                "options": options,
                "answered": False,
                "selected": None
            }

        card = st.session_state.quiz_card
        verb = card["verb"]
        options = card["options"]

        st.markdown(
            f"### ❓ What does the verb <span style='color:#1f77b4; font-weight:600'>{verb.infinitive}</span> mean?",
            unsafe_allow_html=True
        )

        cols = st.columns(2)
        for i, opt in enumerate(options):
            key_base = f"verb_quiz_btn_{opt.infinitive}"

            with cols[i % 2]:
                if not card["answered"]:
                    if st.button(opt.meaning, key=key_base, use_container_width=True):
                        card["selected"] = opt.meaning
                        card["answered"] = True
                        st.rerun()
                else:
                    st.button(opt.meaning, key=f"{key_base}_disabled", disabled=True, use_container_width=True)

        if card["answered"]:
            if card["selected"] == verb.meaning:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. The correct answer was **{verb.meaning}**.")

            if st.button("Next Question"):
                del st.session_state.quiz_card
                st.rerun()

# === Run with: streamlit run vocab_app_streamlit.py ===
