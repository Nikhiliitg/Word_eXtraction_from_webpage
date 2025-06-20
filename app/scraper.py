from playwright.async_api import async_playwright, TimeoutError

class Scraper:
    async def scrape_page(self, url: str) -> str:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Give it more time and reduce the wait condition
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)  # Extra 3s buffer
                content = await page.content()

                await browser.close()
                return content

        except TimeoutError:
            raise Exception("❌ Timeout while loading the page.")
        except Exception as e:
            raise Exception(f"Playwright scraping failed: {e}")