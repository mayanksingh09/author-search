import requests
from bs4 import BeautifulSoup
import json

import PyPDF2
from io import BytesIO


class HFPapersScraper:

    def get_paper_urls(self, date=None):
        
        base_url = "https://huggingface.co/papers"
        
        if date:
            url = f"{base_url}?date={date}"
        else:
            url = base_url
        
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        paper_links = soup.find_all('a', href=lambda x: x and '/papers/' in x)
        
        paper_urls = set()
        for link in paper_links:
            full_url = f"https://huggingface.co{link['href']}"
            # remove #community from the url if it exists
            if '#community' in full_url:
                paper_urls.add(full_url.split('#community')[0])
            else:
                paper_urls.add(full_url)

        return list(set(paper_urls))
    
    def get_paper_ids(self, date=None):
        paper_urls = self.get_paper_urls(date)
        paper_ids = [url.split('/')[-1] for url in paper_urls if len(url.split('/')[-1]) > 0]
        return paper_ids

    def get_arxiv_links(self, hf_papers_urls: list, type='pdf'):

        arxiv_paper_links = []
        for url in hf_papers_urls:
            paper_response = requests.get(url)
            paper_soup = BeautifulSoup(paper_response.text, 'html.parser')
            paper_arxiv_link = paper_soup.find('a', href=lambda x: x and 'arxiv.org' in x)
            arxiv_paper_links.append(paper_arxiv_link['href'])

        arxiv_paper_links = [link.replace('/abs/', f'/{type}/') for link in arxiv_paper_links]

        return arxiv_paper_links

    # def get_pdf_content(self, pdf_url):
    #     response = requests.get(pdf_url)
    #     pdf = PyPDF2.PdfReader(BytesIO(response.content))
    #     content = []
    #     for page_num in range(len(pdf.pages)):
    #         page = pdf.pages[page_num]
    #         content.append(page.extract_text())
    #     return content

    # def get_html_content(self, arxiv_url):
    #     response = requests.get(arxiv_url)
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     content = soup.get_text()
    #     return content