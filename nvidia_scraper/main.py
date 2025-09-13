"""
CLI interface for NVIDIA Blog Scraper
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .scraper import NVIDIABlogScraper
from .monitor import ScraperMonitor

console = Console()


@click.group()
@click.version_option()
def cli():
    """NVIDIA Blog Scraper - Collect AI/ML articles for knowledge base."""
    pass


@cli.command()
@click.option(
    '--config',
    '-c',
    default='scraper_config.yaml',
    help='Path to configuration file',
    type=click.Path(exists=True)
)
@click.option(
    '--max-articles',
    '-m',
    type=int,
    help='Maximum number of articles to scrape (overrides config)'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose output'
)
def scrape(config: str, max_articles: Optional[int], verbose: bool):
    """Scrape NVIDIA blogs for relevant articles."""
    try:
        console.print("[bold blue]Initializing NVIDIA Blog Scraper...[/bold blue]")
        
        scraper = NVIDIABlogScraper(config_path=config)
        
        if verbose:
            console.print(f"Configuration loaded from: {config}")
            console.print(f"Output directory: {scraper.base_output_dir}")
            console.print(f"Previously scraped URLs: {len(scraper.scraped_urls)}")
        
        articles_count = scraper.scrape_blog(max_articles=max_articles)
        
        if articles_count > 0:
            console.print(f"\n[bold green]✅ Successfully scraped {articles_count} articles![/bold green]")
            console.print(f"Articles saved to: {scraper.base_output_dir}")
        else:
            console.print("\n[bold yellow]ℹ️  No new articles found to scrape.[/bold yellow]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error during scraping: {e}[/bold red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option(
    '--config',
    '-c',
    default='scraper_config.yaml',
    help='Path to configuration file',
    type=click.Path(exists=True)
)
def status(config: str):
    """Show scraper status and statistics."""
    try:
        scraper = NVIDIABlogScraper(config_path=config)
        
        console.print("[bold blue]NVIDIA Blog Scraper Status[/bold blue]\n")
        console.print(f"📁 Output directory: {scraper.base_output_dir}")
        console.print(f"🔗 Previously scraped URLs: {len(scraper.scraped_urls)}")
        
        # Count articles by category
        if scraper.base_output_dir.exists():
            total_articles = 0
            for category_dir in scraper.base_output_dir.iterdir():
                if category_dir.is_dir() and category_dir.name != "__pycache__":
                    article_count = len(list(category_dir.glob("*"))) - (1 if (category_dir / "scraped_urls.txt").exists() else 0)
                    if article_count > 0:
                        console.print(f"  📂 {category_dir.name}: {article_count} articles")
                        total_articles += article_count
            
            console.print(f"\n📊 Total articles: {total_articles}")
        else:
            console.print("📊 No articles scraped yet")
        
        console.print(f"\n⚙️  Configuration:")
        console.print(f"  📝 Max articles per run: {scraper.config['output']['max_articles_per_run']}")
        console.print(f"  ⏱️  Delay between requests: {scraper.config['scraping']['delay_between_requests']}s")
        console.print(f"  📄 Article format: {scraper.config['output']['article_format']}")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error getting status: {e}[/bold red]")
        sys.exit(1)


@cli.command()
@click.option(
    '--config',
    '-c',
    default='scraper_config.yaml',
    help='Path to configuration file',
    type=click.Path(exists=True)
)
@click.confirmation_option(prompt='Are you sure you want to reset the scraper cache?')
def reset(config: str):
    """Reset scraper cache (will re-scrape all articles)."""
    try:
        scraper = NVIDIABlogScraper(config_path=config)
        
        scraped_file = scraper.base_output_dir / "scraped_urls.txt"
        if scraped_file.exists():
            scraped_file.unlink()
            console.print("[bold green]✅ Scraper cache reset successfully![/bold green]")
        else:
            console.print("[bold yellow]ℹ️  No cache file found to reset.[/bold yellow]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error resetting cache: {e}[/bold red]")
        sys.exit(1)


@cli.command()
@click.option(
    '--config',
    '-c',
    default='scraper_config.yaml',
    help='Path to configuration file',
    type=click.Path(exists=True)
)
def monitor(config: str):
    """Start automatic monitoring and scheduled scraping."""
    try:
        console.print("[bold blue]Starting NVIDIA Blog Monitor...[/bold blue]")
        monitor = ScraperMonitor(config_path=config)
        monitor.start_monitoring()
        
    except Exception as e:
        console.print(f"[bold red]❌ Error starting monitor: {e}[/bold red]")
        sys.exit(1)


if __name__ == '__main__':
    cli()
