import streamlit as st
import os
import time
from modules.article_generator import ArticleGenerator
from modules.exporter import Exporter
from modules.utils import validate_api_key, save_api_keys, load_api_keys
from modules.settings import IMAGES_FOLDER, OUTPUT_FOLDER

st.set_page_config(
    page_title="SEO Article Generator Ultimate",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create necessary directories
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #64748B;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D1FAE5;
        color: #065F46;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FEE2E2;
        color: #991B1B;
        margin: 1rem 0;
    }
    .upload-section {
        padding: 2rem;
        border: 2px dashed #E5E7EB;
        border-radius: 0.5rem;
        text-align: center;
        margin: 1rem 0;
        background-color: #F9FAFB;
    }
    .upload-section:hover {
        border-color: #3B82F6;
        background-color: #F3F4F6;
    }
    .file-list {
        margin-top: 1rem;
        padding: 1rem;
        background-color: white;
        border-radius: 0.5rem;
        border: 1px solid #E5E7EB;
    }
    .file-item {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .file-item:last-child {
        border-bottom: none;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state variables if they don't exist
    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = load_api_keys()
    
    if 'generator' not in st.session_state:
        st.session_state.generator = ArticleGenerator(st.session_state.api_keys)
    
    if 'exporter' not in st.session_state:
        st.session_state.exporter = Exporter()
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://i.ibb.co/sV8SHLP/seo-generator-logo.png", width=150)
        st.markdown("### Navigation")
        page = st.radio("", ["📝 Generate Articles", "⚙️ API Keys", "📤 Export Articles", "📁 Bulk Upload", "ℹ️ About"])
    
    # Display header
    st.markdown('<div class="main-header">SEO Article Generator Ultimate</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Powered by Gemini 1.5 Pro AI & Dual-Engine Image Search</div>', unsafe_allow_html=True)
    
    # Main content based on selected page
    if page == "📝 Generate Articles":
        display_generate_articles()
    elif page == "⚙️ API Keys":
        display_api_keys()
    elif page == "📤 Export Articles":
        display_export_articles()
    elif page == "📁 Bulk Upload":
        display_bulk_upload()
    else:
        display_about()
    
    # Footer
    st.markdown('<div class="footer">SEO Article Generator Ultimate v1.0 © 2025</div>', unsafe_allow_html=True)

def display_bulk_upload():
    st.markdown('<div class="section-header">Bulk Upload Articles</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # File uploader
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload your markdown (.md) or text (.txt) files",
            type=["md", "txt"],
            accept_multiple_files=True,
            help="You can upload multiple files at once. Files will be processed and saved in the _posts directory."
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_files:
            st.markdown("### Processing Files")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(uploaded_files):
                try:
                    # Update progress
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {file.name}...")
                    
                    # Read file content
                    content = file.read().decode('utf-8')
                    
                    # Save to _posts directory
                    output_path = os.path.join(OUTPUT_FOLDER, file.name)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    time.sleep(0.5)  # Small delay for visual feedback
                
                except Exception as e:
                    st.error(f"Error processing {file.name}: {str(e)}")
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            # Success message
            st.success(f"✅ Successfully processed {len(uploaded_files)} files")
            
            # Display file list
            st.markdown('<div class="file-list">', unsafe_allow_html=True)
            for file in uploaded_files:
                st.markdown(f'<div class="file-item">📄 {file.name}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def update_progress(stage, value, progress_bar, status_text):
    """Update the progress bar and status text during article generation"""
    progress_stages = {
        "title": {"message": "Generating SEO-optimized title...", "value": 20},
        "language": {"message": "Detecting language...", "value": 30},
        "article": {"message": "Generating article content...", "value": 50},
        "images": {"message": "Processing images...", "value": 70},
        "saving": {"message": "Saving article to file...", "value": 90}
    }
    
    if stage in progress_stages:
        status_text.text(progress_stages[stage]["message"])
        progress_bar.progress(progress_stages[stage]["value"])

def display_api_keys():
    st.markdown('<div class="section-header">API Key Management</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.markdown("""
        ### Gemini API Keys
        
        Add your Gemini API keys below. You can add multiple keys at once by pasting them in the text area, one key per line.
        
        [Get your Gemini API keys here](https://aistudio.google.com/app/apikey)
        """)
        
        # Display current API keys
        st.markdown("### Current API Keys")
        api_keys = st.session_state.api_keys
        
        if api_keys:
            for i, key in enumerate(api_keys):
                masked_key = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else "Invalid key format"
                st.code(f"Key {i+1}: {masked_key}")
            
            st.success(f"✅ {len(api_keys)} API key(s) loaded successfully")
        else:
            st.warning("⚠️ No API keys found. Please add your API keys below.")
        
        # Bulk API key input
        st.markdown("### Add API Keys")
        st.markdown("Paste your API keys below, one per line:")
        
        bulk_keys = st.text_area(
            "API Keys",
            height=150,
            help="Enter one API key per line. Invalid keys will be ignored."
        )
        
        if st.button("Add API Keys", use_container_width=True):
            if bulk_keys.strip():
                # Split input into individual keys
                new_keys = [key.strip() for key in bulk_keys.split('\n') if key.strip()]
                valid_keys = []
                invalid_keys = []
                duplicate_keys = []
                
                for key in new_keys:
                    if validate_api_key(key):
                        if key not in st.session_state.api_keys:
                            valid_keys.append(key)
                        else:
                            duplicate_keys.append(key)
                    else:
                        invalid_keys.append(key)
                
                # Add valid keys
                if valid_keys:
                    st.session_state.api_keys.extend(valid_keys)
                    save_api_keys(st.session_state.api_keys)
                    st.session_state.generator.api_keys = st.session_state.api_keys
                    st.success(f"✅ Successfully added {len(valid_keys)} new API key(s)")
                
                # Show warnings for invalid/duplicate keys
                if invalid_keys:
                    st.error(f"❌ {len(invalid_keys)} invalid API key(s) were ignored")
                if duplicate_keys:
                    st.warning(f"⚠️ {len(duplicate_keys)} duplicate API key(s) were ignored")
        
        # Remove API keys
        if api_keys:
            st.markdown("### Remove API Keys")
            
            key_to_remove = st.selectbox(
                "Select API key to remove:",
                [f"Key {i+1}: {key[:6]}...{key[-4:]}" for i, key in enumerate(api_keys)]
            )
            
            if st.button("Remove Selected API Key", use_container_width=True):
                index = int(key_to_remove.split(":")[0].replace("Key ", "")) - 1
                if 0 <= index < len(api_keys):
                    removed_key = api_keys.pop(index)
                    st.session_state.api_keys = api_keys
                    save_api_keys(api_keys)
                    st.session_state.generator.api_keys = api_keys
                    st.success(f"✅ API key removed successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_generate_articles():
    st.markdown('<div class="section-header">Generate SEO Articles</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        if not st.session_state.api_keys:
            st.warning("⚠️ No API keys found. Please add your Gemini API key in the API Keys section.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Single Article", "Batch Processing from File"],
            horizontal=True
        )
        
        if input_method == "Single Article":
            # Single article inputs
            subject = st.text_input("Enter article keyword/subject:")
            domain = st.text_input("Enter your domain:", value="bloggers.web.id")
            publisher = st.text_input("Enter publisher name:", value="Mas DEEe")
            
            col1, col2 = st.columns(2)
            with col1:
                category_option = st.radio(
                    "Category:",
                    ["Automatic (from subject)", "Custom category"]
                )
            
            with col2:
                if category_option == "Custom category":
                    category = st.text_input("Enter custom category:")
                else:
                    category = None
            
            model_choice = st.selectbox(
                "Select Gemini model:",
                ["gemini-1.5-flash", "gemini-1.5-pro"],
                index=0
            )
            
            # Generate button
            if st.button("🚀 Generate Article", type="primary", use_container_width=True):
                if not subject:
                    st.error("Please enter a subject for the article.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    return
                
                # Show progress
                with st.spinner("Generating article..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Update status
                    status_text.text("Initializing article generator...")
                    progress_bar.progress(10)
                    time.sleep(0.5)
                    
                    # Generate title
                    status_text.text("Generating SEO-optimized title...")
                    progress_bar.progress(20)
                    
                    # Set up the generator with current API keys
                    st.session_state.generator.api_keys = st.session_state.api_keys
                    
                    try:
                        # Generate the article
                        result = st.session_state.generator.generate_seo_article(
                            subject=subject,
                            domain=domain,
                            model_title=model_choice,
                            model_article=model_choice,
                            category=category,
                            publisher=publisher,
                            progress_callback=lambda stage, value: update_progress(stage, value, progress_bar, status_text)
                        )
                        
                        progress_bar.progress(100)
                        status_text.text("Article generated successfully!")
                        
                        # Display result
                        st.markdown('<div class="success-message">', unsafe_allow_html=True)
                        st.markdown(f"✅ **Successfully generated article!**")
                        st.markdown(f"**Title:** {result['title']}")
                        st.markdown(f"**Permalink:** {domain}{result['permalink']}")
                        st.markdown(f"**Saved to:** {result['file_path']}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Preview button
                        if st.button("Preview Article Content"):
                            st.markdown("### Article Preview")
                            st.markdown(result['article'])
                    
                    except Exception as e:
                        progress_bar.progress(100)
                        st.markdown('<div class="error-message">', unsafe_allow_html=True)
                        st.markdown(f"❌ **Error generating article:**")
                        st.markdown(f"{str(e)}")
                        st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # Batch processing
            st.markdown("### Batch Processing from subjects.txt")
            
            # Check if subjects.txt exists
            if os.path.exists("subjects.txt"):
                with open("subjects.txt", "r", encoding="utf-8") as f:
                    subjects = [line.strip() for line in f if line.strip()]
                
                st.info(f"Found {len(subjects)} subjects in subjects.txt")
                
                # Display the first few subjects
                if subjects:
                    st.markdown("**Sample subjects:**")
                    for subject in subjects[:5]:
                        st.markdown(f"- {subject}")
                    if len(subjects) > 5:
                        st.markdown(f"- ... and {len(subjects) - 5} more")
            else:
                subjects = []
                st.warning("subjects.txt file not found. Create a text file with one subject per line.")
                
                # File uploader for subjects.txt
                uploaded_file = st.file_uploader("Upload subjects.txt file", type=["txt"])
                if uploaded_file is not None:
                    # Save the uploaded file
                    with open("subjects.txt", "wb") as f:
                        f.write(uploaded_file.getvalue())
                    st.success("subjects.txt file uploaded successfully!")
                    
                    # Read the subjects
                    with open("subjects.txt", "r", encoding="utf-8") as f:
                        subjects = [line.strip() for line in f if line.strip()]
                    st.info(f"Found {len(subjects)} subjects in uploaded file")
            
            # Batch processing options
            if subjects:
                st.markdown("### Batch Processing Options")
                domain = st.text_input("Enter your domain for all articles:", value="bloggers.web.id")
                publisher = st.text_input("Enter publisher name for all articles:", value="Mas DEEe")
                
                category_option = st.radio(
                    "Category for all articles:",
                    ["Automatic (from each subject)", "One category for all articles"]
                )
                
                if category_option == "One category for all articles":
                    category = st.text_input("Enter category for all articles:")
                else:
                    category = None
                
                model_choice = st.selectbox(
                    "Select Gemini model for batch processing:",
                    ["gemini-1.5-flash", "gemini-1.5-pro"],
                    index=0
                )
                
                # Start batch processing button
                if st.button("🚀 Start Batch Processing", type="primary", use_container_width=True):
                    # Show progress
                    progress_placeholder = st.empty()
                    status_text = st.empty()
                    article_results = st.empty()
                    
                    batch_results = []
                    errors = []
                    
                    # Set up the generator with current API keys
                    st.session_state.generator.api_keys = st.session_state.api_keys
                    
                    for idx, subject in enumerate(subjects):
                        try:
                            # Update progress
                            progress = int((idx / len(subjects)) * 100)
                            progress_placeholder.progress(progress)
                            status_text.text(f"Processing {idx+1}/{len(subjects)}: {subject}")
                            
                            # Generate the article
                            result = st.session_state.generator.generate_seo_article(
                                subject=subject,
                                domain=domain,
                                model_title=model_choice,
                                model_article=model_choice,
                                category=category,
                                publisher=publisher
                            )
                            
                            batch_results.append({
                                "subject": subject,
                                "title": result["title"],
                                "permalink": result["permalink"],
                                "file_path": result["file_path"]
                            })
                            
                            # Display incremental results
                            article_results.markdown(f"✅ **Generated ({idx+1}/{len(subjects)}):** {result['title']}")
                            
                        except Exception as e:
                            errors.append({"subject": subject, "error": str(e)})
                            article_results.markdown(f"❌ **Error with \"{subject}\":** {str(e)}")
                    
                    # Complete the progress
                    progress_placeholder.progress(100)
                    status_text.text("Batch processing completed!")
                    
                    # Display summary
                    st.markdown("### Batch Processing Summary")
                    st.markdown(f"✅ **Successfully generated:** {len(batch_results)} articles")
                    st.markdown(f"❌ **Errors:** {len(errors)} articles")
                    
                    if errors:
                        with st.expander("View Errors"):
                            for error in errors:
                                st.markdown(f"- **{error['subject']}:** {error['error']}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_export_articles():
    st.markdown('<div class="section-header">Export Articles</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.markdown("""
        ### Export Generated Articles
        
        Export your generated articles to different formats for publishing on various platforms.
        """)
        
        # Check if any articles exist
        article_files = []
        if os.path.exists(OUTPUT_FOLDER):
            article_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.md')]
        
        if article_files:
            st.success(f"✅ Found {len(article_files)} articles ready for export")
            
            # Sort files by date (newest first)
            article_files.sort(reverse=True)
            
            # Display sample of articles
            with st.expander("View Available Articles"):
                for file in article_files[:10]:
                    st.markdown(f"- {file}")
                if len(article_files) > 10:
                    st.markdown(f"- ... and {len(article_files) - 10} more")
            
            # Export options
            st.markdown("### Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Export to HTML", use_container_width=True):
                    with st.spinner("Exporting to HTML..."):
                        result = st.session_state.exporter.export_to_html(OUTPUT_FOLDER)
                        if result["success"]:
                            st.success(f"✅ Successfully exported {result['count']} articles to HTML")
                            if "output_dir" in result:
                                st.info(f"Output directory: {result['output_dir']}")
                        else:
                            st.error(f"❌ Error exporting to HTML: {result['error']}")
            
            with col2:
                if st.button("🔄 Export to WordPress XML", use_container_width=True):
                    with st.spinner("Exporting to WordPress XML..."):
                        result = st.session_state.exporter.export_to_wordpress(OUTPUT_FOLDER)
                        if result["success"]:
                            st.success(f"✅ Successfully exported to WordPress XML")
                            if "output_file" in result:
                                st.info(f"Output file: {result['output_file']}")
                                
                                # Download button
                                with open(result["output_file"], "rb") as file:
                                    st.download_button(
                                        label="Download WordPress XML",
                                        data=file,
                                        file_name=os.path.basename(result["output_file"]),
                                        mime="application/xml"
                                    )
                        else:
                            st.error(f"❌ Error exporting to WordPress XML: {result['error']}")
            
            with col3:
                if st.button("🔄 Export to Blogspot XML", use_container_width=True):
                    with st.spinner("Exporting to Blogspot XML..."):
                        result = st.session_state.exporter.export_to_blogspot(OUTPUT_FOLDER)
                        if result["success"]:
                            st.success(f"✅ Successfully exported to Blogspot XML")
                            if "output_file" in result:
                                st.info(f"Output file: {result['output_file']}")
                                
                                # Download button
                                with open(result["output_file"], "rb") as file:
                                    st.download_button(
                                        label="Download Blogspot XML",
                                        data=file,
                                        file_name=os.path.basename(result["output_file"]),
                                        mime="application/xml"
                                    )
                        else:
                            st.error(f"❌ Error exporting to Blogspot XML: {result['error']}")
            
            # Export all button
            if st.button("🔄 Export All Formats", type="primary", use_container_width=True):
                with st.spinner("Exporting to all formats..."):
                    # Export to HTML
                    html_result = st.session_state.exporter.export_to_html(OUTPUT_FOLDER)
                    
                    # Export to WordPress XML
                    wp_result = st.session_state.exporter.export_to_wordpress(OUTPUT_FOLDER)
                    
                    # Export to Blogspot XML
                    bs_result = st.session_state.exporter.export_to_blogspot(OUTPUT_FOLDER)
                    
                    # Display results
                    if html_result["success"]:
                        st.success(f"✅ HTML Export: {html_result['count']} articles exported successfully")
                    else:
                        st.error(f"❌ HTML Export: {html_result['error']}")
                    
                    if wp_result["success"]:
                        st.success(f"✅ WordPress XML Export: Completed successfully")
                        # Download button
                        if "output_file" in wp_result:
                            with open(wp_result["output_file"], "rb") as file:
                                st.download_button(
                                    label="Download WordPress XML",
                                    data=file,
                                    file_name=os.path.basename(wp_result["output_file"]),
                                    mime="application/xml"
                                )
                    else:
                        st.error(f"❌ WordPress XML Export: {wp_result['error']}")
                    
                    if bs_result["success"]:
                        st.success(f"✅ Blogspot XML Export: Completed successfully")
                        # Download button
                        if "output_file" in bs_result:
                            with open(bs_result["output_file"], "rb") as file:
                                st.download_button(
                                    label="Download Blogspot XML",
                                    data=file,
                                    file_name=os.path.basename(bs_result["output_file"]),
                                    mime="application/xml"
                                )
                    else:
                        st.error(f"❌ Blogspot XML Export: {bs_result['error']}")
        else:
            st.warning("⚠️ No articles found for export. Generate articles first.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_about():
    st.markdown('<div class="section-header">About SEO Article Generator</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.markdown("""
        ### SEO Article Generator Ultimate v1.0
        
        This application generates high-quality, SEO-optimized articles using Google's Gemini 1.5 AI models. 
        Articles are automatically enhanced with images from dual search engines (Bing + Yahoo) for optimal content matching.
        
        #### Features:
        
        - **AI-Powered Content**: Utilizes Gemini 1.5 Pro/Flash for human-like, engaging content
        - **SEO Optimization**: Creates articles with proper keyword density, LSI keywords, and internal linking
        - **Image Integration**: Automatically searches and adds relevant images to each article
        - **Multiple Export Options**: Export to HTML, WordPress XML, and Blogspot XML
        - **Batch Processing**: Generate multiple articles from a list of subjects
        - **API Key Management**: Rotate between multiple API keys to avoid rate limits
        
        #### Requirements:
        
        - Gemini API key(s) - Get yours at [Google AI Studio](https://aistudio.google.com/app/apikey)
        - Internet connection for image search and API access
        
        #### Usage Tips:
        
        - For best results, use specific, detailed subjects rather than broad topics
        - Add multiple API keys for faster batch processing
        - Articles are saved in the `_posts` directory in Jekyll-compatible format
        - Images are saved in the `assets/image` directory
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
