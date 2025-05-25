import os
import json
import datetime

class ArticleLinksManager:
    def __init__(self, filename="article_links.json"):
        self.filename = filename
        self.articles = self._load_articles()
    
    def _load_articles(self):
        """
        Load articles from the JSON file
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except:
                return []
        return []
    
    def save_articles(self):
        """
        Save articles to the JSON file
        """
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.articles, file, ensure_ascii=False, indent=2)
    
    def add_article(self, title, subject, permalink):
        """
        Add a new article to the links manager
        """
        # Check if article with this permalink already exists
        for article in self.articles:
            if article['permalink'] == permalink:
                return False
        
        # Add new article
        self.articles.append({
            'title': title,
            'subject': subject,
            'permalink': permalink,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        # Save to file
        self.save_articles()
        return True
    
    def get_related_articles(self, subject, current_permalink, max_links=3):
        """
        Get related articles based on subject similarity
        """
        # Get words from the subject
        subject_words = set(subject.lower().split())
        
        # Score articles based on relevance
        scored_articles = []
        for article in self.articles:
            # Skip the current article
            if article['permalink'] == current_permalink:
                continue
            
            # Calculate word overlap for relevance
            article_subject_words = set(article['subject'].lower().split())
            overlap = len(subject_words.intersection(article_subject_words))
            
            if overlap > 0:
                scored_articles.append({
                    'title': article['title'],
                    'permalink': article['permalink'],
                    'score': overlap
                })
        
        # Sort by relevance score (higher is more relevant)
        scored_articles.sort(key=lambda x: x['score'], reverse=True)
        
        # Return the top N most relevant articles
        return scored_articles[:max_links]
    
    def get_all_articles(self):
        """
        Get all articles in the links manager
        """
        return self.articles