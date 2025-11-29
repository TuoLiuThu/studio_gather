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
    Fetch YouTube transcript with fallback to auto-generated captions.
    """
    logger.info(f"Fetching transcript for video: {video_id}")
    try:
        # 1. 获取该视频的所有字幕列表 (List all available transcripts)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # 2. 智能查找英语字幕 (Smart find)
        # 这行代码会自动查找手动上传的('en')，如果没有，会自动查找自动生成的('en')
        # 同时也支持 en-US, en-GB 等变体
        transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])

        # 3. 下载字幕数据
        transcript_data = transcript.fetch()

        # 4. 格式化为纯文本
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript_data)
        return text

    except Exception as e:
        # 如果标准方法失败，记录详细错误
        logger.error(f"Failed to get transcript for {video_id}: {e}")
        
        # 最后的尝试：如果有非英语字幕，尝试调用翻译（可选，防止报错退出）
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for t in transcript_list:
                if t.is_translatable:
                    logger.info(f"Trying to translate {t.language} to English...")
                    translated_transcript = t.translate('en').fetch()
                    formatter = TextFormatter()
                    return formatter.format_transcript(translated_transcript)
        except Exception as trans_e:
             logger.error(f"Translation fallback also failed: {trans_e}")
        
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
