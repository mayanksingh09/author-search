import PyPDF2
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from typing import List, Union
import xml.etree.ElementTree as ET
from urllib.parse import urlencode


def get_pdf_content(pdf_url):
    """
    Get the content of a PDF file from a URL.
    Args:
        pdf_url (str): The URL of the PDF file
    Returns:
        list: A list of strings, where each string is the text content of a page in
                the PDF file
        """
    
    response = requests.get(pdf_url)
    pdf = PyPDF2.PdfReader(BytesIO(response.content))
    content = []
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        content.append(page.extract_text())
        
    return content

def get_html_content(arxiv_url):
    """
    Get the content of an arXiv paper from a URL.
    Args:
        arxiv_url (str): The URL of the arXiv paper
    Returns:
        str: The text content of the arXiv paper
    """

    response = requests.get(arxiv_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.get_text()

    return content

def get_content_by_topic(topic: Union[str, List[str]], 
                         filter_type: str = "all",
                         field_to_search: str = "all",
                         print_url: bool = False):
    """
    Get the content of arXiv papers by topic.
    Args:
        topic (str or list): The topic(s) to search for papers on arXiv
        filter_type (str): The filter type to use.
        field_to_search (str): The field to search for the topic string in.
        Options: {
            'abs': abstract, 
            'co': comment, 
            'jr': journal reference, 
            'ti': title, 
            'all': all of the above including author
        }
        additional details about field_to_search: https://info.arxiv.org/help/api/user-manual.html#query_details
        print_url (bool): Whether to print the URL used to get the papers
    Returns:
        str: The XML content of the arXiv papers    
    """
    if isinstance(topic, list):
        topics_list = [f"{field_to_search}:{topic}" for topic in topic]
        if filter_type == "all":
            topic = "+AND+".join(topics_list)
        elif filter_type == "any":
            topic = "+OR+".join(topics_list)
        else: 
            raise ValueError("Invalid filter type. Options: 'all', 'any'")
    else:
        topic = f"{field_to_search}:{topic}"

    api_url = f"http://export.arxiv.org/api/query?{urlencode({'search_query': topic})}"
    
    if print_url:
        print(api_url)

    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception("Failed to get papers from arXiv")
    
    return response.text

def get_content_by_author(author: str,
                          filter_type: str = "all",
                          print_url: bool = False):
    """
    Get the content of arXiv papers by author.
    Args:
        author (str or list): The author(s) to search for papers on arXiv. 
        filter_type (str): The filter type to use. Options: 'all', 'any'
        print_url (bool): Whether to print the URL used to get the papers
    Returns:
        str: The XML content of the arXiv papers
    """

    if isinstance(author, list):
        author_list = [f"au:{author.lower().strip}" for author in author]
        if filter_type == "all":
            author = "+AND+".join(f"au:{author.strip().lower()}")
        elif filter_type == "any":
            author = "+OR+".join(f"au:{author.strip().lower()}")
        else:
            raise ValueError("Invalid filter type. Options: 'all', 'any'")
    else:
        author = f"au:{author.lower().strip()}"

    api_url = f"http://export.arxiv.org/api/query?{urlencode({'search_query': author})}"
    if print_url:
        print(api_url)
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception("Failed to get papers from arXiv")

    return response.text

def get_content_by_id(paper_id: str, print_url: bool = False):
    """
    Get the content of an arXiv paper by its ID.
    Args:
        paper_id (str): The ID of the arXiv paper
        print_url (bool): Whether to print the URL used to get the paper
    Returns:
        str: The XML content of the arXiv paper
    """
    
    api_url = f"http://export.arxiv.org/api/query?{urlencode({'id_list': paper_id})}"
    if print_url:
        print(api_url)
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception("Failed to get papers from arXiv")

    return response.text

def extract_paper_info(xml_string):
    """
    Extract the title, authors, and summary from an arXiv paper XML string.
    Args:
        xml_string (str): The XML content of an arXiv paper
    Returns:
        dict: A dictionary containing the title, authors, and summary of the paper
    """
    try: 
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        root = ET.fromstring(xml_string)
        
        entries = root.findall('atom:entry', namespace)

        if not entries:
            return []

        papers_info = []
        for entry in entries:
            
            # Extract the summary
            summary = entry.find('atom:summary', namespace)
            summary_text = summary.text.strip() if summary is not None else ""
            
            # Extract the authors
            authors = entry.findall('atom:author', namespace)
            author_names = [
                author.find('atom:name', namespace).text.strip()
                for author in authors 
                if author.find('atom:name', namespace) is not None
            ]
            
            # Extract the title
            title = entry.find('atom:title', namespace)
            title_text = title.text.strip() if title is not None else ""

            # Extract the primary category
            primary_category = entry.find('atom:primary_category', namespace)
            primary_category = primary_category.attrib['term'] if primary_category is not None else ""

            papers_info.append({
                'title': title_text,
                'authors': author_names,
                'summary': summary_text,
            })

        return papers_info
    
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def filter_content_by_exact_name(xml_content, relax_name=False):
    pass


def format_author_name(author_name: str, 
                       use_initials: bool= False):
    name_parts = author_name.strip().split(" ")
    if len(name_parts) == 3:
        # If the middle name is an initial, ignore it and use the first and last name only
        first_name, last_name = name_parts[0], f"{name_parts[1]}_{name_parts[2]}" if len(name_parts[1].replace('.', '')) > 1 else name_parts[2]
    elif len(name_parts) == 2:
        first_name, last_name = name_parts
    elif len(name_parts) == 1:
        first_name = ""
        last_name = name_parts[0]
        return last_name
    else:
        first_name = name_parts[0]
        last_name = name_parts[-1]
    
    if use_initials:
        initial = first_name[0] if first_name else ""

    return f"{last_name}_{initial}" if use_initials else f"{last_name}_{first_name}"


# TODOs:
    # 1. Add primary category extraction to extract_paper_info
        # More info on this here: https://arxiv.org/category_taxonomy
    # 2. Add affiliation extraction to extract_paper_info
    # 3. Add arxiv id to the extracted_paper_info
    # 4. The names are still approximate, find a way to make them more accurate
    # 5. Add other query parameters to function (currently only using search_query & id_list).
    #       Add start, max_results (https://info.arxiv.org/help/api/user-manual.html#search_query_and_id_list)