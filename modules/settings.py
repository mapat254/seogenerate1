# SEO Article Generator Settings

# Paths and directories
OUTPUT_FOLDER = "_posts"  # Output directory for generated articles
IMAGES_FOLDER = "assets/image"  # Images folder in root directory
ARTICLE_LINKS_FILE = "article_links.json"  # File to store article links for internal linking
API_KEYS_FILE = "apikey.txt"  # File to store API keys

# API settings
API_KEY_MIN_LENGTH = 25  # Minimum length for a valid API key
DEFAULT_DOMAIN = "bloggers.web.id"  # Default domain if none provided

# Article generation settings
DEFAULT_PUBLISHER = "Mas DEEe"  # Default publisher name
MAX_RETRIES = 5  # Maximum retries for API requests
WAIT_TIME_BETWEEN_REQUESTS = 2  # Wait time between API requests (seconds)

# Model selection
DEFAULT_TITLE_MODEL = "gemini-1.5-flash"  # Default model for title generation
DEFAULT_ARTICLE_MODEL = "gemini-1.5-flash"  # Default model for article generation
FALLBACK_MODEL = "gemini-1.5-flash"  # Fallback model if primary fails

# Images settings
MAX_IMAGES_PER_ARTICLE = 7  # Maximum number of images per article
MAX_SEARCH_ATTEMPTS = 3  # Maximum attempts for image search

# HTML & XML export settings
HTML_OUTPUT_DIR = "html_export"  # Directory for HTML exports
WORDPRESS_XML_FILE = "wordpress_export.xml"  # WordPress XML export filename
BLOGSPOT_XML_FILE = "blogspot_export.xml"  # Blogspot XML export filename