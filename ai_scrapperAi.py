import asyncio
from crawl4ai import AsyncWebCrawler

from bs4 import BeautifulSoup

def remove_html_tags(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return text

async def fetch_pages(base_url, pages=3):
    results = []

    async with AsyncWebCrawler() as crawler:
        for page in range(1, pages+1):

            url = f"{base_url}&page={page}"

            result = await crawler.arun(
                url,
                wait_until="networkidle",
                timeout=120000,
                scroll=True,
                delay_before_return_html=5
            )

            html = result.html
            text = remove_html_tags(html)

            results.append(text)

    return {"content": "\n".join(results)[:8000]}
# asyncio.run(fetch_pages("https://www.flipkart.com/search?q=top"))




