# tools.py - Search and scraping tools for TIC Compliance Agent

import os
import re
import json
import requests
from bs4 import BeautifulSoup
from typing import Optional


BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

# Domains to filter out (SEO spam, ads, low-quality)
NOISE_DOMAINS = {
    "amazon.com", "ebay.com", "alibaba.com", "aliexpress.com",
    "taobao.com", "jd.com", "pinterest.com", "youtube.com",
    "facebook.com", "twitter.com", "instagram.com",
    "quora.com", "reddit.com",  # sometimes useful, but filter for now
}

# High-quality regulatory/standards domains to prioritize
AUTHORITATIVE_DOMAINS = {
    "ec.europa.eu", "eur-lex.europa.eu", "europa.eu",
    "fcc.gov", "cpsc.gov", "fda.gov", "nist.gov",
    "iso.org", "iec.ch", "itu.int",
    "cnca.org.cn", "sac.gov.cn", "samr.gov.cn", "gb688.cn",
    "meti.go.jp", "mhlw.go.jp", "nite.go.jp",
    "ul.com", "tuvsud.com", "sgs.com", "bureauveritas.com",
    "intertek.com", "dekra.com",
    "bsigroup.com", "din.de", "afnor.org",
}


def search_regulations(query: str, count: int = 10) -> dict:
    """
    Search for regulatory information using Brave Search API.
    Returns filtered, de-noised results.
    
    Args:
        query: Search query string
        count: Number of results to request (max 10)
    
    Returns:
        dict with 'results' list and 'error' if any
    """
    if not BRAVE_API_KEY:
        return {"error": "BRAVE_API_KEY not configured", "results": []}
    
    try:
        resp = requests.get(
            BRAVE_SEARCH_URL,
            headers={
                "X-Subscription-Token": BRAVE_API_KEY,
                "Accept": "application/json",
            },
            params={"q": query, "count": count, "search_lang": "en"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        
        raw_results = data.get("web", {}).get("results", [])
        filtered = _filter_results(raw_results)
        
        return {
            "query": query,
            "results": filtered,
            "total_found": len(raw_results),
            "after_filter": len(filtered),
        }
    
    except requests.exceptions.Timeout:
        return {"error": "Search timed out", "results": [], "query": query}
    except requests.exceptions.RequestException as e:
        return {"error": f"Search failed: {str(e)}", "results": [], "query": query}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "results": [], "query": query}


def _filter_results(results: list) -> list:
    """
    Filter and score search results, removing noise.
    
    Scoring:
    - Authoritative domain: +3
    - Contains standard number pattern (e.g., EN 71, IEC 62133): +2
    - Contains regulatory keywords: +1
    - Noise domain: excluded
    """
    REGULATORY_KEYWORDS = [
        "regulation", "directive", "standard", "certification", "compliance",
        "requirement", "safety", "testing", "法规", "标准", "认证", "合规",
        "GB", "CE", "FCC", "PSE", "RoHS", "REACH", "WEEE", "CCC",
    ]
    
    STANDARD_NUMBER_PATTERN = re.compile(
        r'\b(EN|IEC|ISO|GB|UL|ASTM|ANSI|JIS|AS|NF|DIN|BS)\s*\d+[\d\-/\.]*\b|'
        r'\b(FCC|CE|RoHS|REACH|WEEE|CCC|PSE|PSC|TELEC)\b|'
        r'\b\d{4}/\d+/EC\b|'  # EU directives like 2009/48/EC
        r'\b\d{4}/\d+/EU\b',   # EU regulations like 2023/1542/EU
        re.IGNORECASE
    )
    
    filtered = []
    for r in results:
        url = r.get("url", "")
        title = r.get("title", "")
        description = r.get("description", "")
        
        # Extract domain
        domain = _extract_domain(url)
        
        # Skip noise domains
        if domain in NOISE_DOMAINS:
            continue
        
        # Skip if title looks like ad/commercial
        if _is_commercial_spam(title, description):
            continue
        
        # Score the result
        score = 0
        if domain in AUTHORITATIVE_DOMAINS:
            score += 3
        
        text = f"{title} {description}"
        if STANDARD_NUMBER_PATTERN.search(text):
            score += 2
        
        keyword_hits = sum(1 for kw in REGULATORY_KEYWORDS if kw.lower() in text.lower())
        score += min(keyword_hits, 3)  # cap at 3
        
        filtered.append({
            "title": title,
            "url": url,
            "description": description,
            "domain": domain,
            "relevance_score": score,
        })
    
    # Sort by relevance score
    filtered.sort(key=lambda x: x["relevance_score"], reverse=True)
    return filtered[:8]  # Return top 8


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def _is_commercial_spam(title: str, description: str) -> bool:
    """Detect SEO/commercial spam content."""
    SPAM_PATTERNS = [
        r'buy\s+\w+\s+cheap',
        r'best\s+price',
        r'free\s+shipping',
        r'order\s+now',
        r'discount\s+\d+%',
        r'click\s+here',
        r'wholesale',
        r'manufacturer.*supplier',
    ]
    
    text = f"{title} {description}".lower()
    return any(re.search(p, text, re.IGNORECASE) for p in SPAM_PATTERNS)


def fetch_page_content(url: str, max_chars: int = 5000) -> dict:
    """
    Fetch and extract text content from a regulatory/standards page.
    
    Args:
        url: Page URL to fetch
        max_chars: Maximum characters to return
    
    Returns:
        dict with 'content', 'title', 'url', and 'error' if any
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5,zh-CN;q=0.3",
        }
        
        resp = requests.get(url, timeout=12, headers=headers, allow_redirects=True)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Extract title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown"
        
        # Remove script, style, nav, footer elements
        for tag in soup(["script", "style", "nav", "footer", "header", 
                          "aside", "advertisement", "ads"]):
            tag.decompose()
        
        # Remove hidden elements
        for tag in soup.find_all(attrs={"style": re.compile(r"display\s*:\s*none", re.I)}):
            tag.decompose()
        
        # Try to find main content area
        main_content = (
            soup.find("main") or
            soup.find("article") or
            soup.find(attrs={"role": "main"}) or
            soup.find("div", attrs={"class": re.compile(r"content|main|article", re.I)}) or
            soup.find("body")
        )
        
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split("\n")]
        lines = [line for line in lines if line and len(line) > 10]  # Remove very short lines
        text = "\n".join(lines)
        
        # Truncate
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[content truncated]"
        
        return {
            "url": url,
            "title": title,
            "content": text,
            "char_count": len(text),
        }
    
    except requests.exceptions.Timeout:
        return {"url": url, "error": "Page fetch timed out", "content": ""}
    except requests.exceptions.HTTPError as e:
        return {"url": url, "error": f"HTTP error: {e.response.status_code}", "content": ""}
    except requests.exceptions.RequestException as e:
        return {"url": url, "error": f"Connection error: {str(e)}", "content": ""}
    except Exception as e:
        return {"url": url, "error": f"Parse error: {str(e)}", "content": ""}


# Tool definitions for OpenAI function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_regulations",
            "description": (
                "Search for regulatory requirements, standards, and compliance information "
                "for a product in a specific market. Returns filtered, high-quality results "
                "from regulatory bodies and standards organizations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Search query. Be specific: include product type, market/country, "
                            "and regulatory area. E.g., 'bluetooth headset CE certification EU RED directive', "
                            "'children toy EN 71 safety standard Europe'"
                        ),
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results to fetch (1-10, default 8)",
                        "default": 8,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_page_content",
            "description": (
                "Fetch and extract the text content from a specific webpage, such as a "
                "regulatory agency page, standards document, or official announcement. "
                "Use this to get detailed requirements from specific URLs found in search results."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL of the page to fetch",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum characters to return (default 5000)",
                        "default": 5000,
                    },
                },
                "required": ["url"],
            },
        },
    },
]


def execute_tool(tool_name: str, tool_args: dict) -> str:
    """
    Execute a tool by name with given arguments.
    Returns JSON string result.
    """
    if tool_name == "search_regulations":
        result = search_regulations(
            query=tool_args.get("query", ""),
            count=tool_args.get("count", 8),
        )
    elif tool_name == "fetch_page_content":
        result = fetch_page_content(
            url=tool_args.get("url", ""),
            max_chars=tool_args.get("max_chars", 5000),
        )
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    
    return json.dumps(result, ensure_ascii=False, indent=2)
