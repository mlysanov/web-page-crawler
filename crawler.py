import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class Link:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth


class WebCrawler:
    def __init__(self, start_url, max_depth):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }

        self.proxy_host = ""
        self.proxy_port =
        self.proxy_username = ""
        self.proxy_password = ""
        self.proxy_url = f"http://{self.proxy_username}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"
        self.proxies = {
            "http": self.proxy_url,
            "https": self.proxy_url,
        }

    def normalize_url(self, url):
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        path = parsed.path if parsed.path != '/' else ''
        normalized = f"{scheme}://{parsed.netloc}{path}"
        return normalized

    def crawl_stream(self, link=None):
        if link is None:
            link = Link(self.start_url, 1)

        stack = [link]

        while stack:
            current_link = stack.pop()

            if current_link.depth > self.max_depth:
                continue

            if current_link.url in self.visited:
                continue

            parsed_url = urlparse(current_link.url)
            if parsed_url.fragment:
                continue

            if parsed_url.scheme not in ["http", "https"]:
                yield f"Схема не поддерживается {current_link.url}\n\n"
                continue

            yield f"data: {current_link.url}\n\n"

            try:
                response = requests.get(current_link.url, headers=self.headers, timeout=5)
                response.raise_for_status()
            except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
                try:
                    response = requests.get(current_link.url, headers=self.headers, proxies=self.proxies, timeout=10)
                    response.raise_for_status()
                except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
                    yield f"Не удалось перейти по ссылке {current_link.url}\n\n"
                    continue

            self.visited.add(current_link.url)

            if current_link.depth < self.max_depth:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    full_url = urljoin(current_link.url, a_tag['href'])
                    full_url = self.normalize_url(full_url)
                    parsed_child_url = urlparse(full_url)

                    if full_url not in self.visited and parsed_child_url.scheme in ["http", "https"]:
                        stack.append(Link(full_url, current_link.depth + 1))
