import logging
import argparse
import discovery
import ingest
import analyzer
import notifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("aggregator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Daily AI Investment Insider Aggregator")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending email")
    args = parser.parse_args()

    logger.info("Starting Daily AI Investment Aggregator...")

    # 1. Discovery
    logger.info("Phase 1: Discovery")
    items = discovery.discover_content()
    if not items:
        logger.info("No new content found. Exiting.")
        return

    # 2. Ingest & Analyze
    logger.info("Phase 2: Ingest & Analyze")
    analyzed_items = []
    
    for item in items:
        # Ingest
        item_with_content = ingest.ingest_content(item)
        if not item_with_content:
            continue
            
        # Analyze
        analyzed_item = analyzer.analyze_content(item_with_content)
        if analyzed_item:
            analyzed_items.append(analyzed_item)
        else:
            logger.warning(f"Skipping {item['title']} due to analysis failure.")

    # 3. Notify
    logger.info("Phase 3: Notify")
    if analyzed_items:
        html_report = notifier.generate_html_report(analyzed_items)
        
        if args.dry_run:
            logger.info("Dry run enabled. Saving report to disk.")
            with open("dry_run_report.html", "w", encoding="utf-8") as f:
                f.write(html_report)
        else:
            subject = f"AI Investment Insider - {len(analyzed_items)} New Updates"
            notifier.send_email(subject, html_report)
    else:
        logger.info("No items successfully analyzed.")

    logger.info("Job complete.")

if __name__ == "__main__":
    main()
