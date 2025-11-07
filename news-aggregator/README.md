# News Aggregator Application

This is a news aggregator application that fetches, parses, and summarizes news articles from various sources. It provides a RESTful API built with FastAPI, allowing users to interact with the application to manage news feeds and articles.

## Project Structure

```
news-aggregator
├── src
│   ├── app.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── routers
│   │   │   ├── feeds.py
│   │   │   └── articles.py
│   │   └── dependencies.py
│   ├── core
│   │   ├── config.py
│   │   └── logging.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── session.py
│   ├── services
│   │   ├── fetcher.py
│   │   ├── parser.py
│   │   └── summarizer.py
│   ├── tasks
│   │   ├── celery_app.py
│   │   └── workers.py
│   ├── repositories
│   │   └── article_repository.py
│   ├── schemas
│   │   └── article.py
│   ├── parsers
│   │   ├── rss_parser.py
│   │   └── html_parser.py
│   └── utils
│       ├── http.py
│       └── helpers.py
├── tests
│   ├── test_fetcher.py
│   ├── test_parser.py
│   └── test_api.py
├── scripts
│   ├── run.sh
│   └── migrate.sh
├── migrations
│   └── README
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
├── configs
│   └── default.yaml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd news-aggregator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the environment variables by copying `.env.example` to `.env` and modifying it as needed.

## Usage

To run the application, execute the following command:
```
sh scripts/run.sh
```

## Testing

To run the tests, use:
```
pytest
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.