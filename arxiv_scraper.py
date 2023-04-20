import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import shutil
import time


def get_arxiv_categories():
    arxiv_categories_url = "https://arxiv.org/help/api/user-manual#subject_classifications"
    response = requests.get(arxiv_categories_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    categories = []
    for item in soup.find_all('li'):
        code = item.find('span', class_='arxiv')
        if code:
            category = code.text.strip()
            description = item.text.replace(category, '').strip()
            categories.append((category, description))
    return categories

def search_arxiv_papers(query, category, start_date, end_date, max_results=500):
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query=cat:{category}+AND+all:{query}"
    
    # Format start_date and end_date
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y%m%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y%m%d")

    date_range = f"submittedDate:[{start_date}0000+TO+{end_date}2359]"
    query_url = f"{base_url}{search_query}+AND+{date_range}&sortBy=submittedDate&sortOrder=ascending&start=0&max_results={max_results}"

    response = requests.get(query_url)
    soup = BeautifulSoup(response.text, "lxml-xml")

    papers = []
    for entry in soup.find_all("entry"):
        paper = {
            "id": entry.id.text,
            "title": entry.title.text,
            "authors": [author.find("name").text for author in entry.find_all("author")],
            "published": entry.published.text,
            "updated": entry.updated.text,
            "summary": entry.summary.text,
            "link": entry.link["href"],
            "category": entry.category["term"]
        }
        papers.append(paper)
    return papers

def save_papers_to_json(papers, output_dir="papers"):
    os.makedirs(output_dir, exist_ok=True)
    for paper in papers:
        # Download the PDF and update the paper metadata
        pdf_filename = download_paper_pdf(paper, output_dir)
        paper["pdf_filename"] = pdf_filename

        # Save the updated metadata to a JSON file
        paper_id = paper["id"].split("/")[-1]
        file_path = os.path.join(output_dir, f"{paper_id}.json")
        with open(file_path, "w") as f:
            json.dump(paper, f, indent=2)


def download_paper_pdf(paper, output_dir="papers"):
    pdf_url = paper["link"].replace("http://", "https://") + ".pdf"
    pdf_filename = f"{paper['id'].split('/')[-1]}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    response = requests.get(pdf_url, stream=True)
    time.sleep(3)
    with open(pdf_path, "wb") as pdf_file:
        shutil.copyfileobj(response.raw, pdf_file)

    return pdf_filename

if __name__ == "__main__":
    categories = get_arxiv_categories()
    print("Categories:")
    for cat, desc in categories:
        print(f"{cat}: {desc}")

    query = "deep learning"
    category = "cs.LG"  # Category for Machine Learning
    start_date = "2021-01-01"
    end_date = "2021-12-31"

    papers = search_arxiv_papers(query, category, start_date, end_date, 25)
    print("\nSaving papers to JSON files...")
    save_papers_to_json(papers)
    print("Done.")
