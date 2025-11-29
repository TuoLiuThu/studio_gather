import google.generativeai as genai
import json
import logging
import config
import typing_extensions as typing

logger = logging.getLogger(__name__)

# Configure Gemini
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

# Define the output schema for structured generation
class InvestmentInsight(typing.TypedDict):
    title_en: str
    title_cn: str
    summary_cn: str
    key_insight: str
    category: str

def analyze_content(item):
    """
    Analyze content using Gemini to generate an investment summary.
    """
    if not config.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set.")
        return None

    content = item.get('content')
    if not content:
        return None

    logger.info(f"Analyzing content: {item['title']}")
    
    # Truncate content if too long (simple safety check, though Gemini context is large)
    # 1 token ~= 4 chars. 1M tokens is huge, but let's be safe with 100k chars for now to avoid timeouts/costs if not needed.
    truncated_content = content[:100000] 

    prompt = f"""
    You are a private equity technology investment manager. 
    Read the following content and generate a structured JSON output.
    
    Content Title: {item['title']}
    Content Source: {item['source_name']}
    
    Content Body:
    {truncated_content}
    
    Requirements:
    1. title_en: Original title or cleaned up English title.
    2. title_cn: Professional Chinese translation of the title.
    3. summary_cn: A detailed summary in Chinese. Keep professional technical terms in English (e.g., "Transformer", "Wafer", "CoWoS").
    4. key_insight: The single most important investment takeaway or market implication (in Chinese).
    5. category: Choose one of [Hardware, Model, App, Infrastructure, Policy].
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-pro') # Using 2.5 Pro as proxy for "3 Pro"
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=InvestmentInsight
            )
        )
        
        result = json.loads(response.text)
        
        # Merge analysis with original item
        item.update(result)
        return item

    except Exception as e:
        logger.error(f"Gemini analysis failed for {item['title']}: {e}")
        return None


