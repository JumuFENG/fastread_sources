from app.parsers.base_parser import BaseBookSourceParser, ChapterInfo, SearchResult
import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote, urlencode
from app.lofig import logger


class BxwxParser(BaseBookSourceParser):
    """笔下文学解析器"""
    source_config = {
        "name": "bxwx",
        "show_name": "笔下文学",
        "encoding": "gbk",
        "url": "https://www.hen0.com/",
        "domains": ["www.hen0.com","hen0.com"],
        "search": {
            "url": "https://www.hen0.com/search.html",
            "items": [
                ".table-responsive tbody tr"
            ]
        },
        "chapter_list": {
            "count_per_page": 60,
            "next": ".listpage .right a",
            "list": [],
            "items": ['ul.chapter-list a[class]'],
            "page_url": {
                "skip_endding": "/",
                "fmt": "{book_url}_{page}/"
            }
        },
        "book": {
            "title": ['h1.book-title'],
            "author": ['p.book-author'],
            "description": ['div.book-tags'],
            "cover_img": ['img.book-cover-large'],
        },
        "content": {
            "selector": "#chapter-content",
            "next": ".text-end a",
            "remove_tags": ["center"]
        }
    }

    async def search_books(self, keyword: str, limit: int = 10):
        try:
            async with httpx.AsyncClient(timeout=30.0, default_encoding=self.default_encoding) as client:
                form_data = urlencode({"searchkey": keyword}, encoding='gbk')
                headers = self.headers.copy()
                headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=gbk'
                response = await client.post(self.search_url, content=form_data.encode('gbk'), headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                books = await self.parse_search_results(soup)

                return books

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []

    async def parse_search_results(self, soup: BeautifulSoup):
        """
        解析搜索结果页面
        子类可以重写此方法实现特定的解析逻辑
        """
        results = []

        for book in soup.select(self.search_items_selectors[0]):
            try:
                title = book.select('a')[0].get_text()
                author = book.select('td')[1].get_text()
                book_url = book.select('a')[0].get('href')

                if title and book_url:
                    results.append(SearchResult(
                        title=title,
                        author=author,
                        description='',
                        source_url=book_url,
                        cover_url=''
                    ))
            except Exception as e:
                logger.error(f"解析搜索结果项失败: {e}")
                continue

        return results

    def build_chapter_next_section_url(self, chapter_url: str, next_sec: str):
        return chapter_url.replace(chapter_url.rsplit('/', 1)[1] , next_sec)

    async def parse_chapter_list(self, soup, book_url: str, chno:int=0):
        style_text = soup.select_one('style').get_text()
        pattern = re.compile(r"\.(p_\d+)::after\{content:'([^']*)'\}")
        content_map = dict(pattern.findall(style_text))
        chapters = []
        chapter_number = chno + 1
        for link in soup.select(self.chapter_links_items_selector[0]):
            try:
                lcls = link.get('class')[0]
                title = content_map.get(lcls, '')
                href = link.get('href')

                if self.is_valid_chapter_link(title, href):
                    full_url = self.build_full_url(href, self.base_url)
                    chapters.append(ChapterInfo(
                        title=title,
                        url=full_url,
                        chapter_number=chapter_number
                    ))
                    chapter_number += 1

            except Exception as e:
                logger.error(f"解析章节链接失败: {e}")
                continue
        return chapters

    def clean_content_soup(self, element):
        text = element.select_one('style').get_text().strip()
        contents = re.findall(r"\{content:'(.*?)'\}", text)
        return self.join_paragraphs([p.strip() for p in contents if p.strip()])
