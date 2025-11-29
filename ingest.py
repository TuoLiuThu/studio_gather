import logging
import time      # <--- 新增
import random    # <--- 新增
import os        # <--- 新增
from firecrawl import FirecrawlApp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import config

logger = logging.getLogger(__name__)

def get_article_content(url):
    # ... (保持原样不变) ...
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
    Fetch YouTube transcript using Cookies for authentication
    and fallback mechanisms.
    """
    logger.info(f"Fetching transcript for video: {video_id}")
    
    # === 修改 1: 检查 Cookies 文件是否存在 ===
    cookies_path = config.YOUTUBE_COOKIES_PATH
    if not os.path.exists(cookies_path):
        logger.warning(f"Cookies file not found at {cookies_path}, trying anonymous access (High Risk of Failure).")
        cookies_path = None # 如果文件丢了，尝试裸奔（虽然大概率失败）

    try:
        # === 修改 2: 传入 cookies 参数 ===
        # 这就是你解决 "Subtitles disabled" 的关键
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookies_path)

        # 智能查找 (优先手动英文 -> 自动生成英文)
        transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])

        # 下载数据
        transcript_data = transcript.fetch()

        # 格式化
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript_data)
        return text

    except Exception as e:
        logger.error(f"Failed to get transcript for {video_id}: {e}")
        
        # 最后的尝试：翻译回落
        try:
            # 同样需要带上 Cookies 重试
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookies_path)
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
    Dispatcher function with Rate Limiting for YouTube.
    """
    item = discovery_item.copy()
    content = None
    
    source_type = item.get('source_type')

    if source_type == 'rss' or source_type == 'website':
        content = get_article_content(item['url'])
        
    elif source_type == 'youtube':
        content = get_youtube_transcript(item['video_id'])
        
        # === 修改 3: 针对 YouTube 的强制随机休眠 (Rate Limiting) ===
        # 这是为了保护你的新号不被 Google 判定为机器人
        # 处理完一个视频后，随机休息 10 到 30 秒
        sleep_time = random.uniform(10, 30)
        logger.info(f"YouTube rate limiting: Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
        
    if content:
        item['content'] = content
        return item
    else:
        logger.warning(f"Failed to ingest content for {item['title']}")
        return None