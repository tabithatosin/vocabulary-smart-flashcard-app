# vocabulary-smart-flashcard-app
# 📚 Vocabulary Master

Vocabulary Master is an AI-powered vocabulary learning application that helps users discover, learn, and retain new words through dictionary lookup, AI explanations, smart flashcards, quizzes, and spaced repetition.

## ✨ Features

* 🔍 Word lookup with definitions, pronunciation, examples, synonyms, and antonyms
* 🤖 AI-generated simple explanations, example sentences, and memory tricks using Google Gemini
* 💾 Save vocabulary words for future learning
* 🃏 Smart flashcards with spaced repetition
* 📝 Multiple-choice vocabulary quizzes
* 📊 Progress tracking and quiz statistics
* 📥 Downloadable statistics
* 🗑️ Delete saved words

## 🛠️ Built With

* Python
* Streamlit
* Free Dictionary API
* Google Gemini API
* Requests
* Matplotlib
* JSON

## 🚀 Setup

Clone the repository and enter the project folder:

```bash
git clone https://github.com/tabithatosin/vocabulary-smart-flashcard-app.git
cd vocabulary-smart-flashcard-app
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

**Windows Git Bash:**

```bash
source .venv/Scripts/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root and add your Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

## 📁 Project Structure

* `app.py` — Main Streamlit application
* `word_service.py` — Dictionary API, Gemini AI, and Word class
* `search_ui.py` — Word lookup, AI content, and saving words
* `flashcard_srs.py` — Flashcards, spaced repetition, quizzes, and statistics
* `data/` — Local JSON storage for saved words, flashcards, and quiz scores
* `requirements.txt` — Project dependencies

## 💾 Data & Security

The application currently stores data locally as JSON files. A persistent database would be recommended for a production deployment.

The Gemini API key is stored in `.env`, which is excluded from Git using `.gitignore`. **Never commit your `.env` file or expose your API key publicly.**

## 👥 Collaboration

This project was developed collaboratively using Git and GitHub, with feature branches and Pull Requests used to review and merge contributions into the `main` branch.

