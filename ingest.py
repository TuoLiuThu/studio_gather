import logging
import time
import random
import os
import re
from firecrawl import FirecrawlApp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import yt_dlp  # 必须安装: pip install yt-dlp
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

def clean_vtt_text(vtt_content):
    """
    Helper function to clean VTT subtitle format to plain text.
    """
    lines = vtt_content.splitlines()
    text_lines = []
    # 简单的去重和清洗逻辑
    seen = set()
    for line in lines:
        # 跳过时间轴 (e.g., 00:00:00.000 --> 00:00:05.000) 和 WEBVTT 头
        if '-->' in line or line.strip() == 'WEBVTT' or not line.strip():
            continue
        # 去除 HTML 标签 (e.g., <c.colorE5E5E5>)
        clean_line = re.sub(r'<[^>]+>', '', line).strip()
        # 去除重复行 (歌词或字幕常有重复)
        if clean_line and clean_line not in seen:
            seen.add(clean_line)
            text_lines.append(clean_line)
    return " ".join(text_lines)

def get_transcript_with_ytdlp(video_id, cookies_path):
    """
    Fallback method: Use yt-dlp to download subtitles.
    """
    logger.info(f"Fallback: Trying yt-dlp for {video_id}...")
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en', 'zh-Hans'],
        'cookiefile': cookies_path, # 使用同样的 cookies
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 检查是否有字幕
            subtitles = info.get('requested_subtitles')
            if not subtitles:
                # 尝试再次查找，有时候 yt-dlp 逻辑不一样
                if 'en' in info.get('subtitles', {}):
                    sub_url = info['subtitles']['en'][0]['url']
                elif 'en' in info.get('automatic_captions', {}):
                    sub_url = info['automatic_captions']['en'][0]['url']
                else:
                    return None
            else:
                # 优先取英文
                if 'en' in subtitles:
                    sub_url = subtitles['en']['url']
                else:
                    # 取第一个可用的
                    key = list(subtitles.keys())[0]
                    sub_url = subtitles[key]['url']
            
            # 下载字幕内容
            import requests
            # 这里的 sub_url 通常是 json3 或 vtt 格式，yt-dlp 获取的 url 可以直接下载
            res = requests.get(sub_url)
            if res.status_code == 200:
                # 简单清洗 VTT/JSON 格式 (这里假设是 VTT 或类文本)
                return clean_vtt_text(res.text)
            
    except Exception as e:
        logger.error(f"yt-dlp fallback failed: {e}")
    
    return None

def get_youtube_transcript(video_id):
    """
    Fetch YouTube transcript using Cookies, with yt-dlp fallback.
    """
    logger.info(f"Fetching transcript for video: {video_id}")
    
    cookies_path = config.YOUTUBE_COOKIES_PATH
    if not os.path.exists(cookies_path):
        logger.warning(f"Cookies file not found at {cookies_path}, trying anonymous access.")
        cookies_path = None

    # === 策略 1: 尝试 youtube_transcript_api ===
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookies_path)
        transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        transcript_data = transcript.fetch()
        formatter = TextFormatter()
        return formatter.format_transcript(transcript_data)

    except Exception as e:
        error_msg = str(e)
        logger.warning(f"Standard API failed for {video_id}: {error_msg}")
        
        # 如果是 429 错误，记录严重警告，但继续尝试 fallback (yt-dlp 抗封锁能力更强)
        if "Too Many Requests" in error_msg:
            logger.warning("Hit 429 Rate Limit on standard API. Switching to yt-dlp immediately.")
        
        # === 策略 2: 启动 yt-dlp 兜底 ===
        fallback_content = get_transcript_with_ytdlp(video_id, cookies_path)
        if fallback_content:
            logger.info(f"Successfully retrieved transcript using yt-dlp for {video_id}")
            return fallback_content

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
        
        # 即使失败了也要 sleep，防止死循环轰炸
        sleep_time = random.uniform(20, 40) # 稍微增加一点等待时间
        logger.info(f"YouTube rate limiting: Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
        
    if content:
        item['content'] = content
        return item
    else:
        logger.warning(f"Failed to ingest content for {item['title']}")
        return None
