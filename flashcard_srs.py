"""
Vocab Master — Flashcards, Spaced Repetition & Quiz
====================================================
Owner: [JOSEPH EKUMA]  |  Branch: feature/joseph
Covers: Tabs 2-4 of the app (Review, Quiz, Stats) + flashcards.json / scores.json
also delete word and download png
"""

import streamlit as st
import json
import re
import random
import os
from datetime import datetime, timedelta
from io import BytesIO
import matplotlib.pyplot as plt


DATA_FOLDER = "data"
FLASHCARDS_FILE = os.path.join(DATA_FOLDER, "flashcards.json")
SCORES_FILE = os.path.join(DATA_FOLDER, "scores.json")
WORDS_FILE = os.path.join(DATA_FOLDER, "saved_words.json")
os.makedirs(DATA_FOLDER, exist_ok=True)


# ===== FILE HANDLING =====
def load_json(file, default):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return default


def save_json(file, data):
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving file: {e}")


# ===== OOP CLASSES =====
class Flashcard:
    """Flashcard with Spaced Repetition fields: SM-2 algorithm"""
    def __init__(self, word, back, interval=1, repetitions=0, ef=2.5, next_review=None):
        self.word = word
        self.back = back
        self.interval = interval
        self.repetitions = repetitions
        self.ef = ef
        self.next_review = next_review or datetime.now().date().isoformat()

    @property
    def front(self):
        # "front" of the card is just the word itself - derived, not stored,
        # so it never gets written to JSON and never breaks from_dict()
        return self.word

    @classmethod
    def from_word(cls, word_obj):
        back = (
            f"**Simple:** {word_obj.simple_explanation}\n\n"
            f"**Example:** {word_obj.ai_example}\n\n"
            f"**Trick:** {word_obj.memory_trick}\n\n"
            f"**Synonym:** {', '.join(word_obj.synonyms)}\n\n"
            f"**Antonym:** {', '.join(word_obj.antonyms)}"
        )
        return cls(word=word_obj.word, back=back)

    @classmethod
    def from_dict(cls, d):
        # Ignore any legacy/unexpected keys (e.g. old saved "front" field)
        allowed = {"word", "back", "interval", "repetitions", "ef", "next_review"}
        clean_d = {k: v for k, v in d.items() if k in allowed}
        return cls(**clean_d)

    def to_dict(self):
        return {
            "word": self.word,
            "back": self.back,
            "interval": self.interval,
            "repetitions": self.repetitions,
            "ef": self.ef,
            "next_review": self.next_review,
        }


class SpacedRepetitionManager:
    """SM-2 Spaced Repetition Algorithm."""

  
    def update_card(self, card, quality):  # quality 0-5
        if quality < 3:
            card.repetitions = 0
            card.interval = 1
        else:
            card.repetitions += 1
            if card.repetitions == 1:
                card.interval = 1
            elif card.repetitions == 2:
                card.interval = 6
            else:
                card.interval = round(card.interval * card.ef)
            card.ef = max(1.3, card.ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

        next_date = datetime.now().date() + timedelta(days=card.interval)
        card.next_review = next_date.isoformat()
        return card

    def get_due_cards(self, flashcards):
        today = datetime.now().date().isoformat()
        return [c for c in flashcards if c.next_review <= today]


class QuizGenerator:
    """Generates objective (multiple-choice) quizzes from saved words —
    1 correct definition + 2 distractors, 3 options total."""

    def generate_mcq(self, word_obj, all_words):
        """Objective question: 1 correct definition + 2 distractors = 3 options."""
        correct_def = word_obj.meanings[0]['definition'] if word_obj.meanings else ""
        wrong_defs = [
            w['meanings'][0]['definition']
            for w in all_words
            if w['word'] != word_obj.word and w['meanings']
        ]

        options = [correct_def]
        if len(wrong_defs) >= 2:
            options += random.sample(wrong_defs, 2)
        else:
            options += ["Distractor 1", "Distractor 2"][:2 - len(wrong_defs)]
        random.shuffle(options)

        return {
            "type": "mcq",
            "question": f"What is the meaning of '{word_obj.word}'?",
            "options": options,
            "answer": correct_def,
        }

    def generate(self, word_obj, all_words, flashcard=None):
        return self.generate_mcq(word_obj, all_words)


# ===== STREAMLIT UI: TAB 2 - FLASHCARD REVIEW + DELETE =====
def render_flashcard_tab(flashcards, saved_words, srs):
    """Renders Tab 2. Returns the (possibly updated) flashcards list, since
    scoring and deleting both mutate it."""
    st.header("Review Flashcards")
    due_cards = srs.get_due_cards(flashcards)
    st.write(f"**Cards due for review:** {len(due_cards)}")

    if due_cards:
        if st.session_state["current_due_card_front"] not in [c.front for c in due_cards]:
            st.session_state["current_due_card_front"] = random.choice(due_cards).front
        card = next(c for c in due_cards if c.front == st.session_state["current_due_card_front"])
        st.subheader(f"Flashcard: {card.front}")
        if st.button("Show Answer"):
            st.write(card.back)
        st.write("How well did you remember?")
        cols = st.columns(4)
        for i, q in enumerate([0, 2, 4, 5]):
            if cols[i].button(f"Score: {q}", key=f"score{q}"):
                updated = srs.update_card(card, q)
                flashcards = [updated if c.front == card.front else c for c in flashcards]
                save_json(FLASHCARDS_FILE, [c.to_dict() for c in flashcards])
                st.session_state["current_due_card_front"] = None
                st.rerun()
    else:
        st.info("No cards due. Add more words!")

    # ----- Delete-a-word block -----
    st.divider()
    with st.expander("🗑️ Manage saved words"):
        if not flashcards:
            st.caption("No saved words yet.")
        else:
            word_to_delete = st.selectbox(
                "Pick a word to remove from your flashcards",
                sorted(c.word for c in flashcards),
                key="delete_word_select",
            )
            if st.button("Delete word", type="primary"):
                flashcards = [c for c in flashcards if c.word != word_to_delete]
                saved_words[:] = [w for w in saved_words if w['word'] != word_to_delete]
                save_json(FLASHCARDS_FILE, [c.to_dict() for c in flashcards])
                save_json(WORDS_FILE, saved_words)
                if st.session_state.get("current_due_card_front") == word_to_delete:
                    st.session_state["current_due_card_front"] = None
                st.success(f"'{word_to_delete}' removed.")
                st.rerun()

    return flashcards


# ===== STREAMLIT UI: TAB 3 - QUIZ (MCQ + Fill-in-the-blank) =====
def render_quiz_tab(flashcards, saved_words, scores):
    st.header("Take a Quiz")
    if len(saved_words) < 4:
        st.info("Save at least 4 words first to take a quiz")
        return

    if st.session_state["current_quiz"] is None:
        w_card = random.choice(flashcards)
        w_data = next((x for x in saved_words if x['word'] == w_card.word), None)
        if w_data:
            word_obj = type('obj', (object,), w_data)
            st.session_state["current_quiz"] = QuizGenerator().generate(
                word_obj, saved_words, flashcard=w_card
            )

    q = st.session_state["current_quiz"]
    if not q:
        return

    st.subheader(q["question"])
    choice = st.radio("Choose the correct option:", q["options"], key="quiz_mcq")
    if st.button("Submit Answer"):
        score_val = 1 if choice == q["answer"] else 0
        scores.append({
            "date": datetime.now().isoformat(),
            "score": score_val,
            "word": q["question"],
            "type": q["type"],
        })
        save_json(SCORES_FILE, scores)
        if score_val:
            st.success("Correct! 🎉")
        else:
            st.error(f"Wrong. Answer: {q['answer']}")
        st.session_state["current_quiz"] = None
        st.rerun()


# ===== STREAMLIT UI: TAB 4 - STATS DASHBOARD =====
def render_stats_tab(saved_words, scores):
    st.header("Your Progress")

    total_words = len(saved_words)
    total_quizzes = len(scores)
    accuracy = (sum(s['score'] for s in scores) / len(scores) * 100) if scores else 0.0

    st.metric("Total Words Saved", total_words)
    st.metric("Total Quizzes Taken", total_quizzes)
    if scores:
        st.metric("Overall Accuracy", f"{accuracy:.1f}%")

    # Running accuracy after each quiz attempt, in order taken.
    running_correct = 0
    chart_values = []
    for i, s in enumerate(scores, start=1):
        running_correct += s['score']
        chart_values.append(running_correct / i * 100)

    st.subheader("Accuracy over time")

    # Built with matplotlib (not st.line_chart)  
    fig, ax = plt.subplots(figsize=(8, 4))
    if chart_values:
        ax.plot(range(1, len(chart_values) + 1), chart_values, marker="o", color="#4C78A8")
    ax.set_ylim(0, 100)
    ax.set_xlabel("Quiz attempt #")
    ax.set_ylabel("Running accuracy (%)")
    ax.set_title("Vocab Master — Stats")
    ax.grid(True, alpha=0.3)

    # Fold the summary metrics into the same figure so the PNG download
    # captures "everything displayed on stats", not just the chart.
    summary = f"Words saved: {total_words}   |   Quizzes taken: {total_quizzes}   |   Overall accuracy: {accuracy:.1f}%"
    fig.text(0.5, -0.02, summary, ha="center", fontsize=9, color="#444444")

    if chart_values:
        st.pyplot(fig)
        st.caption("Running accuracy (%) after each quiz question, in order taken.")
    else:
        st.caption("Take a few quizzes to see your accuracy trend here.")

    # ----- PNG export button -----
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    buf.seek(0)
    st.download_button(
        "📥 Save stats as PNG",
        data=buf,
        file_name="vocab_master_stats.png",
        mime="image/png",
    )
    plt.close(fig)

    st.write("All data is stored locally in the `data` folder as JSON files.")


# ===== STANDALONE DEMO (for testing this branch without Tab 1) =====
def run_demo():
    """`streamlit run flashcards_srs.py` — exercises Tabs 2-4 with a couple
    of seeded fake words, so this part can be tested/tuned independently
    before merging with the Search & AI branch."""
    st.set_page_config(page_title="Vocab Master (my part - demo)", layout="wide")
    st.title("🃏 Flashcards, SRS & Quiz — standalone demo")

    srs = SpacedRepetitionManager()
    flashcards = [Flashcard.from_dict(c) for c in load_json(FLASHCARDS_FILE, [])]
    saved_words = load_json(WORDS_FILE, [])
    scores = load_json(SCORES_FILE, [])

    if not flashcards:
        seed_words = [
            {
                "word": "ephemeral", "phonetics": "/ɪˈfɛm(ə)rəl/",
                "meanings": [{"definition": "Lasting for a very short time.",
                              "example": "", "synonyms": ["fleeting", "transient"], "antonyms": ["permanent"]}],
            },
            {
                "word": "resilient", "phonetics": "/rɪˈzɪliənt/",
                "meanings": [{"definition": "Able to recover quickly from difficulties.",
                              "example": "", "synonyms": ["tough", "hardy"], "antonyms": ["fragile"]}],
            },
            {
                "word": "meticulous", "phonetics": "/mɪˈtɪkjʊləs/",
                "meanings": [{"definition": "Showing great attention to detail.",
                              "example": "", "synonyms": ["careful", "precise"], "antonyms": ["careless"]}],
            },
            {
                "word": "candid", "phonetics": "/ˈkandɪd/",
                "meanings": [{"definition": "Truthful and straightforward.",
                              "example": "", "synonyms": ["frank", "honest"], "antonyms": ["evasive"]}],
            },
        ]
        for w in seed_words:
            saved_words.append(w)
            fake_word_obj = type('obj', (object,), {
                "word": w["word"],
                "simple_explanation": w["meanings"][0]["definition"],
                "ai_example": f"The scientist was {w['word']} in her approach.",
                "memory_trick": f"Think of '{w['word']}' and picture it clearly.",
                "synonyms": w["meanings"][0]["synonyms"],
                "antonyms": w["meanings"][0]["antonyms"],
            })
            flashcards.append(Flashcard.from_word(fake_word_obj))
        save_json(WORDS_FILE, saved_words)
        save_json(FLASHCARDS_FILE, [c.to_dict() for c in flashcards])

    for key in ["current_due_card_front", "current_quiz"]:
        st.session_state.setdefault(key, None)

    tab2, tab3, tab4 = st.tabs(["🃏 Flashcards", "📝 Quiz", "📊 Stats"])
    with tab2:
        flashcards = render_flashcard_tab(flashcards, saved_words, srs)
    with tab3:
        render_quiz_tab(flashcards, saved_words, scores)
    with tab4:
        render_stats_tab(saved_words, scores)


if __name__ == "__main__":
    run_demo()