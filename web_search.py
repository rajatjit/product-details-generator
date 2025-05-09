import requests
import streamlit as st



def google_search(query, num_results):
    """
    Returns a list of {title, snippet, link} for the top num_results.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": st.secrets["google"]["api_key"],
        "cx": st.secrets["google"]["cse_id"],
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