from pathlib import Path
import re
import pandas as pd

# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "assignments_files"
ARTICLES_DIR = BASE_DIR / "articles"
OUTPUT_DIR = BASE_DIR / "output"

INPUT_FILE = FILES_DIR / "Input.xlsx"
TEMPLATE_FILE = FILES_DIR / "Output Data Structure.xlsx"

POSITIVE_FILE = FILES_DIR / "MasterDictionary" / "positive-words.txt"
NEGATIVE_FILE = FILES_DIR / "MasterDictionary" / "negative-words.txt"
STOPWORDS_DIR = FILES_DIR / "StopWords"

OUTPUT_FILE = OUTPUT_DIR / "Blackcoffer_Output.xlsx"

OUTPUT_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# 2. Load word lists
# --------------------------------------------------

def load_word_list(file_path):
    """Read a UTF-8 text file and return lowercase words."""
    words = set()

    with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as file:
        for line in file:
            word = line.strip().lower()
            if word:
                words.add(word)

    return words



stop_words = set()

for file_path in STOPWORDS_DIR.glob("*.txt"):
    stop_words.update(load_word_list(file_path))

positive_words = load_word_list(POSITIVE_FILE) - stop_words
negative_words = load_word_list(NEGATIVE_FILE) - stop_words

print("Positive words:", len(positive_words))
print("Negative words:", len(negative_words))
print("Stop words:", len(stop_words))


# --------------------------------------------------
# 3. Text processing helpers
# --------------------------------------------------

def get_words(text):
    """Extract words, including contractions, from text."""
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower())


def count_syllables(word):
    """
    Estimate syllables by counting vowel groups.
    Do not count a final 'es' or 'ed' as an extra syllable,
    following the assignment instructions.
    """
    word = word.lower().strip()

    if not word:
        return 0

    vowel_groups = re.findall(r"[aeiouy]+", word)
    count = len(vowel_groups)

    if word.endswith(("es", "ed")) and count > 1:
        count -= 1

    return max(count, 1)


def count_personal_pronouns(text):
    """Count specified personal pronouns without counting country-name US."""
    matches = re.findall(
        r"\bI\b|\bwe\b|\bmy\b|\bours\b|\bus\b",
        text,
        flags=re.IGNORECASE,
    )

    # Exclude uppercase US, which can refer to the country.
    return sum(
        1 for match in matches
        if not (match == "US")
    )


def count_sentences(text):
    """Estimate sentence count using sentence-ending punctuation."""
    sentences = re.split(r"[.!?]+", text)
    return sum(1 for sentence in sentences if sentence.strip())


# --------------------------------------------------
# 4. Calculate the 13 analysis variables
# --------------------------------------------------

def analyze_text(text):
    words = get_words(text)

    # Remove stop words for the cleaned word list.
    cleaned_words = [
        word for word in words
        if word not in stop_words
    ]

    word_count = len(cleaned_words)

    # Sentiment scores use cleaned words.
    positive_score = sum(
        1 for word in cleaned_words
        if word in positive_words
    )

    negative_score = sum(
        1 for word in cleaned_words
        if word in negative_words
    )

    polarity_score = (
        (positive_score - negative_score)
        / (positive_score + negative_score + 0.000001)
    )

    subjectivity_score = (
        (positive_score + negative_score)
        / (word_count + 0.000001)
    )

    # Sentence-based readability measures.
    sentence_count = count_sentences(text)

    avg_sentence_length = (
        word_count / sentence_count
        if sentence_count else 0
    )

    complex_words = [
        word for word in cleaned_words
        if count_syllables(word) > 2
    ]

    complex_word_count = len(complex_words)

    percentage_complex_words = (
        complex_word_count / word_count
        if word_count else 0
    )

    fog_index = 0.4 * (
        avg_sentence_length + percentage_complex_words
    )

    avg_words_per_sentence = (
        word_count / sentence_count
        if sentence_count else 0
    )

    syllable_per_word = (
        sum(count_syllables(word) for word in cleaned_words)
        / word_count
        if word_count else 0
    )

    personal_pronouns = count_personal_pronouns(text)

    avg_word_length = (
        sum(len(word) for word in cleaned_words) / word_count
        if word_count else 0
    )

    return {
        "POSITIVE SCORE": positive_score,
        "NEGATIVE SCORE": negative_score,
        "POLARITY SCORE": polarity_score,
        "SUBJECTIVITY SCORE": subjectivity_score,
        "AVG SENTENCE LENGTH": avg_sentence_length,
        "PERCENTAGE OF COMPLEX WORDS": percentage_complex_words,
        "FOG INDEX": fog_index,
        "AVG NUMBER OF WORDS PER SENTENCE": avg_words_per_sentence,
        "COMPLEX WORD COUNT": complex_word_count,
        "WORD COUNT": word_count,
        "SYLLABLE PER WORD": syllable_per_word,
        "PERSONAL PRONOUNS": personal_pronouns,
        "AVG WORD LENGTH": avg_word_length,
    }


# --------------------------------------------------
# 5. Process articles and prepare output
# --------------------------------------------------

input_df = pd.read_excel(INPUT_FILE)
template_df = pd.read_excel(TEMPLATE_FILE, nrows=0)

# Preserve the exact column order in the supplied template.
output_columns = list(template_df.columns)

results = []
missing_articles = []

for index, row in input_df.iterrows():
    url_id = int(row["URL_ID"])
    url = row["URL"]
    article_file = ARTICLES_DIR / f"{url_id}.txt"

    if article_file.exists():
        text = article_file.read_text(
            encoding="utf-8",
            errors="ignore"
        ).strip()
    else:
        text = ""
        missing_articles.append(url_id)

    metrics = analyze_text(text)

    result = {
        "URL_ID": url_id,
        "URL": url,
        **metrics,
    }

    results.append(result)

    if (index + 1) % 100 == 0:
        print(f"Processed {index + 1}/{len(input_df)} articles")


# Build the final DataFrame using the template's exact columns.
output_df = pd.DataFrame(results)

# Add any template columns not generated above as blank columns.
for column in output_columns:
    if column not in output_df.columns:
        output_df[column] = ""

output_df = output_df[output_columns]

output_df.to_excel(OUTPUT_FILE, index=False)

print("\nAnalysis complete!")
print("Total input URLs:", len(input_df))
print("Output rows:", len(output_df))
print("Missing article files:", len(missing_articles))

if missing_articles:
    print("Missing URL_IDs:", missing_articles)

print("Saved output to:", OUTPUT_FILE)