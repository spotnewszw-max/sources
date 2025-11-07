def parse_html_content(html_content):
    from bs4 import BeautifulSoup

    # Create a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title
    title = soup.title.string if soup.title else 'No Title Found'

    # Extract all paragraphs
    paragraphs = soup.find_all('p')
    content = ' '.join([para.get_text() for para in paragraphs])

    return {
        'title': title,
        'content': content
    }