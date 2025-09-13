"""
Monitoring and scheduling system for NVIDIA Blog Scraper
"""

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

import schedule
from rich.console import Console

from .scraper import NVIDIABlogScraper

console = Console()


class ScraperMonitor:
    """Monitor and schedule scraping runs."""
    
    def __init__(self, config_path: str = "scraper_config.yaml"):
        """Initialize the monitor."""
        self.scraper = NVIDIABlogScraper(config_path)
        self.logger = logging.getLogger(__name__)
        self.last_run_file = Path("last_scrape_run.txt")
    
    def _record_run(self):
        """Record the timestamp of the last successful run."""
        with open(self.last_run_file, 'w') as f:
            f.write(datetime.now().isoformat())
    
    def _get_last_run(self) -> datetime:
        """Get the timestamp of the last run."""
        if self.last_run_file.exists():
            try:
                with open(self.last_run_file, 'r') as f:
                    return datetime.fromisoformat(f.read().strip())
            except:
                pass
        return datetime.min
    
    def should_run_update(self) -> bool:
        """Check if it's time for an update based on configuration."""
        if not self.scraper.config["monitoring"]["check_for_updates"]:
            return False
        
        last_run = self._get_last_run()
        interval_hours = self.scraper.config["monitoring"]["update_interval_hours"]
        next_run = last_run + timedelta(hours=interval_hours)
        
        return datetime.now() >= next_run
    
    def run_scheduled_scrape(self):
        """Run a scheduled scraping session."""
        console.print(f"[bold blue]🕐 Starting scheduled scrape at {datetime.now()}[/bold blue]")
        
        try:
            articles_count = self.scraper.scrape_blog()
            self._record_run()
            
            if articles_count > 0:
                console.print(f"[bold green]✅ Scheduled scrape completed: {articles_count} new articles[/bold green]")
            else:
                console.print("[bold yellow]ℹ️  Scheduled scrape completed: No new articles found[/bold yellow]")
            
            self.logger.info(f"Scheduled scrape completed: {articles_count} articles")
            
        except Exception as e:
            self.logger.error(f"Scheduled scrape failed: {e}")
            console.print(f"[bold red]❌ Scheduled scrape failed: {e}[/bold red]")
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        interval_hours = self.scraper.config["monitoring"]["update_interval_hours"]
        
        console.print(f"[bold green]🚀 Starting NVIDIA Blog Monitor[/bold green]")
        console.print(f"⏰ Checking for updates every {interval_hours} hours")
        console.print(f"📁 Output directory: {self.scraper.base_output_dir}")
        console.print("Press Ctrl+C to stop monitoring\n")
        
        # Schedule the scraping job
        schedule.every(interval_hours).hours.do(self.run_scheduled_scrape)
        
        # Run initial scrape if needed
        if self.should_run_update():
            console.print("[bold blue]Running initial scrape...[/bold blue]")
            self.run_scheduled_scrape()
        
        # Start the monitoring loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            console.print("\n[bold yellow]🛑 Monitoring stopped by user[/bold yellow]")


if __name__ == "__main__":
    monitor = ScraperMonitor()
    monitor.start_monitoring()
