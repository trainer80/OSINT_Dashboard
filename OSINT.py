import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import whois
import dns.resolver
from datetime import datetime

st.set_page_config(page_title="OSINT Dashboard", layout="wide")

st.title("🔎 OSINT Dashboard")

target = st.text_input("Enter Domain or IP")

# --------------------
# WHOIS Lookup
# --------------------
def get_whois(domain):
    try:
        w = whois.whois(domain)
        return {
            "Domain": w.domain_name,
            "Registrar": w.registrar,
            "Creation Date": w.creation_date,
            "Expiration Date": w.expiration_date,
        }
    except:
        return None

# --------------------
# DNS Lookup
# --------------------
def dns_lookup(domain):
    records = {}

    for rtype in ["A", "MX", "NS"]:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records[rtype] = [str(a) for a in answers]
        except:
            records[rtype] = []

    return records

# --------------------
# IP Geolocation
# --------------------
def ip_lookup(ip):
    try:
        url = f"http://ip-api.com/json/{ip}"
        return requests.get(url).json()
    except:
        return None

# --------------------
# Hacker News Search
# --------------------
def search_news(query):
    try:
        url = f"https://hn.algolia.com/api/v1/search?query={query}"
        data = requests.get(url).json()

        articles = []
        for hit in data["hits"][:10]:
            articles.append({
                "Title": hit.get("title"),
                "Author": hit.get("author"),
                "Date": hit.get("created_at")
            })

        return pd.DataFrame(articles)

    except:
        return pd.DataFrame()

# --------------------
# Dashboard
# --------------------
if target:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("WHOIS")

        whois_data = get_whois(target)

        if whois_data:
            st.json(whois_data)

    with col2:
        st.subheader("DNS Records")

        dns_data = dns_lookup(target)

        st.json(dns_data)

    st.divider()

    st.subheader("News Intelligence")

    news_df = search_news(target)

    if not news_df.empty:
        st.dataframe(news_df)

        news_df["Count"] = 1

        fig = px.histogram(
            news_df,
            x="Author",
            y="Count",
            title="News Authors Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("IP Geolocation")

    try:
        ip = dns_data["A"][0]
        geo = ip_lookup(ip)

        if geo:
            st.json(geo)

            map_df = pd.DataFrame(
                [{
                    "lat": geo["lat"],
                    "lon": geo["lon"]
                }]
            )

            st.map(map_df)

    except:
        st.warning("No IP found")

st.sidebar.title("About")
st.sidebar.info(
    """
    Educational OSINT Dashboard
    
    Features:
    - WHOIS
    - DNS Enumeration
    - IP Geolocation
    - News Intelligence
    - Visual Analytics
    """
)
