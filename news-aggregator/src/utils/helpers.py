def format_article(article):
    return {
        "title": article.title,
        "link": article.link,
        "published": article.published,
        "summary": article.summary,
    }

def extract_keywords(text):
    # Placeholder for keyword extraction logic
    return text.split()[:5]  # Example: return first 5 words as keywords

def clean_html(html_content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def log_error(error_message):
    import logging
    logging.error(error_message)