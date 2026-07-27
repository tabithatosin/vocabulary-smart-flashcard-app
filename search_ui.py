import streamlit as st
from word_service import DictionaryClient, Word

st.set_page_config(
    page_title="Vocabulary Master",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Vocabulary Master")
st.header("Word Lookup & AI")
st.write("Search for a word to explore its meaning and learn with AI.")

word_input = st.text_input(
    "Enter a word",
    placeholder="e.g. beautiful, curious, resilient"
)

search_button = st.button("Search", use_container_width=True)

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
                for number, definition in enumerate(word.definitions, start=1):
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

            try:
                with st.spinner("Generating AI learning content..."):
                    word.add_ai_content()

                st.write("**Explanation**")
                st.write(word.ai_explanation)

                st.write("**Example**")
                st.write(word.ai_example)

                st.write("**Memory Trick**")
                st.write(word.memory_trick)

            except RuntimeError as e:
                st.warning(
                    "The dictionary results are available, but AI learning "
                    "content is temporarily unavailable."
                )
                st.caption(str(e))

        except ValueError as e:
            st.error(str(e))

        except RuntimeError as e:
            st.error(str(e))