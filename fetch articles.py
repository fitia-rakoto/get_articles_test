import requests
import xml.etree.ElementTree as ET

# Function to search PubMed and fetch article metadata
def search_and_fetch_pubmed(api_key, query):
    def search_pubmed(query, api_key):
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": 10,  # Adjust as needed
            "apikey": api_key
        }
        response = requests.get(base_url, params=params)
        return response.text if response.status_code == 200 else None

    def parse_pmids_from_result(result_xml):
        root = ET.fromstring(result_xml)
        return [id_elem.text for id_elem in root.findall('.//Id')]

    def fetch_article_metadata(pmids, api_key):
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        articles = []
        for pmid in pmids:
            params = {"db": "pubmed", "id": pmid, "apikey": api_key}
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                article = {
                    "pmid": pmid,
                    "title": root.find('.//Item[@Name="Title"]').text,
                    "authors": [author.text for author in root.findall('.//Item[@Name="Author"]')],
                    "doi": root.find('.//Item[@Name="DOI"]').text if root.find('.//Item[@Name="DOI"]') is not None else None
                }
                articles.append(article)
            else:
                print(f"Failed to fetch metadata for PMID {pmid}")
        return articles

    # Execute PubMed search and fetch metadata
    results_xml = search_pubmed(query, api_key)
    if results_xml:
        pmids = parse_pmids_from_result(results_xml)
        articles = fetch_article_metadata(pmids, api_key)
        for article in articles:
            print(f"PubMed PMID: {article['pmid']}")
            print(f"Title: {article['title']}")
            print(f"Authors: {', '.join(article['authors'])}")
            print(f"DOI: {article['doi']}\n")
    else:
        print("No PubMed results found or an error occurred.")

# Function to fetch articles from Google Scholar
def fetch_and_print_scholar_articles(api_key, query):
    def fetch_scholar_articles(api_key, query, page=0):
        base_url = "https://serpapi.com/search.json"
        params = {
            "api_key": api_key,
            "engine": "google_scholar",
            "q": query,
            "start": page * 10,
            "hl": "en"
        }
        response = requests.get(base_url, params=params)
        return response.json() if response.status_code == 200 else None

    articles = fetch_scholar_articles(api_key, query)
    if articles:
        for article in articles.get("organic_results", []):
            print(f"Google Scholar Title: {article['title']}")
            print(f"Link: {article['link']}")
            if "publication_info" in article and "authors" in article["publication_info"]:
                authors = article["publication_info"]["authors"]
                author_names = [author["name"] for author in authors]
                print(f"Authors: {', '.join(author_names)}\n")
    else:
        print("No Google Scholar results found or an error occurred.")

# PubMed API key and search query
pubmed_api_key = "fc36ae0facacd00e510a203952235f3cbb08"
pubmed_query = '((data linkage[Title/Abstract]) OR (data curation[Title/Abstract]) OR (data harmonization[Title/Abstract])) AND (y_10[Filter])'
search_and_fetch_pubmed(pubmed_api_key, pubmed_query)

# Google Scholar API key and query
scholar_api_key = "a97e5ce49241d378b635be4a7d519a3a73b551d5643db0b0994d9cd7670e78dc"
scholar_query = "data linkage, data curation, data harmonization"
fetch_and_print_scholar_articles(scholar_api_key, scholar_query)
