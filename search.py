import aiohttp
import re


async def web_search(query: str) -> str:
    """Поиск через DuckDuckGo без API ключа"""
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1",
            "no_redirect": "1",
        }
        headers = {"User-Agent": "Mozilla/5.0"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                data = await resp.json(content_type=None)

        # Пробуем AbstractText (краткий ответ)
        if data.get("AbstractText"):
            text = data["AbstractText"]
            return text[:300] + ("..." if len(text) > 300 else "")

        # Пробуем Answer (прямой ответ типа "сколько будет 2+2")
        if data.get("Answer"):
            return data["Answer"]

        # Пробуем первый RelatedTopic
        topics = data.get("RelatedTopics", [])
        for topic in topics:
            if isinstance(topic, dict) and topic.get("Text"):
                text = topic["Text"]
                return text[:300] + ("..." if len(text) > 300 else "")

        return None

    except Exception:
        return None
