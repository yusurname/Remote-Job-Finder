import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
import os

base_url = "https://mostaql.com/projects?page={}&keyword={}&budget_max=10000&sort=latest"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def scrape_mostaql_pages(num_pages=1, keyword=""):
    all_projects = []

    for page in range(1, num_pages + 1):
        url = base_url.format(page, keyword)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to load page {page}: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        projects = soup.find_all("tr", class_="project-row")

        if not projects:
            st.warning(f"No projects found on page {page}")
            continue

        for rank, project in enumerate(projects, start=1):
            title = project.find("h2", class_="mrg--bt-reset")
            project_name = title.text.strip() if title else "Not Available"

            bids = project.find_all("li", class_="text-muted")[2]
            offers_count = bids.text.strip() if bids else "Not Available"

            time_element = project.find_all("li", class_="text-muted")[1]
            time_left = time_element.text.replace("\n", "").replace("\t", "").strip() if time_element else "Not Available"

            name = project.find_all("li", class_="text-muted")[0]
            client_name = name.text.strip() if name else "Not Available"

            description_element = project.find("p", class_="text-wrapper-div project__brief")
            project_description = description_element.text.strip() if description_element else "Not Available"

            all_projects.append({
                "page_number": page,
                "rank": rank,
                "project_name": project_name,
                "offers_count": offers_count,
                "time_left": time_left,
                "client_name": client_name,
                "project_description": project_description
            })

    return all_projects

def save_to_csv(data, filename="mostaql_projects.csv"):
    if not data:
        st.error("No data to save.")
        return None

    keys = data[0].keys()
    try:
        with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        return filename
    except Exception as e:
        st.error(f"Error while saving the file: {e}")
        return None

st.set_page_config(page_title="Mostaql Scraper", layout="centered")
st.title("🕸️ Mostaql Data Scraper")

keyword = st.text_input("🔍 Enter Keyword")
num_pages = st.number_input("📄 Number of Pages", min_value=1, max_value=20, value=1)

if st.button("Start Scraping"):
    if keyword.strip() == "":
        st.error("Please enter a keyword.")
    else:
        with st.spinner("Scraping in progress..."):
            data = scrape_mostaql_pages(num_pages, keyword)
            if data:
                csv_file = save_to_csv(data)
                if csv_file:
                    st.success(f"Data saved to {csv_file}")
                    with open(csv_file, "rb") as f:
                        st.download_button("⬇️ Download CSV", f, file_name=csv_file, mime="text/csv")
            else:
                st.warning("No data extracted.")
