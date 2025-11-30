import re
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup

from . import BaseTool


class FetchUrlTool(BaseTool):
    """
    Fetches a URL and returns its content.
    
    ## FetchUrl
    
    Fetches a web page and returns its title and text content.
    
    **Usage:**
    
    ```
    <FetchUrl url="https://example.com" />
    <FetchUrl url="https://docs.python.org/3/library/re.html" />
    ```
    
    **Attributes:**
    - url: The URL to fetch
    
    **Notes:**
    - Returns the page title and cleaned text content
    - Timeout: 30 seconds
    """

    FETCHURL_RE = re.compile(r"<FetchUrl\b([^>]*)/>", re.IGNORECASE)
    TIMEOUT = 30

    def process(self, mdx: str) -> Optional[Tuple[str, str]]:
        """Process FetchUrl tags. Returns (full_results, summary) or None."""
        parts = []
        summaries = []
        for match in self.FETCHURL_RE.finditer(mdx):
            attrs = self._parse_attrs(match.group(1))
            url = attrs.get("url")
            if not url:
                continue
            
            result = self._fetch_url(url)
            if result:
                title, content = result
                parts.append(f"=== URL: {url} ===\nTitle: {title}\n\n{content}")
                summaries.append(f"🌐 FETCHED {url}")
            else:
                parts.append(f"=== URL: {url} ===\n(Failed to fetch)")
                summaries.append(f"❌ {url} (failed)")
        
        if parts:
            return "\n\n".join(parts), "\n".join(summaries)
        return None

    def _fetch_url(self, url: str) -> Optional[Tuple[str, str]]:
        """Fetch URL and return (title, content) or None on failure."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; MuniBot/1.0)"
            }
            response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract title
            title = soup.title.string.strip() if soup.title and soup.title.string else "(No title)"
            
            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Get text content
            text = soup.get_text(separator="\n", strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            content = "\n".join(lines)
            
            # Truncate if too long
            if len(content) > 10000:
                content = content[:10000] + "\n\n... (truncated)"
            
            return title, content
            
        except requests.RequestException as e:
            return None
        except Exception as e:
            return None

