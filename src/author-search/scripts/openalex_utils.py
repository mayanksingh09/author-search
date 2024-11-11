import requests
from urllib.parse import urlencode

import requests

def get_topic_ids_by_keyword(topic):
    url = f"https://api.openalex.org/topics?filter=display_name.search:{topic}"
    
    output = requests.get(url).json()
    return [result['id'] for result in output['results']]


def get_works_by_topic_id(topic_id, print_url=False):
    url = f"https://api.openalex.org/works?filter=topics.id:{topic_id}"
    
    if print_url:
        print(url)
    output = requests.get(url).json()
    return output['results']
