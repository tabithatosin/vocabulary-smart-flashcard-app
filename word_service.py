import re
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




if __name__ == "__main__":
    print(clean_word("  HELLO  "))
    print(clean_sentence("  Hello    , how are you???  "))