
import asyncio
import json

import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st

from core import app

st.set_page_config(page_title="AI Web Scraper", page_icon="🕷️")

st.title("🕷️ AI Powered Web Scraper")
st.write("Enter a query to extract data from websites.")

query = st.text_area(
    "Enter your scraping query",
    placeholder="Example: Extract book titles and prices from https://books.toscrape.com"
)

if "result" not in st.session_state:
    st.session_state.result = None


# async function that calls LangGraph
async def run_agent(user_query):
    result = await app.ainvoke({
        "query": user_query
    })
    return result


# button
if st.button("🚀 Run Scraper"):

    if query.strip() == "":
        st.warning("Please enter a query.")
    else:

        with st.spinner("Scraping website..."):

            result = asyncio.run(run_agent(query))

            st.session_state.result = result["response"]


# show result
if st.session_state.result:

    st.subheader("📊 Extracted Data")

    st.json(st.session_state.result)

    json_data = json.dumps(st.session_state.result, indent=4)

    st.download_button(
        label="⬇ Download JSON",
        data=json_data,
        file_name="scraped_data.json",
        mime="application/json"
    )