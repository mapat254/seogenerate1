import os
import re
import json
import time
import random
import datetime
from slugify import slugify
import markdown
import xml.etree.ElementTree as ET
import frontmatter
from modules.settings import (
    HTML_OUTPUT_DIR, WORDPRESS_XML_FILE, BLOGSPOT_XML_FILE
)

class Exporter:
    def __init__(self):
        # Create output directories
        os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)
    
    def export_to_html(self, posts_dir):
        """
        Export markdown posts to HTML files
        """
        try:
            # Create HTML output directory
            os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)
            
            # Find all markdown files in the posts directory
            markdown_files = []
            if os.path.exists(posts_dir):
                markdown_files = [f for f in os.listdir(posts_dir) if f.endswith('.md')]
            
            if not markdown_files:
                return {"success": False, "error": "No markdown files found"}
            
            # Process each markdown file
            processed_posts = []
            for md_file in markdown_files:
                try:
                    # Read the markdown file
                    with open(os.path.join(posts_dir, md_file), 'r', encoding='utf-8') as file:
                        post_content = file.read()
                    
                    # Parse frontmatter
                    post = frontmatter.loads(post_content)
                    
                    # Extract metadata
                    title = post.get('title', 'Untitled')
                    date = post.get('date', datetime.datetime.now().isoformat())
                    permalink = post.get('permalink', '')
                    tags = post.get('tag', [])
                    categories = post.get('categories', [])
                    featured_image = post.get('image', '')
                    
                    # Convert markdown to HTML
                    html_content = markdown.markdown(post.content, extensions=['tables', 'fenced_code'])
                    
                    # Create HTML file
                    html_filename = slugify(title) + '.html'
                    html_path = os.path.join(HTML_OUTPUT_DIR, html_filename)
                    
                    # Simple HTML template
                    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        img {{ max-width: 100%; height: auto; }}
        h1, h2, h3, h4, h5, h6 {{ color: #333; }}
        a {{ color: #0066cc; text-decoration: none; }}
        .post-meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        .post-tags {{ margin-top: 30px; }}
        .post-tags span {{ background: #f1f1f1; padding: 3px 8px; border-radius: 3px; margin-right: 5px; font-size: 0.8em; }}
    </style>
</head>
<body>
    <article>
        <header>
            <h1>{title}</h1>
            <div class="post-meta">
                <time datetime="{date}">{datetime.datetime.fromisoformat(date.replace('Z', '+00:00')).strftime('%B %d, %Y')}</time>
                {' - ' + ', '.join(categories) if categories else ''}
            </div>
            {f'<img src="{featured_image}" alt="{title}">' if featured_image else ''}
        </header>
        
        <div class="post-content">
            {html_content}
        </div>
        
        <footer>
            <div class="post-tags">
                {' '.join([f'<span>{tag}</span>' for tag in tags])}
            </div>
        </footer>
    </article>
</body>
</html>"""
                    
                    # Save HTML file
                    with open(html_path, 'w', encoding='utf-8') as file:
                        file.write(html_template)
                    
                    # Add to processed posts
                    processed_posts.append({
                        "title": title,
                        "date": date,
                        "permalink": permalink,
                        "tags": tags,
                        "categories": categories,
                        "featured_image": featured_image,
                        "content": html_content,
                        "html_file": html_path
                    })
                    
                except Exception as e:
                    print(f"Error processing file {md_file}: {str(e)}")
            
            return {
                "success": True, 
                "count": len(processed_posts), 
                "posts": processed_posts,
                "output_dir": HTML_OUTPUT_DIR
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_to_wordpress(self, posts_dir):
        """
        Export posts to WordPress XML format
        """
        try:
            # First convert to HTML
            html_result = self.export_to_html(posts_dir)
            
            if not html_result["success"]:
                return {"success": False, "error": html_result["error"]}
            
            posts = html_result["posts"]
            
            if not posts:
                return {"success": False, "error": "No posts to export"}
            
            # Create WordPress XML
            rss = ET.Element('rss')
            rss.set('version', '2.0')
            rss.set('xmlns:excerpt', 'http://wordpress.org/export/1.2/excerpt/')
            rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
            rss.set('xmlns:wfw', 'http://wellformedweb.org/CommentAPI/')
            rss.set('xmlns:dc', 'http://purl.org/dc/elements/1.1/')
            rss.set('xmlns:wp', 'http://wordpress.org/export/1.2/')
            
            channel = ET.SubElement(rss, 'channel')
            
            # Channel information
            ET.SubElement(channel, 'title').text = 'WordPress Export'
            ET.SubElement(channel, 'link').text = 'https://wordpress.com'
            ET.SubElement(channel, 'description').text = 'WordPress export file'
            ET.SubElement(channel, 'pubDate').text = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
            ET.SubElement(channel, 'language').text = 'en-US'
            ET.SubElement(channel, 'wp:wxr_version').text = '1.2'
            ET.SubElement(channel, 'wp:base_site_url').text = 'https://wordpress.com'
            ET.SubElement(channel, 'wp:base_blog_url').text = 'https://wordpress.com'
            
            # Add posts
            for post_data in posts:
                item = ET.SubElement(channel, 'item')
                
                # Basic post information
                ET.SubElement(item, 'title').text = post_data["title"]
                ET.SubElement(item, 'link').text = post_data["permalink"]
                ET.SubElement(item, 'pubDate').text = datetime.datetime.fromisoformat(post_data["date"].replace('Z', '+00:00')).strftime('%a, %d %b %Y %H:%M:%S +0000')
                ET.SubElement(item, 'dc:creator').text = 'admin'
                
                # Content
                content = ET.SubElement(item, 'content:encoded')
                content.text = ET.CDATA(post_data["content"])
                
                # WordPress specific fields
                ET.SubElement(item, 'wp:post_id').text = str(random.randint(1000, 9999))
                ET.SubElement(item, 'wp:post_date').text = datetime.datetime.fromisoformat(post_data["date"].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                ET.SubElement(item, 'wp:post_date_gmt').text = datetime.datetime.fromisoformat(post_data["date"].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                ET.SubElement(item, 'wp:comment_status').text = 'open'
                ET.SubElement(item, 'wp:ping_status').text = 'open'
                ET.SubElement(item, 'wp:post_name').text = slugify(post_data["title"])
                ET.SubElement(item, 'wp:status').text = 'publish'
                ET.SubElement(item, 'wp:post_parent').text = '0'
                ET.SubElement(item, 'wp:menu_order').text = '0'
                ET.SubElement(item, 'wp:post_type').text = 'post'
                ET.SubElement(item, 'wp:post_password').text = ''
                
                # Add categories
                for category in post_data["categories"]:
                    cat = ET.SubElement(item, 'category')
                    cat.set('domain', 'category')
                    cat.set('nicename', slugify(category))
                    cat.text = category
                
                # Add tags
                for tag in post_data["tags"]:
                    tag_elem = ET.SubElement(item, 'category')
                    tag_elem.set('domain', 'post_tag')
                    tag_elem.set('nicename', slugify(tag))
                    tag_elem.text = tag
                
                # Featured image
                if post_data["featured_image"]:
                    postmeta = ET.SubElement(item, 'wp:postmeta')
                    ET.SubElement(postmeta, 'wp:meta_key').text = '_thumbnail_id'
                    ET.SubElement(postmeta, 'wp:meta_value').text = str(random.randint(100, 999))
            
            # Write to file
            output_file = WORDPRESS_XML_FILE
            tree = ET.ElementTree(rss)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            
            return {"success": True, "output_file": output_file}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_to_blogspot(self, posts_dir):
        """
        Export posts to Blogspot/Blogger XML format
        """
        try:
            # First convert to HTML
            html_result = self.export_to_html(posts_dir)
            
            if not html_result["success"]:
                return {"success": False, "error": html_result["error"]}
            
            posts = html_result["posts"]
            
            if not posts:
                return {"success": False, "error": "No posts to export"}
            
            # Create Blogspot XML
            feed = ET.Element('feed')
            feed.set('xmlns', 'http://www.w3.org/2005/Atom')
            feed.set('xmlns:blogger', 'http://schemas.google.com/blogger/2008')
            feed.set('xmlns:georss', 'http://www.georss.org/georss')
            feed.set('xmlns:gd', 'http://schemas.google.com/g/2005')
            feed.set('xmlns:thr', 'http://purl.org/syndication/thread/1.0')
            
            # Feed information
            ET.SubElement(feed, 'title').text = 'Blogspot Export'
            id_elem = ET.SubElement(feed, 'id')
            id_elem.text = f'tag:blogger.com,1999:blog-{random.randint(1000000000000, 9999999999999)}'
            ET.SubElement(feed, 'updated').text = datetime.datetime.now().isoformat()
            
            # Add posts
            for post_data in posts:
                entry = ET.SubElement(feed, 'entry')
                
                # Basic post information
                ET.SubElement(entry, 'id').text = f'tag:blogger.com,1999:blog-post-{random.randint(1000000000000, 9999999999999)}'
                ET.SubElement(entry, 'title').text = post_data["title"]
                
                # Published and updated dates
                published = ET.SubElement(entry, 'published')
                published.text = post_data["date"]
                updated = ET.SubElement(entry, 'updated')
                updated.text = post_data["date"]
                
                # Content
                content = ET.SubElement(entry, 'content')
                content.set('type', 'html')
                content.text = post_data["content"]
                
                # Author
                author = ET.SubElement(entry, 'author')
                ET.SubElement(author, 'name').text = 'Author'
                ET.SubElement(author, 'email').text = 'author@example.com'
                
                # Blogger specific fields
                ET.SubElement(entry, 'blogger:kind').text = 'post'
                
                # Add links
                link = ET.SubElement(entry, 'link')
                link.set('rel', 'alternate')
                link.set('type', 'text/html')
                link.set('href', post_data["permalink"])
                
                # Add categories/labels
                for category in post_data["categories"]:
                    cat = ET.SubElement(entry, 'category')
                    cat.set('scheme', 'http://www.blogger.com/atom/ns#')
                    cat.set('term', category)
                
                # Add tags as labels
                for tag in post_data["tags"]:
                    tag_elem = ET.SubElement(entry, 'category')
                    tag_elem.set('scheme', 'http://www.blogger.com/atom/ns#')
                    tag_elem.set('term', tag)
            
            # Write to file
            output_file = BLOGSPOT_XML_FILE
            tree = ET.ElementTree(feed)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            
            return {"success": True, "output_file": output_file}
            
        except Exception as e:
            return {"success": False, "error": str(e)}