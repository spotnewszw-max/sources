"""
Think Tank Analysis Engine
Analyzes news, social media posts, and trends to generate insights and predictions
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Analyzes content for themes, trends, and patterns"""
    
    ZIMBABWE_POLITICAL_FIGURES = {
        "Emmerson Mnangagwa": ["mnangagwa", "emmerson", "president"],
        "Nelson Chamisa": ["chamisa", "nelson"],
        "Mthuli Ncube": ["ncube", "mthuli"],
        "Constantino Chiwenga": ["chiwenga", "constantino", "vp"],
        "Strive Masiyiwa": ["masiyiwa", "strive"],
        "Hopewell Chin'ono": ["hopewell", "chin'ono"],
        "Vince Musewe": ["musewe", "vince"]
    }
    
    ZIMBABWE_TOPICS = {
        "Politics": ["election", "parliament", "government", "political", "minister", "opposition"],
        "Economy": ["inflation", "currency", "economy", "dollar", "rtgs", "bond notes", "economic"],
        "Agriculture": ["farming", "agriculture", "crops", "drought", "harvest", "land"],
        "Health": ["health", "disease", "covid", "pandemic", "medical", "healthcare"],
        "Education": ["education", "school", "university", "student", "exam"],
        "Technology": ["tech", "digital", "internet", "technology", "innovation"],
        "Media": ["press", "journalist", "media", "freedom"],
        "Security": ["military", "army", "police", "security", "violence"]
    }
    
    def __init__(self):
        self.openai_available = OPENAI_AVAILABLE
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract political figures, organizations, and topics from text"""
        text_lower = text.lower()
        entities = {
            "politicians": [],
            "topics": [],
            "organizations": [],
            "sentiment": self._analyze_sentiment(text)
        }
        
        # Extract politicians
        for politician, keywords in self.ZIMBABWE_POLITICAL_FIGURES.items():
            if any(kw in text_lower for kw in keywords):
                entities["politicians"].append(politician)
        
        # Extract topics
        for topic, keywords in self.ZIMBABWE_TOPICS.items():
            if any(kw in text_lower for kw in keywords):
                entities["topics"].append(topic)
        
        # Extract organizations (simple pattern matching)
        organizations = ["ZANU-PF", "CCC", "Econet", "NetOne", "Zimbabwe Stock Exchange", "RBZ"]
        for org in organizations:
            if org.lower() in text_lower:
                entities["organizations"].append(org)
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis based on keyword matching"""
        text_lower = text.lower()
        
        positive_words = ["success", "growth", "improve", "positive", "good", "gain", "victory", "achieve"]
        negative_words = ["crisis", "collapse", "fail", "negative", "bad", "loss", "defeat", "decline", "problem"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def detect_patterns(self, articles: List[Dict]) -> Dict:
        """Detect patterns, trends, and recurring themes"""
        patterns = {
            "top_topics": defaultdict(int),
            "top_politicians": defaultdict(int),
            "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
            "trending_keywords": defaultdict(int),
            "organization_mentions": defaultdict(int)
        }
        
        for article in articles:
            text = article.get("content", "") + " " + article.get("title", "")
            entities = self.extract_entities(text)
            
            # Count topics
            for topic in entities["topics"]:
                patterns["top_topics"][topic] += 1
            
            # Count politicians
            for politician in entities["politicians"]:
                patterns["top_politicians"][politician] += 1
            
            # Count sentiment
            patterns["sentiment_distribution"][entities["sentiment"]] += 1
            
            # Count organizations
            for org in entities["organizations"]:
                patterns["organization_mentions"][org] += 1
        
        return patterns
    
    def identify_trends(self, historical_articles: List[Dict], window_days: int = 30) -> Dict:
        """Identify trends over a specific time window"""
        cutoff_date = datetime.now() - timedelta(days=window_days)
        
        recent_articles = [
            a for a in historical_articles
            if datetime.fromisoformat(a.get("published_date", datetime.now().isoformat())) > cutoff_date
        ]
        
        patterns = self.detect_patterns(recent_articles)
        
        # Sort by frequency
        trends = {
            "top_topics": sorted(patterns["top_topics"].items(), key=lambda x: x[1], reverse=True)[:5],
            "top_politicians": sorted(patterns["top_politicians"].items(), key=lambda x: x[1], reverse=True)[:5],
            "top_keywords": sorted(
                {k: v for k, v in patterns["organization_mentions"].items()}.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "sentiment": patterns["sentiment_distribution"],
            "article_count": len(recent_articles),
            "period_days": window_days
        }
        
        return trends


class PredictionEngine:
    """Generates predictions based on historical patterns and trends"""
    
    def __init__(self):
        self.analyzer = ContentAnalyzer()
    
    def forecast_trends(self, historical_articles: List[Dict], forecast_days: int = 30) -> Dict:
        """Forecast future trends based on historical data"""
        recent_trends = self.analyzer.identify_trends(historical_articles, window_days=90)
        
        forecasts = {
            "predicted_top_topics": [],
            "predicted_focus_areas": [],
            "risk_factors": [],
            "opportunity_factors": [],
            "forecast_confidence": 0.0,
            "forecast_period_days": forecast_days
        }
        
        # Topic predictions - assume recent top topics will continue
        for topic, count in recent_trends["top_topics"]:
            # Simple growth model - recent topics likely to remain relevant
            forecasts["predicted_top_topics"].append({
                "topic": topic,
                "confidence": min(0.95, (count / len(recent_trends["article_count"]) + 0.5)),
                "reason": f"Strong recent focus ({count} articles in past 90 days)"
            })
        
        # Identify risk and opportunity factors
        forecasts = self._identify_factors(historical_articles, forecasts, recent_trends)
        
        # Calculate overall confidence
        forecasts["forecast_confidence"] = sum(
            t["confidence"] for t in forecasts["predicted_top_topics"]
        ) / max(len(forecasts["predicted_top_topics"]), 1)
        
        return forecasts
    
    def _identify_factors(self, articles: List[Dict], forecasts: Dict, trends: Dict) -> Dict:
        """Identify risk and opportunity factors"""
        text_corpus = " ".join([a.get("content", "") + " " + a.get("title", "") for a in articles[-100:]])
        text_lower = text_corpus.lower()
        
        # Risk factors
        risk_keywords = {
            "Political Instability": ["election", "protest", "conflict", "tension", "dispute"],
            "Economic Crisis": ["inflation", "currency collapse", "debt", "recession"],
            "Supply Chain Disruption": ["shortage", "blockade", "export ban", "tariff"],
            "Health Emergency": ["outbreak", "epidemic", "pandemic"]
        }
        
        for risk, keywords in risk_keywords.items():
            if any(kw in text_lower for kw in keywords):
                forecasts["risk_factors"].append(risk)
        
        # Opportunity factors
        opportunity_keywords = {
            "Economic Growth": ["growth", "investment", "expansion", "partnership"],
            "Technology Adoption": ["digital", "innovation", "technology", "startup"],
            "Agricultural Recovery": ["harvest", "yield", "crop", "farming success"],
            "Political Reform": ["reform", "transparency", "governance", "accountability"]
        }
        
        for opportunity, keywords in opportunity_keywords.items():
            if any(kw in text_lower for kw in keywords):
                forecasts["opportunity_factors"].append(opportunity)
        
        return forecasts
    
    def predict_outcomes(self, topic: str, recent_events: List[Dict]) -> Dict:
        """Predict possible outcomes for a specific topic"""
        prediction = {
            "topic": topic,
            "possible_outcomes": [],
            "most_likely": None,
            "confidence": 0.0
        }
        
        # Analyze sentiment and patterns in recent events about this topic
        topic_events = [e for e in recent_events if topic.lower() in e.get("content", "").lower()]
        
        if not topic_events:
            return prediction
        
        sentiment_scores = []
        for event in topic_events:
            sentiment = self.analyzer._analyze_sentiment(event.get("content", ""))
            sentiment_scores.append(1 if sentiment == "positive" else -1 if sentiment == "negative" else 0)
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Generate possible outcomes
        if avg_sentiment > 0.3:
            prediction["possible_outcomes"] = [
                "Positive resolution or improvement",
                "Continued positive momentum",
                "Leadership and initiative emerging"
            ]
            prediction["most_likely"] = "Positive resolution"
            prediction["confidence"] = min(0.85, abs(avg_sentiment))
        elif avg_sentiment < -0.3:
            prediction["possible_outcomes"] = [
                "Crisis or escalation",
                "Negative outcome if not addressed",
                "Need for intervention"
            ]
            prediction["most_likely"] = "Escalation without intervention"
            prediction["confidence"] = min(0.85, abs(avg_sentiment))
        else:
            prediction["possible_outcomes"] = [
                "Status quo continues",
                "Slow gradual change",
                "Dependent on external factors"
            ]
            prediction["most_likely"] = "Status quo with gradual shifts"
            prediction["confidence"] = 0.6
        
        return prediction


class ArticleGenerator:
    """Generates analysis articles and reports"""
    
    def __init__(self):
        self.analyzer = ContentAnalyzer()
        self.prediction_engine = PredictionEngine()
        self.openai_available = OPENAI_AVAILABLE
    
    async def generate_historical_analysis(
        self,
        topic: str,
        articles: List[Dict],
        years_back: int = 10
    ) -> Dict:
        """Generate historical analysis article"""
        
        article = {
            "type": "historical_analysis",
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "title": f"Historical Analysis: {topic} in Zimbabwe (Past {years_back} Years)",
            "content": "",
            "sections": {}
        }
        
        # Collect historical context
        historical_content = " ".join([
            a.get("title", "") + " " + a.get("content", "")
            for a in articles if topic.lower() in a.get("content", "").lower()
        ])
        
        # Generate sections using LLM or templates
        article["sections"]["background"] = self._generate_background(topic, articles)
        article["sections"]["timeline"] = self._generate_timeline(topic, articles)
        article["sections"]["key_events"] = self._generate_key_events(topic, articles)
        article["sections"]["evolution"] = self._generate_evolution(topic, articles)
        
        # Combine sections into full content
        article["content"] = self._combine_sections(article["sections"])
        
        return article
    
    async def generate_present_analysis(
        self,
        topic: str,
        recent_articles: List[Dict],
        days: int = 7
    ) -> Dict:
        """Generate present-day analysis article"""
        
        article = {
            "type": "present_analysis",
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "title": f"Current Situation: {topic} in Zimbabwe",
            "content": "",
            "sections": {}
        }
        
        # Analyze current state
        trends = self.analyzer.identify_trends(recent_articles, window_days=days)
        
        article["sections"]["overview"] = self._generate_present_overview(topic, recent_articles, trends)
        article["sections"]["stakeholders"] = self._generate_stakeholders(topic, recent_articles)
        article["sections"]["current_challenges"] = self._generate_challenges(topic, recent_articles)
        article["sections"]["recent_developments"] = self._generate_recent_developments(topic, recent_articles)
        article["sections"]["sentiment_analysis"] = self._generate_sentiment_analysis(topic, trends)
        
        article["content"] = self._combine_sections(article["sections"])
        
        return article
    
    async def generate_future_prediction(
        self,
        topic: str,
        articles: List[Dict],
        forecast_days: int = 90
    ) -> Dict:
        """Generate future prediction article"""
        
        forecasts = self.prediction_engine.forecast_trends(articles, forecast_days=forecast_days)
        predictions = self.prediction_engine.predict_outcomes(topic, articles[-100:])
        
        article = {
            "type": "future_prediction",
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "title": f"Outlook: {topic} in Zimbabwe - Next {forecast_days} Days",
            "content": "",
            "sections": {},
            "confidence": forecasts["forecast_confidence"],
            "risk_level": "high" if forecasts["risk_factors"] else "medium" if forecasts["opportunity_factors"] else "low"
        }
        
        article["sections"]["executive_summary"] = self._generate_prediction_summary(topic, predictions)
        article["sections"]["predicted_scenarios"] = self._generate_scenarios(topic, predictions, forecasts)
        article["sections"]["risk_analysis"] = self._generate_risk_analysis(forecasts)
        article["sections"]["opportunities"] = self._generate_opportunities(forecasts)
        article["sections"]["recommendations"] = self._generate_recommendations(topic, predictions)
        
        article["content"] = self._combine_sections(article["sections"])
        
        return article
    
    # Section generation methods using templates
    def _generate_background(self, topic: str, articles: List[Dict]) -> str:
        """Generate background section"""
        return f"""
BACKGROUND
{topic} has been a significant area of focus in Zimbabwe's development trajectory.
Historical records show its importance to national discourse across multiple administrations.
This analysis provides context for understanding its evolution and current relevance.
        """.strip()
    
    def _generate_timeline(self, topic: str, articles: List[Dict]) -> str:
        """Generate timeline section"""
        # Extract dates and milestones
        entities = defaultdict(list)
        for article in articles:
            text = article.get("content", "")
            year_matches = [int(m) for m in [2020, 2021, 2022, 2023, 2024] if str(m) in text]
            if year_matches:
                for year in year_matches:
                    entities[year].append(article.get("title", ""))
        
        timeline_text = "KEY TIMELINE:\n"
        for year in sorted(entities.keys()):
            timeline_text += f"{year}: {len(entities[year])} significant developments\n"
        
        return timeline_text
    
    def _generate_key_events(self, topic: str, articles: List[Dict]) -> str:
        """Generate key events section"""
        # Get articles most relevant to topic
        relevant = sorted(
            articles,
            key=lambda a: (a.get("title", "") + a.get("content", "")).count(topic),
            reverse=True
        )[:5]
        
        events_text = "KEY EVENTS:\n"
        for i, article in enumerate(relevant, 1):
            events_text += f"{i}. {article.get('title', 'Untitled')}\n"
        
        return events_text
    
    def _generate_evolution(self, topic: str, articles: List[Dict]) -> str:
        """Generate evolution section"""
        return f"""
EVOLUTION OF {topic.upper()}
The topic has evolved significantly through various economic cycles and political transitions.
Multiple factors have contributed to its changing importance and policy implications.
Understanding this evolution is crucial for predicting future trajectories.
        """.strip()
    
    def _generate_present_overview(self, topic: str, articles: List[Dict], trends: Dict) -> str:
        """Generate present overview section"""
        return f"""
CURRENT OVERVIEW
As of {datetime.now().strftime('%B %Y')}, {topic} remains a key area of focus.
Recent coverage shows {len(articles)} significant developments.
Current sentiment: {trends['sentiment']}
        """.strip()
    
    def _generate_stakeholders(self, topic: str, articles: List[Dict]) -> str:
        """Generate stakeholders section"""
        # Extract politicians mentioned
        all_text = " ".join([a.get("content", "") + a.get("title", "") for a in articles])
        analyzer = ContentAnalyzer()
        entities = analyzer.extract_entities(all_text)
        
        stakeholders_text = "KEY STAKEHOLDERS:\n"
        for politician in entities["politicians"][:5]:
            stakeholders_text += f"- {politician}\n"
        
        return stakeholders_text
    
    def _generate_challenges(self, topic: str, articles: List[Dict]) -> str:
        """Generate challenges section"""
        return """
CURRENT CHALLENGES
Multiple interconnected challenges affect the topic area.
These include structural constraints and immediate operational challenges.
Addressing these requires coordinated efforts across multiple stakeholders.
        """.strip()
    
    def _generate_recent_developments(self, topic: str, articles: List[Dict]) -> str:
        """Generate recent developments section"""
        recent = articles[-10:] if len(articles) >= 10 else articles
        developments_text = "RECENT DEVELOPMENTS:\n"
        for i, article in enumerate(recent, 1):
            developments_text += f"{i}. {article.get('title', 'Development')}\n"
        return developments_text
    
    def _generate_sentiment_analysis(self, topic: str, trends: Dict) -> str:
        """Generate sentiment analysis"""
        total = sum(trends['sentiment'].values())
        if total == 0:
            return "No data available for sentiment analysis"
        
        sentiment_text = "SENTIMENT DISTRIBUTION:\n"
        for sentiment, count in trends['sentiment'].items():
            percentage = (count / total) * 100
            sentiment_text += f"- {sentiment.capitalize()}: {percentage:.1f}%\n"
        return sentiment_text
    
    def _generate_prediction_summary(self, topic: str, predictions: Dict) -> str:
        """Generate prediction summary"""
        return f"""
EXECUTIVE SUMMARY
The analysis predicts a {predictions['most_likely'].lower()} scenario.
Confidence level: {predictions['confidence']:.0%}

Most Likely Outcome: {predictions['most_likely']}
        """.strip()
    
    def _generate_scenarios(self, topic: str, predictions: Dict, forecasts: Dict) -> str:
        """Generate scenarios section"""
        scenarios_text = "PREDICTED SCENARIOS:\n"
        for i, outcome in enumerate(predictions['possible_outcomes'], 1):
            scenarios_text += f"Scenario {i}: {outcome}\n"
        return scenarios_text
    
    def _generate_risk_analysis(self, forecasts: Dict) -> str:
        """Generate risk analysis"""
        risk_text = "RISK FACTORS:\n"
        if forecasts['risk_factors']:
            for risk in forecasts['risk_factors']:
                risk_text += f"⚠ {risk}\n"
        else:
            risk_text += "No significant risks identified in current trajectory\n"
        return risk_text
    
    def _generate_opportunities(self, forecasts: Dict) -> str:
        """Generate opportunities section"""
        opp_text = "OPPORTUNITIES:\n"
        if forecasts['opportunity_factors']:
            for opp in forecasts['opportunity_factors']:
                opp_text += f"✓ {opp}\n"
        else:
            opp_text += "Limited immediate opportunities in current environment\n"
        return opp_text
    
    def _generate_recommendations(self, topic: str, predictions: Dict) -> str:
        """Generate recommendations"""
        return """
RECOMMENDATIONS
1. Continued monitoring of key indicators
2. Engagement with stakeholders for validation
3. Regular updating of forecasts as new data emerges
4. Contingency planning for alternative scenarios
        """.strip()
    
    def _combine_sections(self, sections: Dict) -> str:
        """Combine all sections into full article"""
        content = ""
        for section_name, section_content in sections.items():
            content += f"\n## {section_name.upper().replace('_', ' ')}\n\n{section_content}\n"
        return content