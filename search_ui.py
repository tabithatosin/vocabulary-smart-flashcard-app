import streamlit as st
import os

from word_service import DictionaryClient, Word
from flashcard_srs import Flashcard, load_json, save_json


DATA_FOLDER = "data"
FLASHCARDS_FILE = os.path.join(DATA_FOLDER, "flashcards.json")
WORDS_FILE = os.path.join(DATA_FOLDER, "saved_words.json")

os.makedirs(DATA_FOLDER, exist_ok=True)


def render_search_tab():
    if "current_word" not in st.session_state:
        st.session_state.current_word = None

    st.header("Word Lookup & AI")
    st.write("Search for a word to explore its meaning and learn with AI.")

    word_input = st.text_input(
        "Enter a word",
        placeholder="e.g. beautiful, curious, resilient"
    )

    search_button = st.button(
        "Search",
        use_container_width=True
    )

    if search_button:
        if not word_input.strip():
            st.warning("Please enter a word.")
        else:
            try:
                client = DictionaryClient()

                with st.spinner("Looking up your word..."):
                    raw_data = client.lookup(word_input)
                    parsed_data = client.parse_entry(raw_data)

                word = Word(
                    word=parsed_data["word"],
                    phonetics=parsed_data["phonetics"],
                    definitions=parsed_data["definitions"],
                    examples=parsed_data["examples"],
                    synonyms=parsed_data["synonyms"],
                    antonyms=parsed_data["antonyms"]
                )

                st.session_state.current_word = word

            except ValueError as e:
                st.error(str(e))

            except RuntimeError as e:
                st.error(str(e))

    current_word = st.session_state.current_word

    if current_word is not None:
        word = current_word

        st.success(f"Found: {word.word}")

        st.divider()

        st.subheader("🔊 Pronunciation")

        if word.phonetics:
            for phonetic in word.phonetics:
                st.write(phonetic)
        else:
            st.write("No pronunciation available.")

        st.subheader("📖 Definitions")

        if word.definitions:
            for number, definition in enumerate(
                word.definitions,
                start=1
            ):
                st.write(f"{number}. {definition}")
        else:
            st.write("No definitions available.")

        st.subheader("✏️ Examples")

        if word.examples:
            for example in word.examples:
                st.write(f"- {example}")
        else:
            st.write("No examples available.")

        st.subheader("🔗 Synonyms")

        if word.synonyms:
            st.write(", ".join(word.synonyms))
        else:
            st.write("No synonyms available.")

        st.subheader("↔️ Antonyms")

        if word.antonyms:
            st.write(", ".join(word.antonyms))
        else:
            st.write("No antonyms available.")

        st.divider()

        st.subheader("🤖 AI Learning Content")

        if not word.ai_explanation:
            try:
                with st.spinner(
                    "Generating AI learning content..."
                ):
                    word.add_ai_content()

            except RuntimeError as e:
                st.warning(
                    "The dictionary results are available, but AI "
                    "learning content is temporarily unavailable."
                )
                st.caption(str(e))

        if word.ai_explanation:
            st.write("**Explanation**")
            st.write(word.ai_explanation)

        if word.ai_example:
            st.write("**Example**")
            st.write(word.ai_example)

        if word.memory_trick:
            st.write("**Memory Trick**")
            st.write(word.memory_trick)

        st.divider()

        st.subheader("💾 Save Word")

        if st.button(
            "Save Word",
            use_container_width=True
        ):
            saved_words = load_json(
                WORDS_FILE,
                []
            )

            flashcards = load_json(
                FLASHCARDS_FILE,
                []
            )

            already_saved = any(
                item.get("word") == word.word
                for item in saved_words
            )

            if already_saved:
                st.warning(
                    f"'{word.word}' is already saved."
                )

            else:
                saved_word_data = {
                    "word": word.word,
                    "phonetics": word.phonetics,
                    "definitions": word.definitions,
                    "examples": word.examples,
                    "synonyms": word.synonyms,
                    "antonyms": word.antonyms,
                    "ai_explanation": word.ai_explanation,
                    "ai_example": word.ai_example,
                    "memory_trick": word.memory_trick,
                    "meanings": [
                        {
                            "definition": definition,
                            "example": (
                                word.examples[0]
                                if word.examples
                                else ""
                            ),
                            "synonyms": word.synonyms,
                            "antonyms": word.antonyms,
                        }
                        for definition in word.definitions
                    ],
                }

                saved_words.append(
                    saved_word_data
                )

                flashcard = Flashcard.from_word(
                    word
                )

                flashcards.append(
                    flashcard.to_dict()
                )

                save_json(
                    WORDS_FILE,
                    saved_words
                )

                save_json(
                    FLASHCARDS_FILE,
                    flashcards
                )

                st.success(
                    f"'{word.word}' has been saved and "
                    "added to your flashcards! 🎉"
                )