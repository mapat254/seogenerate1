import os
import re
import time
import json
import random
import datetime
import requests
from slugify import slugify
from modules.article_links_manager import ArticleLinksManager
from modules.image_manager import ImageManager
from modules.api_client import GeminiClient
from modules.utils import detect_language, generate_frontmatter
from modules.settings import (
    OUTPUT_FOLDER, IMAGES_FOLDER, ARTICLE_LINKS_FILE,
    DEFAULT_DOMAIN, DEFAULT_PUBLISHER, DEFAULT_TITLE_MODEL, DEFAULT_ARTICLE_MODEL
)

class ArticleGenerator:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or []
        self.links_manager = ArticleLinksManager(ARTICLE_LINKS_FILE)
        self.image_manager = ImageManager(IMAGES_FOLDER)
        self.api_client = GeminiClient(self.api_keys)
    
    def generate_title(self, subject, language, model=DEFAULT_TITLE_MODEL):
        """
        Generate a catchy and SEO-optimized article title
        """
        title_prompt = (
            f"Write a catchy and SEO-optimized article title in {language} about '{subject}'.\n\n"
            f"RULES:\n"
            f"1. Make it attention-grabbing and click-worthy without being clickbait\n"
            f"2. Include the main keyword \"{subject}\" or a closely related term\n"
            f"3. Keep it under 60 characters if possible\n"
            f"4. Make sure it's in {language} language\n"
            f"5. Add a subtitle separated by a colon or dash if appropriate\n"
            f"6. Do not include unnecessary punctuation or all caps\n"
            f"7. If the language is English, make the title more professional and concise\n"
            f"8. For English titles, use power words that drive engagement and clicks\n\n"
            f"FORMAT THE TITLE EXACTLY LIKE THIS (no extra text): Title Here"
        )
        
        response = self.api_client.send_request(title_prompt, model)
        
        # Clean up title (remove quotes and extra formatting)
        title = response.strip().replace('"', '').replace("'", "")
        
        # Handle multi-paragraph responses (take only the first line)
        title = title.split('\n')[0]
        
        return title
    
    def generate_article(self, title, subject, domain, permalink, language, model=DEFAULT_ARTICLE_MODEL, related_articles=None):
        """
        Generate a comprehensive SEO article
        """
        # Add related articles information to prompt if available
        related_links_text = ""
        if related_articles and len(related_articles) > 0:
            related_links_text = "RELATED ARTICLES TO INCLUDE:\n"
            for i, article in enumerate(related_articles):
                related_links_text += f"{i+1}. Title: \"{article['title']}\", Link: {domain}{article['permalink']}\n"
            related_links_text += "Include these links naturally within the article content using relevant anchor text that relates to both the keyword and the destination article.\n\n"
        
        # Determine if we should force English content based on subject or language
        force_english = language.lower() == "english" or any(eng_term in subject.lower() for eng_term in ["seo", "digital marketing", "google", "content marketing", "social media", "analytics"])
        
        # Define article language requirements
        language_specific_instructions = ""
        if force_english:
            language_specific_instructions = (
                "ENGLISH CONTENT REQUIREMENTS:\n"
                "1. Write the entire article in professional, flawless English regardless of the keyword language.\n"
                "2. Use precise terminology and industry-standard vocabulary.\n"
                "3. Maintain a clear, authoritative tone that conveys expertise.\n"
                "4. For technical topics, use proper technical terms and explain them clearly.\n"
                "5. Use American English spelling and grammar conventions.\n\n"
            )
        
        article_prompt = (
            f"Write an extremely comprehensive and in-depth SEO-optimized article for the following title: \"{title}\"\n\n"
            f"FORMAT REQUIREMENTS:\n"
            f"1. Start with an engaging 3-4 paragraph introduction that includes the domain name '{domain}' as a BOLD HYPERLINK only ONCE in the first paragraph. Format it as [**{domain}**](https://{domain}). This automatically creates both bold and hyperlink.\n"
            f"2. Immediately after the introduction, insert an image placeholder with format: [IMAGE: {subject} overview infographic].\n"
            f"3. Create a deep hierarchical structure with H2, H3, and H4 headings (use markdown format: ##, ###, ####). START with H2 headings after the introduction, and use H3 and H4 for more detailed subsections.\n"
            f"4. Create a minimum of 4000 words (target range: 4000-7000 words) with detailed professional-level analysis for each heading section.\n"
            f"5. Bold 5-7 primary and secondary keywords related to '{subject}' throughout the article for SEO optimization. These should appear naturally in the text, especially at the beginning of paragraphs.\n"
            f"6. Include exactly 6-7 image placeholders throughout the article using format: [IMAGE: detailed description related to the heading], but ALWAYS place these image placeholders BEFORE their related headings, not after.\n"
            f"7. DO NOT include any image placeholders in the conclusion section or at the very end of the article.\n" 
            f"8. End with a warm, personalized conclusion paragraph that directly addresses the reader, followed by a friendly call-to-action paragraph with a bold internal link to '[**{domain}{permalink}**](https://{domain}{permalink})' using the article title as anchor text.\n\n"
            f"{language_specific_instructions}"
            f"{related_links_text}"
            f"CONTENT REQUIREMENTS:\n"
            f"1. Make each section extremely detailed, professional, and comprehensive - cover the topic '{subject}' with expert-level depth and analysis.\n"
            f"2. Include real-world examples, case studies, statistics, and actionable step-by-step instructions with specific details and metrics when possible.\n"
            f"3. Write in a professional, authoritative {language} tone that establishes genuine expertise. Address readers directly using 'you' and 'your' to increase engagement.\n"
            f"4. Add 6-8 external links to highly authoritative sources (major publications, university studies, industry leaders) with descriptive anchor text.\n"
            f"5. Maintain a keyword density of 2-3% for the main keyword '{subject}'. Aim for the main keyword to appear approximately 1-2 times per 100 words. This creates optimal density without keyword stuffing.\n"
            f"6. Heavily optimize for LSI (Latent Semantic Indexing) keywords by incorporating 10-15 semantically related terms to '{subject}' throughout the article. These should appear naturally within the content.\n"
            f"7. Create advanced internal linking: Convert 7-8 appropriate LSI keywords or phrases into internal links pointing to: [**{domain}/keyword-phrase**](https://{domain}/keyword-phrase) - replace spaces with hyphens in the URL portion.\n"
            f"8. For related articles provided, include links to them using descriptive anchor text that naturally fits within the content, with at least one link in each major section.\n"
            f"9. DO NOT include table of contents - start directly with the first major H2 section after the introduction and infographic.\n"
            f"10. Include multiple professional-quality formatted elements: 2-3 bulleted lists, 2-3 numbered lists, and at least one detailed comparison table or data table formatted with markdown.\n"
            f"11. Make each H2, H3, and H4 heading compelling, specific, and keyword-optimized. Follow SEO best practices: include numbers in some headings, use 'how to,' 'why,' or question formats in others, and keep headings under 60 characters.\n"
            f"12. For each heading section, start with a concise topic sentence that summarizes the section, followed by a detailed, data-backed explanation (250-400 words per H2 section).\n"
            f"13. Develop a clear hierarchy: Each H2 should have 2-3 H3 subsections, and at least one H3 should contain 1-2 H4 subsections for even more detailed analysis.\n"
            f"14. DO NOT include FAQ sections - directly incorporate questions and their detailed answers into the relevant sections as regular paragraphs and headings.\n"
            f"15. When mentioning specific tools, resources, or techniques, provide expert insights about their implementation, advantages, limitations, and competitive alternatives.\n"
            f"16. Include practical examples for immediate implementation in each section, with clear steps and expected outcomes.\n"
            f"17. Add current industry trends, future predictions backed by research, and expert insights in the relevant industry. Include recent statistics or developments (2023-2025) where appropriate.\n"
            f"18. Create a logical flow between sections, with clear transitions that connect each topic to the main subject and to adjacent headings.\n"
            f"19. Ensure each H2 section is comprehensive enough to stand alone as a mini-article on its subtopic, while still contributing to the overall narrative.\n"
            f"20. If you want to include an image for the final section before conclusion, place it BEFORE the heading, not after it.\n"
            f"21. For technical or complex topics, include practical applications or simplified explanations to make the content accessible while maintaining its professional depth."
        )
        
        response = self.api_client.send_request(article_prompt, model)
        return response
    
    def generate_seo_article(self, subject, domain=DEFAULT_DOMAIN, model_title=DEFAULT_TITLE_MODEL, 
                            model_article=DEFAULT_ARTICLE_MODEL, category=None, publisher=DEFAULT_PUBLISHER,
                            progress_callback=None):
        """
        Generate a complete SEO article
        """
        try:
            # Detect language from subject
            language = detect_language(subject)
            
            # Update progress if callback provided
            if progress_callback:
                progress_callback("language", 30)
            
            # Generate title
            title = self.generate_title(subject, language, model_title)
            
            # Update progress if callback provided
            if progress_callback:
                progress_callback("title", 40)
            
            # Generate permalink
            permalink = f"/{slugify(title)}"
            
            # Find related articles
            related_articles = self.links_manager.get_related_articles(subject, permalink)
            
            # Generate article content with related links
            article = self.generate_article(title, subject, domain, permalink, language, model_article, related_articles)
            
            # Update progress if callback provided
            if progress_callback:
                progress_callback("article", 60)
            
            # Replace image placeholders with real images
            article_with_images, featured_image = self.image_manager.replace_image_placeholders(article, subject, domain)
            
            # Update progress if callback provided
            if progress_callback:
                progress_callback("images", 80)
            
            # Generate Jekyll frontmatter with optional custom category and featured image
            frontmatter = generate_frontmatter(title, subject, permalink, category, publisher, featured_image)
            
            # Add <!--more--> tag after the first paragraph
            paragraphs = article_with_images.split('\n\n')
            if paragraphs:
                paragraphs[0] += '\n\n<!--more-->\n\n'
                article_with_images = '\n\n'.join(paragraphs)
            
            # Create full markdown document with frontmatter
            markdown_content = frontmatter + article_with_images
            
            # Create date prefix for Jekyll post
            date_prefix = datetime.datetime.now().strftime('%Y-%m-%d-')
            
            # File path for markdown post in Jekyll format
            file_md = os.path.join(OUTPUT_FOLDER, f"{date_prefix}{slugify(title)}.md")
            
            # Create output folder if it doesn't exist
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            
            # Save markdown file with frontmatter
            with open(file_md, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_content)
            
            # Update progress if callback provided
            if progress_callback:
                progress_callback("saving", 90)
            
            # Add the article to our link manager for future reference
            self.links_manager.add_article(title, subject, permalink)
            
            return {
                "title": title,
                "article": article_with_images,
                "markdown": markdown_content,
                "permalink": permalink,
                "file_path": file_md
            }
            
        except Exception as e:
            raise Exception(f"Error generating article: {str(e)}")