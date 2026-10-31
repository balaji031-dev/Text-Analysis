# Blackcoffer Data Extraction and Text Analysis

## 1. Project Overview

This project extracts article text from the URLs provided in the input Excel file and performs text analysis to calculate the 13 variables specified in the Blackcoffer assignment.

The final results are saved in an Excel file with the required output column names and order.

## 2. Project Structure

```text
Blackcoffer/
├── assignments_files/
│   ├── Input.xlsx
│   ├── MasterDictionary/
│   │   ├── positive-words.txt
│   │   └── negative-words.txt
│   └── StopWords/
├── articles/
│   └── <URL_ID>.txt
├── output/
│   ├── Blackcoffer_Output.xlsx
│   └── extraction_log.csv
├── discover_urls.py
├── prepare_input.py
├── clean_input.py
├── extract_articles.py
├── text_analysis.py
├── validate_output.py
└── README.md
```

## 3. Requirements

- Python 3
- pandas
- openpyxl
- requests
- beautifulsoup4
- trafilatura

## 4. Environment Setup

Create and activate a virtual environment in the project directory.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install pandas openpyxl requests beautifulsoup4 trafilatura
```

## 5. Execution Steps

Run the scripts from the project root directory.

1. Discover article URLs:

   ```powershell
   python discover_urls.py
   ```

2. Prepare the input Excel file:

   ```powershell
   python prepare_input.py
   ```

3. Remove URLs that do not contain usable article content:

   ```powershell
   python clean_input.py
   ```

4. Extract article text into individual text files:

   ```powershell
   python extract_articles.py
   ```

5. Perform text analysis and generate the output workbook:

   ```powershell
   python text_analysis.py
   ```

6. Validate the generated output:

   ```powershell
   python validate_output.py
   ```

**Note:** The input preparation and cleaning steps can overwrite the working input file. Preserve a backup of the original input before running them. If article extraction has already been completed successfully, rerun extraction only when necessary.

## 6. Text Analysis Variables

The program calculates the following variables:

1. Positive Score
2. Negative Score
3. Polarity Score
4. Subjectivity Score
5. Average Sentence Length
6. Percentage of Complex Words
7. Fog Index
8. Average Number of Words Per Sentence
9. Complex Word Count
10. Word Count
11. Syllable Per Word
12. Personal Pronouns
13. Average Word Length

The positive and negative word dictionaries and the supplied stop-word lists are used by the analysis script.

## 7. Output

The final output file is:

`output/Blackcoffer_Output.xlsx`

The workbook contains the URL ID, URL, and all 13 required text-analysis variables in the specified column order.

## 8. Validation Results

The latest validation run reported:

- Input rows: 1,037
- Output rows: 1,037
- Missing article files during analysis: 0
- Missing output values: 0
- Duplicate URL IDs: 0
- Output columns: 15

These results confirm the row counts and output structure. The calculation formulas and article extraction quality should also be reviewed before final submission.

## 9. Reproducibility

Keep the Python scripts, input workbook, article text files, stop-word files, and master dictionaries available to reproduce the analysis. The final output workbook and this README document the generated results and execution procedure.