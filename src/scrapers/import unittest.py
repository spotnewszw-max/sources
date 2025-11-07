import unittest
from unittest.mock import patch, MagicMock
from scrapers.scraper_thestandard import scrape_thestandard

# scrapers/test_scraper_thestandard.py


class TestScrapeTheStandard(unittest.TestCase):
    @patch("scrapers.scraper_thestandard.cloudscraper.create_scraper")
    @patch("scrapers.scraper_thestandard.extract_featured_image", return_value="http://img.com/img.jpg")
    @patch("scrapers.scraper_thestandard.extract_published_date", return_value="2024-01-01")
    @patch("scrapers.scraper_thestandard.extract_content_paragraphs", return_value=["Paragraph 1", "Paragraph 2"])
    @patch("scrapers.scraper_thestandard.render_paragraphs_html", return_value="<p>Paragraph 1</p><p>Paragraph 2</p>")
    @patch("scrapers.scraper_thestandard.build_source_attribution", return_value="<div>Source</div>")
    @patch("scrapers.scraper_thestandard.time.sleep", return_value=None)
    def test_scrape_success(self, mock_sleep, mock_attribution, mock_render, mock_extract, mock_date, mock_image, mock_scraper):
        # Mock the scraper's get method for listing and article pages
        mock_session = MagicMock()
        # Listing page HTML with one article link
        mock_listing_html = '''
            <html>
                <body>
                    <article>
                        <a href="https://www.thestandard.co.zw/article1">Test Article</a>
                    </article>
                </body>
            </html>
        '''
        # Article page HTML (content is not used due to mocks)
        mock_article_html = "<html><body><div>Article Content</div></body></html>"
        # Configure get() to return listing, then article
        mock_session.get.side_effect = [
            MagicMock(status_code=200, content=mock_listing_html.encode("utf-8")),
            MagicMock(status_code=200, content=mock_article_html.encode("utf-8")),
        ]
        mock_scraper.return_value = mock_session

        articles = scrape_thestandard(max_articles=1)
        self.assertIsInstance(articles, list)
        self.assertEqual(len(articles), 1)
        article = articles[0]
        self.assertIn("title", article)
        self.assertIn("content", article)
        self.assertIn("source_url", article)
        self.assertIn("source", article)
        self.assertEqual(article["title"], "Test Article")
        self.assertEqual(article["image_url"], "http://img.com/img.jpg")
        self.assertIn("<p>Paragraph 1</p>", article["content"])
        self.assertIn("<div>Source</div>", article["content"])

    @patch("scrapers.scraper_thestandard.cloudscraper.create_scraper")
    @patch("scrapers.scraper_thestandard.time.sleep", return_value=None)
    def test_scrape_no_articles(self, mock_sleep, mock_scraper):
        mock_session = MagicMock()
        # Listing page with no articles
        mock_session.get.return_value = MagicMock(status_code=200, content=b"<html><body></body></html>")
        mock_scraper.return_value = mock_session

        articles = scrape_thestandard(max_articles=2)
        self.assertIsInstance(articles, list)
        self.assertEqual(len(articles), 0)

    @patch("scrapers.scraper_thestandard.cloudscraper.create_scraper")
    @patch("scrapers.scraper_thestandard.time.sleep", return_value=None)
    def test_scrape_network_failure(self, mock_sleep, mock_scraper):
        mock_session = MagicMock()
        # Simulate network error on get
        mock_session.get.side_effect = Exception("Network error")
        mock_scraper.return_value = mock_session

        articles = scrape_thestandard(max_articles=1)
        self.assertIsInstance(articles, list)
        self.assertEqual(len(articles), 0)

if __name__ == "__main__":
    unittest.main()