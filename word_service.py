import re
import requests
def clean_word(word):
    """Clean and validate a word before dictionary lookup."""
    word = word.strip().lower()

    if not word:
        raise ValueError("Please enter a word.")

    word = re.sub(r"[^\w\s'-]", "", word)

    if not re.fullmatch(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*", word):
        raise ValueError("Please enter a valid word.")

    return word
def clean_sentence(sentence):
    """Clean extra whitespace and repeated punctuation from a sentence."""
    sentence = sentence.strip()

    if not sentence:
        return ""

    sentence = re.sub(r"\s+", " ", sentence)
    sentence = re.sub(r"\s+([,.!?;:])", r"\1", sentence)
    sentence = re.sub(r"([!?]){2,}", r"\1", sentence)

    return sentence

class DictionaryClient:
    """Client for retrieving word data from the Free Dictionary API."""

    BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

    def __init__(self):
        self.base_url = self.BASE_URL

    def lookup(self, word):
        """Look up a word using the Free Dictionary API."""

        word = clean_word(word)

        url = f"{self.base_url}/{word}"

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 404:
                raise ValueError("Word not found in the dictionary.")

            if response.status_code == 429:
                raise RuntimeError(
                    "Too many requests. Please wait a moment and try again."
                )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            raise RuntimeError(
                "The dictionary service took too long to respond. Please try again."
            )

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Unable to connect to the dictionary service. Please check your internet connection."
            )

        except requests.exceptions.RequestException:
            raise RuntimeError(
                "An error occurred while connecting to the dictionary service."
            )

    def parse_entry(self, data):
        """Extract useful dictionary information from the API response."""

        entry = data[0]

        word = entry.get("word", "")
        phonetics = []
        definitions = []
        examples = []
        synonyms = []
        antonyms = []

        for phonetic in entry.get("phonetics", []):
            text = phonetic.get("text")

            if text:
                phonetics.append(text)

        for meaning in entry.get("meanings", []):
            for definition in meaning.get("definitions", []):
                definition_text = definition.get("definition")

                if definition_text:
                    definitions.append(definition_text)

                example = definition.get("example")

                if example:
                    examples.append(clean_sentence(example))

                synonyms.extend(definition.get("synonyms", []))
                antonyms.extend(definition.get("antonyms", []))

            synonyms.extend(meaning.get("synonyms", []))
            antonyms.extend(meaning.get("antonyms", []))

        synonyms = list(set(synonyms))
        antonyms = list(set(antonyms))

        return {
            "word": word,
            "phonetics": phonetics,
            "definitions": definitions,
            "examples": examples,
            "synonyms": synonyms,
            "antonyms": antonyms,
        }


if __name__ == "__main__":
    client = DictionaryClient()

    raw_data = client.lookup("book")

    result = client.parse_entry(raw_data)

    print(result)