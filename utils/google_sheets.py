import gspread
from utils.harmonize_classify_verify import harmonize_source


def setup_google_sheets_api(credentials, sheet_name="news-searches"):
    gc = gspread.service_account_from_dict(credentials)
    news_searches_sheet = gc.open(sheet_name)
    return news_searches_sheet

def load_ranking_sources(credentials, sheet_name="ranking"):
    """
    Load sources from a Google Sheet and return them as two lists of harmonized sources.
    """
    news_searches_sheet = setup_google_sheets_api(credentials)
    ranking_sheet = news_searches_sheet.worksheet(sheet_name)
    data = ranking_sheet.get_all_records()  # Assumes first row is header

    useful_sources = [row["utile"] for row in data]
    useless_sources = [row["inutile"] for row in data]

    # remove the empty fields
    useful_sources = [source for source in useful_sources if source]
    useless_sources = [source for source in useless_sources if source]

    harmonized_useful_sources = [harmonize_source(source) for source in useful_sources]
    harmonized_useless_sources = [harmonize_source(source) for source in useless_sources]

    return harmonized_useful_sources, harmonized_useless_sources


def read_google_sheet(credentials, sheet_name):
    news_searches_sheet = setup_google_sheets_api(credentials)
    worksheet = news_searches_sheet.worksheet(sheet_name)
    data = worksheet.get_values()
    return data

def write_to_google_sheet(credentials, sheet_name, data):
    news_searches_sheet = setup_google_sheets_api(credentials)
    worksheet = news_searches_sheet.worksheet(sheet_name)
    worksheet.update([data.columns.values.tolist()] + data.values.tolist())

def get_or_create_worksheet(news_searches_sheet, worksheet_name):
    try:
        worksheet = news_searches_sheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = news_searches_sheet.add_worksheet(title=worksheet_name, rows=1000, cols=101)
        worksheet.append_row(['Titre', 'Source', 'Utilité', 'Publication', 'Année', 'Lien'])
    return worksheet