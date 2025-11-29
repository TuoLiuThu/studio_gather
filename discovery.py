import feedparser
import datetime
from datetime import timezone, timedelta
from dateutil import parser as date_parser
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_recent(published_date):
    """
    Check if the content was published within the configured lookback period.
    published_date: datetime object (timezone aware preferred)
    """
    if published_date is None:
        return False
    
    now = datetime.datetime.now(timezone.utc)
    
    # Ensure published_date is timezone aware. If not, assume UTC.
    if published_date.tzinfo is None:
        published_date = published_date.replace(tzinfo=timezone.utc)
        
    cutoff = now - timedelta(hours=config.LOOKBACK_HOURS)
    return published_date >= cutoff

def get_rss_posts(source):
    """
    Fetch recent posts from an RSS feed.
    """
    url = source['url']
    logger.info(f"Checking RSS feed: {url}")
    
    try:
        feed = feedparser.parse(url)
        if feed.bozo:
            logger.warning(f"Potential issue parsing feed {url}: {feed.bozo_exception}")
            
        recent_posts = []
        
        for entry in feed.entries:
            # Attempt to find publication date
            published_dt = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_dt = datetime.datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            
            if published_dt and is_recent(published_dt):
                logger.info(f"Found recent article: {entry.title}")
                recent_posts.append({
                    "title": entry.title,
                    "url": entry.link,
                    "published_at": published_dt.isoformat(),
                    "source_name": source['name'],
                    "source_type": "rss",
                    "category": "General" # Placeholder, can be refined
                })
        
        return recent_posts
        
    except Exception as e:
        logger.error(f"Error fetching RSS {url}: {e}")
        return []

def get_youtube_videos(source):
    """
    Fetch recent videos from a YouTube channel.
    """
    if not config.YOUTUBE_API_KEY:
        logger.warning("YOUTUBE_API_KEY not set, skipping YouTube source.")
        return []

    channel_id = source.get('channel_id')
    if not channel_id:
        logger.warning(f"No channel_id provided for YouTube source: {source['name']}")
        return []

    logger.info(f"Checking YouTube channel: {source['name']}")
    
    try:
        youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY)
        
        # Calculate RFC 3339 formatted date-time value (e.g., 1970-01-01T00:00:00Z)
        now = datetime.datetime.now(timezone.utc)
        published_after = (now - timedelta(hours=config.LOOKBACK_HOURS)).isoformat().replace('+00:00', 'Z')

        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            publishedAfter=published_after,
            type="video",
            maxResults=10
        )
        response = request.execute()
        
        recent_videos = []
        for item in response.get('items', []):
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            published_at = item['snippet']['publishedAt']
            
            logger.info(f"Found recent video: {title}")
            recent_videos.append({
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "video_id": video_id,
                "published_at": published_at,
                "source_name": source['name'],
                "source_type": "youtube",
                "category": "Video"
            })
            
        return recent_videos

    except HttpError as e:
        logger.error(f"YouTube API error for {source['name']}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching YouTube {source['name']}: {e}")
        return []

def discover_content():
    """
    Main discovery function to aggregate content from all sources.
    """
    all_content = []
    
    for category, sources in config.DATA_SOURCES.items():
        for source in sources:
            try:
                if source['type'] == 'rss':
                    posts = get_rss_posts(source)
                    # Tag with category from config
                    for p in posts: p['category'] = category 
                    all_content.extend(posts)
                elif source['type'] == 'youtube':
                    videos = get_youtube_videos(source)
                    for v in videos: v['category'] = category
                    all_content.extend(videos)
                # Add website crawling logic here if needed (using Firecrawl map/crawl)
            except Exception as e:
                logger.error(f"Unexpected error processing source {source['name']}: {e}")
                continue
                
    logger.info(f"Discovery complete. Found {len(all_content)} items.")
    return all_content

if __name__ == "__main__":
    # Test run
    results = discover_content()
    for item in results:
        print(f"- [{item['source_name']}] {item['title']} ({item['published_at']})")
