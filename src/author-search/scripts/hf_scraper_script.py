import json
import PyPDF2
import requests
from io import BytesIO
from bs4 import BeautifulSoup



class HFPapersScraper:
    """
    Script to scrape papers from Hugging Face's papers page. 
    AK: https://huggingface.co/akhaliq and community submitted papers
    """

    def get_paper_urls(self, date:str = None):
        """
        Get all the paper urls from the Hugging Face papers page.
        Args:
            date (str): The date to filter the papers by. Format: YYYY-MM-DD
        Returns:
            list: A list of paper urls
        """
        
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
    
    def get_paper_ids(self, date: str = None):
        """
        Get all the paper ids from the Hugging Face papers page.
        Args:
            date (str): The date to filter the papers by. Format: YYYY-MM-DD
        Returns:
            list: A list of paper ids
        """
        
        paper_urls = self.get_paper_urls(date)
        paper_ids = [url.split('/')[-1] for url in paper_urls if len(url.split('/')[-1]) > 0]

        return paper_ids

    def get_arxiv_links(self, hf_papers_urls: list, type='pdf'):
        """
        Get the arxiv links for the papers on the Hugging Face papers page.
        Parsing the actual HTML to extract it.
        Quicker to just extract the id from the URL and append it to the arxiv URL.
        Args:
            hf_papers_urls (list): A list of Hugging Face paper urls
            type (str): The type of arxiv link to get. Options: pdf, abs
        Returns:
            list: A list of arxiv links
        """

        arxiv_paper_links = []
        for url in hf_papers_urls:
            paper_response = requests.get(url)
            paper_soup = BeautifulSoup(paper_response.text, 'html.parser')
            paper_arxiv_link = paper_soup.find('a', href=lambda x: x and 'arxiv.org' in x)
            arxiv_paper_links.append(paper_arxiv_link['href'])

        arxiv_paper_links = [link.replace('/abs/', f'/{type}/') for link in arxiv_paper_links]

        return arxiv_paper_links
    
    # TODO: Add a method to tag the votes on each paper
