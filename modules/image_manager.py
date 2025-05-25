import os
import re
import random
import requests
from slugify import slugify
from modules.settings import IMAGES_FOLDER

class ImageManager:
    def __init__(self, images_folder=IMAGES_FOLDER):
        self.images_folder = images_folder
        os.makedirs(self.images_folder, exist_ok=True)
    
    def get_images_from_bing(self, query):
        """
        Search for images using Bing
        """
        try:
            # Set up the headers for the request
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            # Construct search URL
            search_url = f"https://www.bing.com/images/search?q={query}&first=1"
            
            # Get the HTML content of the search results page
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            if not html_content:
                return []
            
            # Extract image URLs using regex
            img_urls = re.findall(r'murl&quot;:&quot;(.*?)&quot;', html_content)
            
            if not img_urls or len(img_urls) == 0:
                return []
            
            # Create image objects from the URLs (up to 5 images)
            images = []
            for i, url in enumerate(img_urls[:5]):
                images.append({
                    "url": url,
                    "title": f"{query} image {i+1}",
                    "source": "Bing"
                })
            
            return images
        
        except Exception as e:
            print(f"Error in get_images_from_bing for query '{query}': {str(e)}")
            return []
    
    def get_images_from_yahoo(self, query):
        """
        Search for images using Yahoo
        """
        try:
            # Set up the headers for the request
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            # Construct search URL
            search_url = f"https://images.search.yahoo.com/search/images?p={query}"
            
            # Get the HTML content of the search results page
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            if not html_content:
                return []
            
            # Extract image URLs using regex - adapt this regex pattern for Yahoo's HTML structure
            img_urls = re.findall(r'<img[^>]+src="([^"]+)"[^>]*class="process[^>]*>', html_content)
            
            if not img_urls or len(img_urls) == 0:
                # Try alternative pattern
                img_urls = re.findall(r'<img[^>]+data-src="([^"]+)"[^>]*class="process[^>]*>', html_content)
            
            if not img_urls or len(img_urls) == 0:
                # Try another alternative pattern
                img_urls = re.findall(r'<img[^>]+src="([^"]+)"[^>]*>', html_content)
                # Filter out small images and icons
                img_urls = [url for url in img_urls if not ('icon' in url.lower() or 'logo' in url.lower())]
                
            if not img_urls or len(img_urls) == 0:
                return []
            
            # Create image objects from the URLs (up to 5 images)
            images = []
            for i, url in enumerate(img_urls[:5]):
                images.append({
                    "url": url,
                    "title": f"{query} image {i+1}",
                    "source": "Yahoo"
                })
            
            return images
        
        except Exception as e:
            print(f"Error in get_images_from_yahoo for query '{query}': {str(e)}")
            return []
    
    def get_images(self, query):
        """
        Get images from both Bing and Yahoo
        """
        # Try Bing first
        bing_images = self.get_images_from_bing(query)
        
        # If Bing returned enough images, use them
        if len(bing_images) >= 3:
            return bing_images
        
        # Otherwise, try Yahoo
        yahoo_images = self.get_images_from_yahoo(query)
        
        # Combine the results
        all_images = bing_images + yahoo_images
        
        # If we still don't have enough images, try with a simplified query
        if len(all_images) < 2:
            # Simplify the query by taking just the first 2-3 words
            simplified_query = ' '.join(query.split()[:3])
            
            # Try Bing with simplified query
            bing_simple_images = self.get_images_from_bing(simplified_query)
            
            # Try Yahoo with simplified query
            yahoo_simple_images = self.get_images_from_yahoo(simplified_query)
            
            # Add to the combined results
            all_images = all_images + bing_simple_images + yahoo_simple_images
        
        return all_images
    
    def find_existing_images_in_assets(self, count=1):
        """
        Find existing images in the assets folder
        """
        # Ensure assets directory exists
        os.makedirs(self.images_folder, exist_ok=True)
        
        # List all files in the assets directory
        image_files = []
        for file in os.listdir(self.images_folder):
            # Check if file is an image
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                image_files.append(f"/{self.images_folder}/{file}")  # Path from site root
        
        # Sort by modification time (newest first)
        image_files.sort(key=lambda x: os.path.getmtime(x.lstrip('/')), reverse=True)
        
        # Return requested number of images or all if fewer exist
        return image_files[:count]
    
    def replace_image_placeholders(self, article, subject, domain):
        """
        Replace image placeholders with real images
        """
        # Find all image placeholders
        pattern = r'\[IMAGE: (.*?)\]'
        image_descriptions = re.findall(pattern, article)
        
        # Track the first image path for the featured image
        featured_image = None
        
        if not image_descriptions:
            # If no placeholders found, try to use an existing image from assets
            existing_images = self.find_existing_images_in_assets(1)
            if existing_images:
                featured_image = existing_images[0]
            return article, featured_image
        
        # Replace each placeholder with an image
        modified_article = article
        for i, description in enumerate(image_descriptions):
            # We'll use the first image as the featured image for the frontmatter
            try:
                # The query should be specific and include the subject and the description
                query = f"{subject} {description}"
                
                # Use our combined image search function
                images = self.get_images(query)
                
                # Try up to 3 times with different queries if needed
                attempts = 0
                while not images and attempts < 3:
                    attempts += 1
                    if attempts == 1:
                        # Try just the description
                        query = description
                    elif attempts == 2:
                        # Try the subject
                        query = subject
                    else:
                        # Try a more generic term related to the subject
                        query = f"{subject} image"
                    
                    images = self.get_images(query)
                
                if images and len(images) > 0:
                    # Find a supported image format from the available images
                    valid_image = None
                    for img in images:
                        img_url = img['url']
                        # Check if the URL contains valid image format indicators
                        if (img_url.endswith('.jpg') or img_url.endswith('.jpeg') or 
                            img_url.endswith('.png') or img_url.endswith('.gif') or 
                            '.jpg?' in img_url or '.jpeg?' in img_url or '.png?' in img_url or 
                            '/photo/' in img_url or '/image/' in img_url):
                            valid_image = img
                            break
                    
                    # If no valid images found, use the first one
                    if valid_image is None and images:
                        valid_image = images[0]
                    
                    # If we have a valid image, use it
                    if valid_image:
                        img_url = valid_image['url']
                        img_title = f"{description}"
                        img_source = valid_image.get('source', 'Image Search')
                    else:
                        # No images available
                        raise Exception("No valid images found")
                    
                    # Create a filename with the format: keyword-title-domain-number.jpg
                    # Format domain as bloggers-web-id (replacing dots with hyphens)
                    domain_part = domain.replace('.', '-')  # Convert dots to hyphens (e.g., "bloggers-web-id")
                    # Combine subject and description to create the keyword part
                    keyword_title = slugify(f"{subject}-{description}")[:40]  # Limit length to avoid excessively long filenames
                    img_filename = f"{keyword_title}-{domain_part}-{i+1}.jpg"
                    img_save_path = os.path.join(self.images_folder, img_filename)
                    img_rel_path = f"{self.images_folder}/{img_filename}"
                    
                    # Download and save the image
                    try:
                        # Set up request headers
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                        
                        # Download the image
                        img_response = requests.get(img_url, headers=headers, stream=True, timeout=10)
                        img_response.raise_for_status()
                        
                        # Save the image to assets folder
                        with open(img_save_path, 'wb') as img_file:
                            for chunk in img_response.iter_content(chunk_size=8192):
                                img_file.write(chunk)
                        
                        # Create markdown image tag with local path (ensuring it starts with a slash for absolute path)
                        if not img_rel_path.startswith('/'):
                            img_rel_path = f"/{img_rel_path}"
                        img_tag = f"![{img_title}]({img_rel_path})"
                        
                        # Store the local path to the image rather than the URL
                        if featured_image is None:
                            # Check if the image URL is valid and supported
                            if img_url and (img_url.endswith('.jpg') or img_url.endswith('.jpeg') or 
                                          img_url.endswith('.png') or img_url.endswith('.gif') or 
                                          'image' in img_url.lower()):
                                # Use the local image path from assets for the featured image
                                featured_image = f"/{img_rel_path}"  # Use relative path from site root
                            else:
                                print(f"Skipping unsupported image format: {img_url}")
                        
                        # Replace the placeholder with the image tag
                        modified_article = modified_article.replace(f"[IMAGE: {description}]", img_tag)
                    
                    except Exception as e:
                        print(f"Error downloading image for '{description}': {str(e)}")
                        
                        # Try to find an existing image in the assets folder to use instead
                        existing_images = self.find_existing_images_in_assets(1)
                        if existing_images:
                            # Use an existing image from assets folder
                            existing_img_path = existing_images[0]
                            img_tag = f"![{img_title}]({existing_img_path})"
                            
                            # Use this as featured image if we don't have one yet
                            if featured_image is None:
                                featured_image = existing_img_path
                        else:
                            # If no existing images, create a fallback reference
                            domain_part = domain.replace('.', '-')  # Convert dots to hyphens
                            filename = f"{slugify(description)}-{domain_part}-fallback.jpg"
                            img_rel_path = f"{self.images_folder}/{filename}"
                            
                            # Try to get any existing image from the assets folder rather than using a placeholder
                            all_assets = self.find_existing_images_in_assets(5)  # Get up to 5 existing images
                            if all_assets:
                                # Use an existing image from the assets folder
                                random_img = random.choice(all_assets)  # Pick a random image for variety
                                # Ensure the path starts with a slash for absolute path
                                if not random_img.startswith('/'):
                                    random_img = f"/{random_img}"
                                img_tag = f"![{img_title}]({random_img})"
                            else:
                                # If no images at all, create a text-only reference
                                img_tag = f"<!-- Image for {img_title} could not be retrieved -->"
                            
                            # Still use the relative path format for consistency
                            if featured_image is None:
                                featured_image = f"/{img_rel_path}"
                        
                        # Replace the placeholder with the appropriate image tag
                        modified_article = modified_article.replace(f"[IMAGE: {description}]", img_tag)
                
                else:
                    # If all attempts failed, keep the placeholder but mark it
                    modified_article = modified_article.replace(
                        f"[IMAGE: {description}]", 
                        f"<!-- Could not find image for: {description} -->"
                    )
            
            except Exception as e:
                print(f"Error replacing image placeholder '{description}': {str(e)}")
                # Mark the error in a comment
                modified_article = modified_article.replace(
                    f"[IMAGE: {description}]", 
                    f"<!-- Error finding image: {description} - {str(e)} -->"
                )
        
        return modified_article, featured_image