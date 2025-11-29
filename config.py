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
            # 改用子域名 RSS，避开 api.substack.com 的 403 封锁
            "name": "Latent Space",
            "url": "https://latentspace.substack.com/feed",
            "type": "rss"
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
            # 原链接 404，改为 Apple ID (The AI Daily Brief)
            "name": "The AI Daily Brief",
            "apple_id": "1680633614",
            "type": "apple_podcast"
        },
        {
            # 改用子域名 RSS
            "name": "Fabricated Knowledge",
            "url": "https://fabricatedknowledge.substack.com/feed",
            "type": "rss"
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
            # 原链接 404，改为 Apple ID (a16z Podcast)
            "name": "a16z Podcast",
            "apple_id": "1416869662",
            "type": "apple_podcast"
        },
        {
            # 原链接 404，改为 Apple ID (All-In with Chamath, Jason, Sacks & Friedberg)
            "name": "All-In Podcast",
            "apple_id": "1502871393",
            "type": "apple_podcast"
        }
    ],

    # 7. AI 实战与中国视角 (AI Ops & China Tech)
    "AI Ops & Strategy": [
        {
            # 原链接 404，改为 Apple ID (The Cognitive Revolution)
            "name": "The Cognitive Revolution",
            "apple_id": "1696784343",
            "type": "apple_podcast"
        },
        {
            # 原链接 404，改为 Apple ID (Tech Buzz China)
            "name": "Tech Buzz China",
            "apple_id": "1370215715",
            "type": "apple_podcast"
        }
    ]
}

# 保持 7 天回顾，确保能抓到周更节目
LOOKBACK_HOURS = 220
