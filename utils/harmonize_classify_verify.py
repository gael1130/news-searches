import re
import unicodedata


# Harmonize and classify functions
def normalize_text(text):
    """Normalize text to ASCII, removing special characters."""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def harmonize_source(source):
    """Harmonize the source by normalizing, converting to lowercase, removing spaces, hyphens, and common domain suffixes, and removing apostrophes."""
    # Normalize special characters
    source = normalize_text(source)
    # Convert to lowercase
    source = source.lower()
    # Remove spaces, hyphens, and apostrophes
    source = re.sub(r"\s+|-|'", "", source)
    # Remove common domain suffixes
    source = re.sub(r"\.com$|\.fr$", "", source)
    return source

def classify_results(entries):
    classifications = []
    for entry in entries:
        title = entry.title
        classification = 'useful' if 'useful' in title else 'not useful'
        classifications.append(classification)
    return classifications

# Date Utility Functions
def bisextile(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def days_in_month(year, month):
    if month == 2:
        return 29 if bisextile(year) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31
    
# List Utility Functions
def remove_empty_values(row):
    """ Remove all empty strings from the row. """
    return [value for value in row if value]