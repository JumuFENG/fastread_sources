from parsers.base_parser import BaseBookSourceParser
import re


class DybzParser(BaseBookSourceParser):
    """笔趣阁解析器"""
    source_config = {
        "name": "diyibanzhu",
        "show_name": "第一版主网",
        "url": "https://m.diyibanzhu5.online/",
        "domains": ["m.diyibanzhu5.online","m.diyibanzhu.me"],
        "search": {
            "url": "{keyword}",
            "items": [],
            "next": "",
            "title": [],
            "author": [],
            "description": [],
            "cover_img": [],
            "cover_bg_img": [],
        },
        "chapter_list": {
            "count_per_page": 30,
            "list":['.chapter-list .bd ul.list'],
            "next": "a.nextPage"
        },
        "book": {
            "author": ['.detail .info'],
        },
        "content": {
            "selector": "#nr1",
            "remove_tags": ['font', 'center'],
            "remove_patterns": []
        }
    }

    def extract_book_author(self, soup):
        for selector in self.book_author_selectors:
            element = soup.select_one(selector)
            if element and element.text.strip():
                text = element.text.strip().split('\n')
                # 移除"作者："等前缀
                text = re.sub(r'^(作[\s]*者[：:]?)', '', text[0]).strip()
                if text:
                    return text

        return "未知作者"

    async def parse_chapter_list(self, soup, book_url, chno = 0):
        links = []
        container_selector = self.chapter_links_container_selectors[0]
        container = soup.select(container_selector)[-1]
        if container:
            links = container.find_all('a', href=True)

        return self.convert_chapter_links(links, chno + 1)

    def get_chapter_next_section(self, soup, chapter_url, chapter_sec):
        curpage = soup.select_one('.chapterPages span')
        if not curpage:
            return None
        curpage = int(curpage.get_text().lstrip('【').rstrip('】'))
        pages = soup.select('.chapterPages a')
        for p in pages:
            if p.get_text().lstrip('【').rstrip('】') == str(curpage + 1):
                return self.build_full_url(p['href'], chapter_url)
        return None
