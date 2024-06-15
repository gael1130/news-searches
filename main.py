import datetime
from utils.google_sheets import load_ranking_sources, setup_google_sheets_api
from utils.search import check_searches_to_perform
from utils.credentials import load_credentials
from config import Config


search_requests_sheet = "searches_to_perform"

def main():
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()

    credentials = load_credentials(Config.GOOGLE_SHEET_CREDENTIALS_PATH)
    if not credentials:
        print("Failed to load credentials.")
        return

    # Connect to Google Sheets API and get the worksheet
    news_searches_sheet = setup_google_sheets_api(credentials, Config.GOOGLE_SHEET_NAME)

    # Perform a search
    useful_sources, useless_sources = load_ranking_sources(credentials)
    searches_to_perform_sheet = news_searches_sheet.worksheet(search_requests_sheet)
    rows = searches_to_perform_sheet.get_all_values()

    check_searches_to_perform(news_searches_sheet, search_requests_sheet, useful_sources, useless_sources, current_date, current_time, rows)

if __name__ == "__main__":
    main()