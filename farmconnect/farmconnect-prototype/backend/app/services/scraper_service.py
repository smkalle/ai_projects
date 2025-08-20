
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from bs4 import BeautifulSoup
import re

from ..core.config import settings
from ..core.database import get_db
from ..models.price_history import PriceHistory

logger = logging.getLogger(__name__)

class ScraperService:
    """AI-powered price scraping service inspired by ScrapeCraft"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.scraping_active = False
        self.supported_platforms = {
            "bigbasket": {
                "base_url": "https://www.bigbasket.com",
                "search_url": "https://www.bigbasket.com/ps/?q={query}",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            },
            "zepto": {
                "base_url": "https://www.zepto.com",
                "search_url": "https://www.zepto.com/search?query={query}",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            },
            "swiggy": {
                "base_url": "https://www.swiggy.com",
                "search_url": "https://www.swiggy.com/instamart/search?custom_back=true&query={query}",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            }
        }

    async def start_periodic_scraping(self):
        """Start periodic scraping of all platforms"""
        self.scraping_active = True
        self.session = aiohttp.ClientSession()

        logger.info("Starting periodic price scraping...")

        while self.scraping_active:
            try:
                await self._scrape_all_platforms()
                # Wait 5 minutes between scraping cycles
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Error in periodic scraping: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def stop(self):
        """Stop the scraping service"""
        self.scraping_active = False
        if self.session:
            await self.session.close()
        logger.info("Scraper service stopped")

    async def health_check(self) -> str:
        """Check if scraper service is healthy"""
        return "running" if self.scraping_active else "stopped"

    async def scrape_product_prices(self, product_name: str, category: str) -> Dict[str, float]:
        """Scrape prices for a specific product across all platforms"""

        if not self.session:
            self.session = aiohttp.ClientSession()

        prices = {}

        for platform_name, platform_config in self.supported_platforms.items():
            try:
                price = await self._scrape_platform_price(
                    platform_name, 
                    platform_config, 
                    product_name
                )
                if price:
                    prices[platform_name] = price

            except Exception as e:
                logger.error(f"Error scraping {platform_name} for {product_name}: {str(e)}")

        return prices

    async def _scrape_platform_price(
        self, 
        platform_name: str, 
        platform_config: Dict, 
        product_name: str
    ) -> Optional[float]:
        """Scrape price from a specific platform"""

        try:
            # Format search URL
            search_url = platform_config["search_url"].format(
                query=product_name.replace(" ", "+")
            )

            # Make request with proper headers
            async with self.session.get(
                search_url,
                headers=platform_config["headers"],
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                if response.status != 200:
                    logger.warning(f"Failed to fetch {platform_name}: {response.status}")
                    return None

                html = await response.text()
                price = self._extract_price_from_html(html, platform_name, product_name)

                return price

        except asyncio.TimeoutError:
            logger.warning(f"Timeout scraping {platform_name} for {product_name}")
        except Exception as e:
            logger.error(f"Error scraping {platform_name}: {str(e)}")

        return None

    def _extract_price_from_html(
        self, 
        html: str, 
        platform_name: str, 
        product_name: str
    ) -> Optional[float]:
        """Extract price from HTML using platform-specific selectors"""

        soup = BeautifulSoup(html, 'html.parser')

        # Platform-specific price extraction logic
        price_selectors = {
            "bigbasket": [
                ".Price___StyledLabel-sc-pldi2d-1",
                ".price",
                "[data-cy='price']"
            ],
            "zepto": [
                ".price-display",
                ".product-price",
                "[data-testid='price']"
            ],
            "swiggy": [
                ".price",
                ".product-price-container",
                "[data-cy='product-price']"
            ]
        }

        selectors = price_selectors.get(platform_name, [".price"])

        for selector in selectors:
            price_elements = soup.select(selector)

            for element in price_elements:
                price_text = element.get_text().strip()
                price = self._extract_price_from_text(price_text)

                if price:
                    logger.info(f"Found price {price} for {product_name} on {platform_name}")
                    return price

        logger.warning(f"No price found for {product_name} on {platform_name}")
        return None

    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract numeric price from text"""

        # Remove common currency symbols and text
        cleaned_text = re.sub(r'[₹$€£,]', '', text)
        cleaned_text = re.sub(r'[^0-9.]', '', cleaned_text)

        # Find price pattern
        price_match = re.search(r'(\d+\.?\d*)', cleaned_text)

        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                pass

        return None
