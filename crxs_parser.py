"""
crxs.me书源解析器
"""

from typing import List, Optional
from bs4 import BeautifulSoup
from parsers.base_parser import BaseBookSourceParser, SearchResult, BookInfo, ChapterInfo


class CrxsParser(BaseBookSourceParser):
    """起点中文网解析器"""
    source_config = {
        "name": "crxs",
        "show_name":"crxs",
        "url": "https://crxs.me",
        "domains": ['crxs.me', 'www.crxs.me'],
        "search": {
            "url": "https://crxs.me/fictions/keyword-{keyword}.html",
            "items": [".item.fiction"],
            "next": ".pager a.pager-next",
            "title": [".text .title a"],
            "author": [],
            "description": [".text .brief"],
            "cover_bg_img": ["a .img"]
        },
        "chapter_list": {
            "list": [".fiction-overview-chapters .chapter-container"]
        },
        "book": {
            "title": [".fiction-overview-info-item.title"],
            "description": [".fiction-overview-brief"],
            "cover_bg_img": [".fiction-cover"],
        },
        "content": {
            "selector": ".fiction-body",
            "remove_patterns": [
                r'（.*crxs.me.*）'
            ]
        }
    }

    async def parse_book_info(self, soup: BeautifulSoup, book_url: str) -> Optional[BookInfo]:
        """解析书籍信息"""
        try:
            bookinfo = await super().parse_book_info(soup, book_url)
            if not bookinfo.title and not bookinfo.author:
                if self.is_single_chapter_book(soup):
                    title_elem = soup.select_one('div.title')
                    bookinfo.title = title_elem.text.strip() if title_elem else "未知标题"
                    bookinfo.author = "未知作者"
                    content = await self.parse_chapter_content(soup)
                    bookinfo.description = content[:500] if content else ""
                    return bookinfo
            if not bookinfo.title:
                bookinfo.title = '未知标题'
            elif not bookinfo.author:
                bookinfo.author = '未知作者'
            return bookinfo

        except Exception as e:
            print(f"解析起点书籍信息失败: {e}")
            return None

    async def parse_chapter_list(self, soup: BeautifulSoup, book_url: str, chno:int=0) -> List[ChapterInfo]:
        """解析起点章节列表"""
        chapters = await super().parse_chapter_list(soup, book_url, chno)
        if chapters:
            return chapters

        if self.is_single_chapter_book(soup):
            title_elem = soup.select_one('div.title')
            title = title_elem.text.strip() if title_elem else "未知标题"
            return [ChapterInfo(
                title=title,
                url=book_url,
                chapter_number=1
            )]
        return []

    def is_single_chapter_book(self, soup: BeautifulSoup) -> bool:
        """判断是否为单章节书籍"""
        return len(soup.select('.fiction-body')) > 0

    def is_valid_chapter_link(self, title: str, href: str) -> bool:
        """判断是否为有效的章节链接"""
        if super().is_valid_chapter_link(title, href):
            return True

        if 'chapter' in href.lower() or '/fiction/id-' in href.lower():
            return True

        return False

