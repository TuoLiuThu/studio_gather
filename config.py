import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") 

# 指定 Cookies 文件路径
YOUTUBE_COOKIES_PATH = os.path.join(os.path.dirname(__file__), 'cookies_burner.txt')

DATA_SOURCES = {
    # 1. AI 深度技术与工程
    "AI Engineering & Tech": [
        {
            # Substack 403 顽固，改用 Apple ID 尝试解析
            "name": "Latent Space",
            "apple_id": "1675357900",
            "type": "apple_podcast"
        },
        {
            "name": "Oxide and Friends",
            "url": "https://feeds.transistor.fm/oxide-and-friends",
            "type": "rss"
        },
        {
            "name": "SemiAnalysis",
            "url": "https://newsletter.semianalysis.com/feed", 
            "type": "rss"
        }
    ],

    # 2. 行业新闻与硬核半导体
    "Industry & Hardware": [
        {
            "name": "The AI Daily Brief",
            "apple_id": "1680633614",
            "type": "apple_podcast"
        },
        {
            # Substack 403 顽固，改用 Apple ID 尝试解析
            "name": "Fabricated Knowledge",
            "apple_id": "1656877017",
            "type": "apple_podcast"
        }
    ],

    # 3. 商业、创投与历史 (VC & Business)
    "VC & Business Strategy": [
        {
            "name": "Acquired",
            "url": "https://feeds.transistor.fm/acquired",
            "type": "rss"
        },
        {
            "name": "Dwarkesh Podcast",
            "url": "https://www.dwarkesh.com/feed",
            "type": "rss"
        },
        {
            "name": "No Priors",
            "apple_id": "1668002688", 
            "type": "apple_podcast"
        }
    ],

    # 4. 中文优质创投 (Chinese Tech & VC)
    "Chinese Tech Insights": [
        {
            "name": "OnBoard!",
            "apple_id": "1613083252",
            "type": "apple_podcast"
        },
        {
            "name": "乱翻书",
            "apple_id": "1591595410",
            "type": "apple_podcast"
        },
        {
            "name": "42章经",
            "apple_id": "1700299886",
            "type": "apple_podcast"
        }
    ],

    # 5. 深度对话与顶级投资人 (Deep Dialogues & General Investing)
    "Deep Dialogues": [
        {
            "name": "Lex Fridman Podcast",
            "url": "https://lexfridman.com/feed/podcast/",
            "type": "rss"
        },
        {
            "name": "Invest Like the Best",
            "url": "https://investlikethebest.libsyn.com/rss",
            "type": "rss"
        }
    ],

    # 6. 硅谷风向标 (Silicon Valley VC)
    "VC Trends": [
        {
            # 已修复：使用 Megaphone 新直链
            "name": "a16z Podcast",
            "url": "https://feeds.megaphone.fm/a16z",
            "type": "rss"
        },
        {
            # 已修复：Apple ID 1502871393 解析正确，保持不变
            "name": "All-In Podcast",
            "apple_id": "1502871393",
            "type": "apple_podcast"
        }
    ],

    # 7. AI 实战与中国视角 (AI Ops & China Tech)
    "AI Ops & Strategy": [
        {
            # 已修复：使用 Megaphone 新直链
            "name": "The Cognitive Revolution",
            "url": "https://feeds.megaphone.fm/cognitive-revolution",
            "type": "rss"
        },
        {
            # 已修复：使用 Megaphone 新直链
            "name": "Tech Buzz China",
            "url": "https://feeds.megaphone.fm/techbuzzchina",
            "type": "rss"
        }
    ]
}

# 保持 7 天回顾
LOOKBACK_HOURS = 168
