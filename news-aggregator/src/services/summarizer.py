from transformers import pipeline

class ArticleSummarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization")

    def summarize(self, article_text):
        summary = self.summarizer(article_text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text'] if summary else "No summary available."