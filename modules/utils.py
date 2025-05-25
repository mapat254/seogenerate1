import os
import re
import json
import time
import random
import datetime
from slugify import slugify
from langdetect import detect
from langcodes import Language
import requests
from modules.settings import API_KEYS_FILE, API_KEY_MIN_LENGTH

def validate_api_key(api_key):
    """
    Validate if a string is a potential Gemini API key
    """
    if not api_key or len(api_key) < API_KEY_MIN_LENGTH:
        return False
    
    # Basic pattern check - this is a simple validation
    # Real validation would occur when the key is used with the API
    if re.match(r'^[A-Za-z0-9_-]+$', api_key):
        return True
    
    return False

def save_api_keys(api_keys):
    """
    Save API keys to the apikey.txt file
    """
    try:
        with open(API_KEYS_FILE, "w", encoding="utf-8") as file:
            for key in api_keys:
                file.write(f"{key}\n")
        return True
    except Exception as e:
        print(f"Error saving API keys: {str(e)}")
        return False

def load_api_keys():
    """
    Load API keys from the apikey.txt file
    """
    api_keys = []
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, "r", encoding="utf-8") as file:
                api_keys = [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(f"Error loading API keys: {str(e)}")
    return api_keys

def detect_language(subject):
    """
    Detect language from text
    """
    try:
        lang_code = detect(subject)
        language = Language.make(language=lang_code).display_name()
        return language
    except:
        return "English"

def generate_permalink(title):
    """
    Generate a permalink from a title
    """
    return f"/{slugify(title)}"

def generate_tags_from_title(title, subject):
    """
    Generate SEO-optimized tags from the title and subject of the article.
    This function uses title words as primary source for tags and supplements with subject words.
    It prioritizes longer phrases as they tend to be more specific keywords.
    """
    # Common words to exclude (both English and Indonesian)
    stop_words = [
        'yang', 'untuk', 'dengan', 'adalah', 'dari', 'cara', 'tips', 'trik',
        'dan', 'atau', 'jika', 'maka', 'namun', 'tetapi', 'juga', 'oleh',
        'the', 'and', 'that', 'this', 'with', 'for', 'from', 'how', 'what',
        'when', 'why', 'where', 'who', 'will', 'your', 'their', 'our', 'its'
    ]
    
    # Clean and normalize text
    clean_title = title.lower().replace(':', ' ').replace('-', ' ').replace(',', ' ').replace('.', ' ')
    clean_subject = subject.lower()
    
    # Extract potential multi-word phrases from title (2-3 words)
    title_parts = clean_title.split()
    title_phrases = []
    
    # Get 2-word phrases
    for i in range(len(title_parts) - 1):
        phrase = title_parts[i] + ' ' + title_parts[i + 1]
        if all(word not in stop_words for word in phrase.split()):
            title_phrases.append(phrase)
    
    # Get 3-word phrases
    for i in range(len(title_parts) - 2):
        phrase = title_parts[i] + ' ' + title_parts[i + 1] + ' ' + title_parts[i + 2]
        if all(word not in stop_words for word in phrase.split()):
            title_phrases.append(phrase)
    
    # Get single words from title
    title_words = [word.strip() for word in clean_title.split() 
                 if len(word.strip()) > 3 and word.lower() not in stop_words]
    
    # Get words from subject
    subject_words = [word.strip() for word in clean_subject.split() 
                    if len(word.strip()) > 3 and word.lower() not in stop_words]
    
    # Build final tag list prioritizing multi-word phrases
    all_tags = []
    
    # First add any 3-word phrases (usually most specific)
    three_word_phrases = [p for p in title_phrases if len(p.split()) == 3]
    all_tags.extend(three_word_phrases[:2])  # Up to 2 three-word phrases
    
    # Then add 2-word phrases
    two_word_phrases = [p for p in title_phrases if len(p.split()) == 2]
    all_tags.extend(two_word_phrases[:2])  # Up to 2 two-word phrases
    
    # Then add important single words
    remaining_slots = 5 - len(all_tags)
    if remaining_slots > 0:
        # Combine and remove duplicates (words already in phrases)
        single_words = []
        for word in title_words + subject_words:
            already_included = any(word in phrase for phrase in all_tags)
            if not already_included and word not in single_words:
                single_words.append(word)
        
        all_tags.extend(single_words[:remaining_slots])
    
    # Ensure we don't exceed 5 tags and we have at least 1 tag
    return all_tags[:5] if all_tags else [subject.split()[0]]

def generate_frontmatter(title, subject, permalink, category=None, publisher="Mas DEEe", featured_image=None):
    """
    Generate Jekyll frontmatter for the article
    """
    today = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    # Generate tags from title and subject
    tags = generate_tags_from_title(title, subject)
    
    # Use provided category or generate from subject if none provided
    if not category:
        main_category = subject.split()[0] if subject.split() else subject
    else:
        main_category = category
    
    # Create frontmatter content as string
    content = "---\n"
    content += f"title: {title}\n"
    content += f"date: {today}\n"
    content += f"publisher: {publisher}\n"
    content += f"layout: post\n"
    
    # Add featured image if available
    if featured_image:
        content += f"image: {featured_image}\n"
    
    content += "tag:\n"
    for tag in tags:  # Using tags generated from title and subject
        content += f"  - {tag}\n"
    content += f"permalink: {permalink}\n"
    content += "categories:\n"
    content += f"  - {main_category}\n"
    content += "---\n\n"
    
    return content

def get_html_content(url, headers=None):
    """
    Get HTML content from a URL
    """
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching URL {url}: {str(e)}")
        return None

def read_subjects_file(filename="subjects.txt"):
    """
    Read subjects from the subjects.txt file
    """
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            subjects = [line.strip() for line in file if line.strip()]
        return subjects
    return []

def get_random_user_agent():
    """
    Get a random user agent to avoid detection
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84'
    ]
    return random.choice(user_agents)