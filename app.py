import streamlit as st

from search_ui import render_search_tab
from flashcard_srs import (
Flashcard,
SpacedRepetitionManager,
load_json,
render_flashcard_tab,
render_quiz_tab,
render_stats_tab,
)

st.set_page_config(
page_title="Vocabulary Master",
page_icon="📚",
layout="wide",
)

st.title("📚 Vocabulary Master")

st.write(
"Build your vocabulary, review with flashcards, "
"test your knowledge, and track your progress."
)

FLASHCARDS_FILE = "data/flashcards.json"
WORDS_FILE = "data/saved_words.json"
SCORES_FILE = "data/scores.json"

flashcards = [
Flashcard.from_dict(card)
for card in load_json(FLASHCARDS_FILE, [])
]

saved_words = load_json(WORDS_FILE, [])
scores = load_json(SCORES_FILE, [])

srs = SpacedRepetitionManager()

if "current_due_card_front" not in st.session_state:
    st.session_state.current_due_card_front = None

if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None


tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🔍 Word Lookup & AI",
        "🃏 Flashcards",
        "📝 Quiz",
        "📊 Stats",
    ]
)


with tab1:
    render_search_tab()


with tab2:
    flashcards = render_flashcard_tab(
        flashcards,
        saved_words,
        srs,
    )


with tab3:
    render_quiz_tab(
        flashcards,
        saved_words,
        scores,
    )


with tab4:
    render_stats_tab(
        saved_words,
        scores,
    )




