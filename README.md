# news-searches
Automate articles extraction and saving them to a google sheet

## Architecture
my_project/
│
├── .venv/                    # Virtual environment (excluded from Git)
├── .env                      # Environment variables file (excluded from Git)
├── .gitignore                # Git ignore file
├── main.py                   # Main application file
├── requirements.txt          # Project dependencies
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── google_sheets.py
│   ├── harmonize.py
│   ├── search_refactored.py
│   ├── classify.py
│   ├── logger.py
├── tests/                    # Test modules
│   ├── __init__.py
│   ├── test_google_sheets.py
│   ├── test_harmonize.py
│   ├── test_search.py
│   ├── test_classify.py
└── data/                     # Data files
    └── sources/
        └── sample_sources.csv

