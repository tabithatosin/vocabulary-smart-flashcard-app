import re
import requests
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
import os
import re
import requests

from dotenv import load_dotenv
from google import genai


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    gemini_client = None
    
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
def get_ai_content(word):
    """Generate AI learning content for a vocabulary word."""

    if gemini_client is None:
        raise RuntimeError(
            "Gemini API key is missing. AI features are unavailable."
        )

    prompt = f"""
You are a vocabulary learning assistant.

For the word "{word}", provide:

1. A simple explanation that a learner can easily understand.
2. One simple example sentence using the word.
3. One memorable and creative memory trick to help the learner remember the word.

Return your response in exactly this format:

Explanation: <simple explanation>
Example: <example sentence>
Memory Trick: <memory trick>
"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text

    except Exception as error:
        raise RuntimeError(
            f"Gemini AI request failed: {error}"
        )
        
class Word:
    """Represent a vocabulary word and its learning information."""

    def __init__(
        self,
        word,
        phonetics=None,
        definitions=None,
        examples=None,
        synonyms=None,
        antonyms=None,
    ):
        self.word = word
        self.phonetics = phonetics or []
        self.definitions = definitions or []
        self.examples = examples or []
        self.synonyms = synonyms or []
        self.antonyms = antonyms or []

        self.ai_explanation = ""
        self.ai_example = ""
        self.memory_trick = ""
    def add_ai_content(self):
        """Generate and store AI learning content for this word."""

        ai_response = get_ai_content(self.word)

        lines = ai_response.splitlines()

        for line in lines:
            line = line.strip()

            # Remove markdown formatting from the beginning
            line = line.lstrip("*#").strip()

            if line.lower().startswith("explanation:"):
                self.ai_explanation = line.split(
                    ":", 1
                )[1].strip()

            elif line.lower().startswith("example:"):
                self.ai_example = line.split(
                    ":", 1
                )[1].strip()

            elif line.lower().startswith("memory trick:"):
                self.memory_trick = line.split(
                    ":", 1
                )[1].strip()
    @classmethod
    def from_dictionary_data(cls, data):
        """Create a Word object from parsed dictionary data."""

        return cls(
            word=data.get("word", ""),
            phonetics=data.get("phonetics", []),
            definitions=data.get("definitions", []),
            examples=data.get("examples", []),
            synonyms=data.get("synonyms", []),
            antonyms=data.get("antonyms", []),
        )
if __name__ == "__main__":
    client = DictionaryClient()

    raw_data = client.lookup("book")

    dictionary_data = client.parse_entry(raw_data)

    word = Word.from_dictionary_data(dictionary_data)

    word.add_ai_content()

    print("WORD:", word.word)
    print("PHONETICS:", word.phonetics)
    print("DEFINITIONS:", word.definitions)
    print("EXAMPLES:", word.examples)
    print("SYNONYMS:", word.synonyms)
    print("ANTONYMS:", word.antonyms)

    print("\nAI EXPLANATION:", word.ai_explanation)
    print("AI EXAMPLE:", word.ai_example)
    print("MEMORY TRICK:", word.memory_trick)