from mcp.server.fastmcp import FastMCP
import os
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebSearch")

mcp = FastMCP("WebSearch")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

@mcp.tool()
def web_search(query: str) -> dict:
    """Search the internet using Google. Use this when the user asks for current information, news, facts or anything that needs up-to-date data from the web."""
    if not SERPAPI_KEY:
        return {"success": False, "error": "SERPAPI_KEY not configured"}

    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": 5,
            "hl": "ru",
            "gl": "ru"
        }
        r = httpx.get("https://serpapi.com/search", params=params, timeout=15)
        data = r.json()

        results = []
        if "answer_box" in data:
            ab = data["answer_box"]
            answer = ab.get("answer") or ab.get("snippet") or ab.get("title")
            if answer:
                results.append(f"Прямой ответ: {answer}")

        if "knowledge_graph" in data:
            kg = data["knowledge_graph"]
            title = kg.get("title", "")
            desc = kg.get("description", "")
            if title or desc:
                results.append(f"{title}: {desc}")

        for item in data.get("organic_results", [])[:5]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"{title}\n{snippet}\n{link}")

        if not results:
            return {"success": False, "error": "Ничего не найдено"}

        return {"success": True, "query": query, "results": "\n\n".join(results)}
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
