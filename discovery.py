import feedparser
import datetime
from datetime import timezone, timedelta
from dateutil import parser as date_parser
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import config
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_recent(published_date):
    """
    Check if the content was published within the configured lookback period.
    """
    if published_date is None:
        return False
    
    now = datetime.datetime.now(timezone.utc)
    
    if published_date.tzinfo is None:
        published_date = published_date.replace(tzinfo=timezone.utc)
        
    cutoff = now - timedelta(hours=config.LOOKBACK_HOURS)
    return published_date >= cutoff

def get_feed_from_apple_id(apple_id):
    """
    Resolve Apple Podcast ID to an RSS Feed URL using iTunes API.
    """
    try:
        # iTunes API 查找接口
        api_url = f"https://itunes.apple.com/lookup?id={apple_id}&entity=podcast"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if data.get("resultCount", 0) > 0:
            feed_url = data["results"][0].get("feedUrl")
            if feed_url:
                logger.info(f"Resolved Apple ID {apple_id} to RSS: {feed_url}")
                return feed_url
            
        logger.warning(f"No feedUrl found for Apple ID {apple_id}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to resolve Apple ID {apple_id}: {e}")
        return None

def get_rss_posts(source, override_url=None):
    """
    Fetch recent posts from an RSS feed with User-Agent spoofing.
    """
    url = override_url if override_url else source.get('url')
    
    if not url:
        logger.error(f"No URL provided for source {source['name']}")
        return []

    logger.info(f"Checking RSS feed: {url}")
    
    try:
        # === 修改处：增加 User-Agent 头，防止 Substack 等平台拦截 ===
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, application/atom+xml, text/xml;q=0.9, */*;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 将获取到的内容传给 feedparser
        content_stream = io.BytesIO(response.content)
        feed = feedparser.parse(content_stream)
        
        if feed.bozo:
            logger.warning(f"Potential issue parsing feed {url}: {feed.bozo_exception}")
            # 注意：即便 bozo 为真，feedparser 经常也能解析出部分内容，所以不直接 return
            
        recent_posts = []
        
        for entry in feed.entries:
            published_dt = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_dt = datetime.datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            
            # 如果解析不到时间，尝试直接取 updated 字符串（部分 RSS 格式不规范）
            if not published_dt and hasattr(entry, 'updated'):
                 try:
                     published_dt = date_parser.parse(entry.updated)
                     if published_dt.tzinfo is None:
                         published_dt = published_dt.replace(tzinfo=timezone.utc)
                 except:
                     pass

            if published_dt and is_recent(published_dt):
                logger.info(f"Found recent article: {entry.title}")
                recent_posts.append({
                    "title": entry.title,
                    "url": entry.link,
                    "published_at": published_dt.isoformat(),
                    "source_name": source['name'],
                    "source_type": "rss",
                    "category": source.get('category', "General")
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
                source['category'] = category 

                if source['type'] == 'rss':
                    posts = get_rss_posts(source)
                    all_content.extend(posts)
                    
                elif source['type'] == 'youtube':
                    videos = get_youtube_videos(source)
                    all_content.extend(videos)
                
                elif source['type'] == 'apple_podcast':
                    rss_url = get_feed_from_apple_id(source['apple_id'])
                    if rss_url:
                        posts = get_rss_posts(source, override_url=rss_url)
                        all_content.extend(posts)

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
