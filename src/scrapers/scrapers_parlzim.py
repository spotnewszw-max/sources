import requests
from bs4 import BeautifulSoup

def scrape_parlzim_homepage():
    url = "https://www.parlzim.gov.zw/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    results = {
        "latest_news": [],
        "latest_hansards": []
    }

    # Latest News
    for item in soup.select('.pt-cv-content-item .pt-cv-ifield'):
        title_tag = item.select_one('.pt-cv-title a')
        date_tag = item.select_one('.entry-date time')
        if title_tag:
            results["latest_news"].append({
                "title": title_tag.get_text(strip=True),
                "url": title_tag.get("href"),
                "date": date_tag.get_text(strip=True) if date_tag else None
            })

    # Latest Hansards (PDFs)
    for item in soup.select('.media.link-template-widget'):
        pdf_link = item.select_one('a.img-48')
        title_tag = item.select_one('.media-body a')
        if pdf_link and title_tag:
            results["latest_hansards"].append({
                "title": title_tag.get_text(strip=True),
                "url": pdf_link.get("href"),
                "pdf_title": title_tag.get_text(strip=True)
            })

    return results

if __name__ == "__main__":
    data = scrape_parlzim_homepage()
    print("Latest News:")
    for news in data["latest_news"]:
        print(news)
    print("\nLatest Hansards:")
    for hansard in data["latest_hansards"]:
        print(hansard)