import requests
import PyPDF2
from io import BytesIO
from bs4 import BeautifulSoup
from typing import List, Union
import xml.etree.ElementTree as ET

def get_pdf_content(pdf_url):
    response = requests.get(pdf_url)
    pdf = PyPDF2.PdfReader(BytesIO(response.content))
    content = []
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        content.append(page.extract_text())
    return content

def get_html_content(arxiv_url):

    response = requests.get(arxiv_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.get_text()
    return content

def get_content_by_topic(topic: Union[str, List[str]], filter_type: str = "all"):

    if isinstance(topic, list) and filter_type == "all":
        topic = "+AND+".join(f"all:{topic}")
    elif isinstance(topic, list) and filter_type == "any":
        topic = "+OR+".join(f"all:{topic}")
    else:
        topic = f"all:{topic}"

    base_url = "http://export.arxiv.org/api/query?search_query=" # TODO: Edit this all parameter
    response = requests.get(base_url + topic)
    if response.status_code != 200:
        raise Exception("Failed to get papers from arXiv")
    
    return response.text

def get_content_by_author(author: str, filter_type: str = "all"):
    if isinstance(author, list) and filter_type == "all":
        author = "+AND+".join(f"au:{author}")
    elif isinstance(author, list) and filter_type == "any":
        author = "+OR+".join(f"au:{author}")
    else:
        author = f"au:{author}"

    base_url = "http://export.arxiv.org/api/query?search_query="
    response = requests.get(base_url + author)
    if response.status_code != 200:
        raise Exception("Failed to get papers from arXiv")

    return response.text

def get_content_by_id(paper_id):

    base_url = "http://export.arxiv.org/api/query?id_list="
    response = requests.get(base_url + paper_id)
    if response.status_code != 200:
        raise Exception("Failed to get papers from arXiv")

    return response.text

def extract_paper_info(xml_string):
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(xml_string)
    
    entry = root.find('atom:entry', namespace)

    if entry is None:
        return {}
    
    summary = entry.find('atom:summary', namespace)
    summary_text = summary.text.strip() if summary is not None else ""
    
    authors = entry.findall('atom:author', namespace)
    author_names = [author.find('atom:name', namespace).text 
                   for author in authors 
                   if author.find('atom:name', namespace) is not None]
    
    title = entry.find('atom:title', namespace)
    title_text = title.text.strip() if title is not None else ""
    
    return {
        'title': title_text,
        'authors': author_names,
        'summary': summary_text
    }