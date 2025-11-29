import logging
from firecrawl import FirecrawlApp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import config

logger = logging.getLogger(__name__)

def get_article_content(url):
    """
    Scrape article content using Firecrawl.
    """
    if not config.FIRECRAWL_API_KEY:
        logger.error("FIRECRAWL_API_KEY not set.")
        return None

    logger.info(f"Scraping article: {url}")
    try:
        app = FirecrawlApp(api_key=config.FIRECRAWL_API_KEY)
        scrape_result = app.scrape_url(url, params={'formats': ['markdown']})
        
        if 'markdown' in scrape_result:
            return scrape_result['markdown']
        else:
            logger.warning(f"No markdown content found for {url}")
            return None
            
    except Exception as e:
        logger.error(f"Firecrawl scraping failed for {url}: {e}")
        return None

def get_youtube_transcript(video_id):
    """
    Fetch YouTube transcript.
    """
    logger.info(f"Fetching transcript for video: {video_id}")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript)
        return text
    except Exception as e:
        logger.error(f"Failed to get transcript for {video_id}: {e}")
        return None

def ingest_content(discovery_item):
    """
    Dispatcher function to get content based on source type.
    Returns the updated item with a 'content' field.
    """
    item = discovery_item.copy()
    content = None
    
    if item['source_type'] == 'rss' or item.get('source_type') == 'website':
        content = get_article_content(item['url'])
    elif item['source_type'] == 'youtube':
        content = get_youtube_transcript(item['video_id'])
        
    if content:
        item['content'] = content
        return item
    else:
        logger.warning(f"Failed to ingest content for {item['title']}")
        return None
