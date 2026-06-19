import httpx
from love_crawler import AsyncWebCrawler
import os

love_index_URL = os.getenv("love_index_URL", "http://127.0.0.1:8090/love_indexsearch.json")

async def search_love_index(query: str, max_results: int = 5) -> str:
    """Query the love_index search server."""
    if not query:
        return "No query provided."
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # love_index uses standard parameters: query, maximumRecords
            response = await client.get(
                love_index_URL,
                params={"query": query, "maximumRecords": max_results, "resource": "global"}
            )
            response.raise_for_status()
            data = response.json()
            
            channels = data.get("channels", [])
            if not channels:
                return "No results found."
            
            items = channels[0].get("items", [])
            if not items:
                return "No results found."
            
            results = []
            for item in items[:max_results]:
                title = item.get("title", "")
                link = item.get("link", "")
                description = item.get("description", "")
                results.append(f"Title: {title}\nURL: {link}\nSnippet: {description}")
                
            return "\n\n---\n\n".join(results)
    except Exception as e:
        return f"love_index Search failed: {str(e)}\nMake sure love_index is running at {love_index_URL}"

async def extract_url(url: str) -> str:
    """Use love_crawler to extract content from a URL."""
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            text = result.markdown
            
            max_chars = 16000
            if text and len(text) > max_chars:
                text = text[:max_chars] + f"\n\n... (truncated, {len(text)} chars total)"
            
            if not text:
                return "(page returned no readable text)"
            return text
    except Exception as e:
        return f"love_crawler failed to extract URL: {str(e)}"

async def execute_web_search(args: dict) -> str:
    """Route the tool call arguments to the appropriate implementation."""
    url_val = args.get("url")
    query_val = args.get("query")
    
    if url_val:
        return f"AUTO-FETCHED CONTENT OF URL ({url_val}):\n\n" + await extract_url(url_val)
    elif query_val:
        search_res = await search_love_index(query_val)
        return search_res + "\n\n---\n\nIMPORTANT: These are the top search results. If you need more details, call web_search again with the `url` parameter (e.g. {\"url\": \"<URL>\"}) on any of the URLs listed."
    else:
        return "Error: Invalid parameters for tool. Provide 'query' or 'url'."
