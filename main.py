import os
import re

import requests
import validators
from requests_html import *


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class HtmlContent:
    def __init__(self, url: str):
        self.url = url
        self.session = HTMLSession()
        self.async_session = AsyncHTMLSession()
        self.request_html_response: HTMLResponse = None
        self.async_session.run(self._get_request)

    async def _get_request(self):
        self.request_html_response = self.session.get(self.url)

    def get_link(self):
        return self.request_html_response.html.links

    def get_response(self):
        return self.request_html_response

    def get_css(self):
        link_css = []
        for k in self.get_response().html.find("link[rel]"):
            try:
                if not validators.url(k.attrs['href']):
                    attr = k.attrs['href']
                    keyword = '.css'
                    attr = attr[: str(attr).find(keyword) + len(keyword)]
                    link_css.append(attr)
            except KeyError:
                pass
        return link_css

    def get_js(self):
        link_js = []
        for k in self.get_response().html.find("script"):
            try:
                if not validators.url(k.attrs['src']):
                    attr = k.attrs['src']
                    keyword = '.js'
                    attr = attr[: str(attr).find(keyword) + len(keyword)]
                    link_js.append(attr)
            except KeyError:
                pass
        return link_js

    def get_img(self):
        links_img = []
        for k in self.get_response().html.find('img'):
            attr = k.attrs['src']
            keyword = '.png'
            if str(attr).find(keyword) < 0:
                keyword = ".jpeg"
                if str(attr).find(keyword) < 0:
                    keyword = '.svg'

            attr = attr[: str(attr).find(keyword) + len(keyword)]
            links_img.append(attr)

        return links_img


def write_content(BASE_URL, data: list):
    for link in data:
        path = ""
        for i in re.findall(r"(?<=\/)(.*?)(?=\/)", link):
            path += i + "/"
        try:
            full_link = BASE_URL + link
            if requests.get(full_link).status_code == 200:
                os.makedirs(path, exist_ok=True)
                with open("." + link, "wb") as w:
                    w.write(requests.get(full_link).content)
        except FileNotFoundError:
            pass

        except (PermissionError, requests.exceptions.InvalidURL):
            continue


def main(URL: str):
    try:
        URL_BASE = URL.replace(urlparse(URL).path, "")
        html_content = HtmlContent(URL)
        with open("index.html", "w") as w:
            w.write(str(html_content.get_response().text))
        write_content(URL_BASE, html_content.get_css())
        write_content(URL_BASE, html_content.get_js())
        write_content(URL_BASE, html_content.get_img())
        print(f'{bcolors.OKCYAN}(OK) {bcolors.WARNING}{URL}')
    except Exception as e:
        print(f'{bcolors.FAIL}(Error {e}) {bcolors.WARNING}{URL}')


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        main(args[1])
    else:
        print(f"{bcolors.WARNING} Inform the URL")
