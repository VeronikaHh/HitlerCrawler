import requests
from constants import WIKI_HITLER_URL_SUFIX, WIKI_URL_PREFIX
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from collections import deque

def find_hitler_page(start_url, max_hops=6):
    queue = deque([(start_url, [start_url])])
    visited = set()

    while queue:
        url, path = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        if url.endswith(WIKI_HITLER_URL_SUFIX):
            return path
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').startswith('/wiki/')]
            for link in links:
                full_url = f'{WIKI_URL_PREFIX}{link}'
                if full_url not in visited:
                    queue.append((full_url, path + [full_url]))
        except:
            pass
        if len(path) >= max_hops:
            return None
    return None

def find_hitler_page_parallel(start_url, max_hops=6, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(max_hops):
            futures.append(executor.submit(find_hitler_page, start_url, i+1))
            if futures[-1].result() is not None:
                return futures[-1].result()
    return None

# Example usage
start_url = 'https://en.wikipedia.org/wiki/Adolf_Eichmann'
print(f'Start url: {start_url}')
path = find_hitler_page_parallel(start_url)
if path:
    print(f'Path to Hitler page: {" -> ".join(path)}')
else:
    print('Hitler not found')