import datetime
from pygooglenews import GoogleNews
from utils.harmonize_classify_verify import harmonize_source, remove_empty_values, days_in_month
from utils.google_sheets import get_or_create_worksheet

def search_articles(search_term, from_date, to_date):
    gn = GoogleNews(lang='fr')
    return gn.search(search_term, from_=from_date, to_=to_date, scraping_bee=None)

def split_date_range(from_date, to_date):
    from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d') if from_date else datetime.datetime(1970, 1, 1)
    to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d')
    mid_date_obj = from_date_obj + (to_date_obj - from_date_obj) // 2
    mid_date = mid_date_obj.strftime('%Y-%m-%d')
    return (from_date, mid_date), (mid_date_obj.strftime('%Y-%m-%d'), to_date)

def classify_article(source, harmonized_useful_sources, harmonized_useless_sources):
    harmonized_source = harmonize_source(source)
    if harmonized_source in harmonized_useful_sources:
        return "utile"
    elif harmonized_source in harmonized_useless_sources:
        return "inutile"
    else:
        return "autre"

def extract_article_data(article, harmonized_useful_sources, harmonized_useless_sources):
    title = article['title']
    link = article['link']
    published_date = article['published']
    published_datetime = datetime.datetime.strptime(published_date, '%a, %d %b %Y %H:%M:%S %Z')
    year = published_datetime.year
    source = title.split(' - ')[-1]
    category = classify_article(source, harmonized_useful_sources, harmonized_useless_sources)
    return [title, source, category, published_date, year, link]

def perform_search(search_term, from_date, to_date, worksheet, harmonized_useful_sources, harmonized_useless_sources):
    print(f"Performing search for '{search_term}' from {from_date} to {to_date}")

    articles = search_articles(search_term, from_date, to_date)
    articles_data = []
    print(f"Number of articles found: {len(articles['entries'])}")

    if len(articles['entries']) > 98:
        print(f"More than 98 articles, splitting the search into two parts: ")
        first_range, second_range = split_date_range(from_date, to_date)
        print(f"First range: {first_range}, Second range: {second_range}")
        perform_search(search_term, first_range[0], first_range[1], worksheet, harmonized_useful_sources, harmonized_useless_sources)
        perform_search(search_term, second_range[0], second_range[1], worksheet, harmonized_useful_sources, harmonized_useless_sources)
    else:
        for article in articles['entries']:
            article_data = extract_article_data(article, harmonized_useful_sources, harmonized_useless_sources)
            articles_data.append(article_data)

        worksheet.append_rows(articles_data)


def check_searches_to_perform(news_searches_sheet, search_requests_sheet, harmonized_useful_sources, harmonized_useless_sources, current_date, current_time, rows):
    started_search = False

    for i, row in enumerate(rows[1:], start=2):
        search_term = row[0]
        status = row[1]

        if status == 'started':
            started_search = True
            dates = remove_empty_values(row[2:])
            worksheet_name = search_term
            worksheet = get_or_create_worksheet(news_searches_sheet, worksheet_name)

            if dates[-1] == 'before 2010':
                perform_search(search_term, '2010-01-01', '2010-12-31', worksheet, harmonized_useful_sources, harmonized_useless_sources)
                row.append('2010')
                row = remove_empty_values(row)
                news_searches_sheet.worksheet(search_requests_sheet).update(f"A{i}:CZ{i}", [row])
                return

            elif '2010' <= dates[-1] < '2019':
                year = int(dates[-1]) + 1
                perform_search(search_term, f'{year}-01-01', f'{year}-12-31', worksheet, harmonized_useful_sources, harmonized_useless_sources)
                row.append(str(year))
                row = remove_empty_values(row)
                news_searches_sheet.worksheet(search_requests_sheet).update(f"A{i}:CZ{i}", [row])
                return

            elif dates[-1] == '2019':
                perform_search(search_term, '2020-01-01', '2020-01-31', worksheet, harmonized_useful_sources, harmonized_useless_sources)
                row.append('2020-01-01')
                row = remove_empty_values(row)
                news_searches_sheet.worksheet(search_requests_sheet).update(f"A{i}:CZ{i}", [row])
                return

            else:
                last_date = datetime.datetime.strptime(dates[-1], '%Y-%m-%d')
                next_month = last_date + datetime.timedelta(days=days_in_month(last_date.year, last_date.month))
                end_of_next_month = datetime.datetime(next_month.year, next_month.month, days_in_month(next_month.year, next_month.month))
                
                # Convert current_date to datetime
                current_datetime = datetime.datetime.combine(current_date, datetime.datetime.min.time())

                if end_of_next_month > current_datetime:
                    perform_search(search_term, next_month.strftime('%Y-%m-%d'), current_datetime.strftime('%Y-%m-%d'), worksheet, harmonized_useful_sources, harmonized_useless_sources)
                    row.append(current_datetime.strftime('%Y-%m-%d'))
                    row[1] = 'completed'
                    row = remove_empty_values(row)
                    news_searches_sheet.worksheet(search_requests_sheet).update(f"A{i}:DA{i}", [row])
                else:
                    perform_search(search_term, next_month.strftime('%Y-%m-%d'), end_of_next_month.strftime('%Y-%m-%d'), worksheet, harmonized_useful_sources, harmonized_useless_sources)
                    row.append(next_month.strftime('%Y-%m-%d'))
                    row = remove_empty_values(row)
                    news_searches_sheet.worksheet(search_requests_sheet).update(f"A{i}:DA{i}", [row])
                return

    if not started_search:
        for i, row in enumerate(rows[1:], start=2):
            search_term = row[0]
            status = row[1]

            if status == 'scheduled':
                print(f"Starting search for '{search_term}'")
                row[1] = 'started'
                worksheet_name = search_term
                worksheet = get_or_create_worksheet(news_searches_sheet, worksheet_name)
                perform_search(search_term, '', '2009-12-31', worksheet, harmonized_useful_sources, harmonized_useless_sources)
                row.append('before 2010')
                row = remove_empty_values(row)
                news_searches_sheet.worksheet(search_requests_sheet).update(f"A{i}:CZ{i}", [row])
                return

    print(f"No searches to perform on {current_date.strftime('%Y-%m-%d')} at {current_time.strftime('%H:%M:%S')}")
