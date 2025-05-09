import requests
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID

def google_search(query, num_results):
    """
    Returns a list of {title, snippet, link} for the top num_results.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    hits = []
    for item in data.get("items", []):
        hits.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link"),
        })
    return hits