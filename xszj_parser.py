"""
xszj.org书源解析器
"""

from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from parsers.base_parser import BaseBookSourceParser, SearchResult, BookInfo, ChapterInfo
import re


class XszjParser(BaseBookSourceParser):
    """小说之家解析器"""
    source_config = {
        "name": "xszj",
        "show_name": "小说之家",
        "url": "https://xszj.org",
        "domains": ['xszj.org', 'www.xszj.org'],
        "chapter_list": {
            "count_per_page": 200,
            "items": ["#list a[rel='chapter']"],
            "next": "a.index-container-btn:-soup-contains('下一页')",
            "page_url": {
                "skip_endding": "/",
                "fmt": "{book_url}/cs/{page}",
            }
        },
        "book": {
            "title": ["#info h1"],
            "author": ['#info p:first-of-type'],
            "description": ["#intro"],
            "cover_img": ["#fmimg img"]
        },
        "content": {
            "selector": "#booktxt",
            "next": ".bottem2 a:-soup-contains('下一页')",
            "remove_patterns": [
                r'.*小说之家为广大书友们.*',
                r'.*xszj\.org.*',
                r'.*请粘贴以下网址分享.*',
                r'.*本站采用Cookie技术.*',
                r'.*搜书名找不到, 可以试试搜作者.*',
                r'.*登录用户跨设备保存书架的问题.*',
                r'.*重新登陆并.*'
            ]
        }
    }

    async def get_chapter_list(self, book_url):
        if '/cs/' not in book_url:
            book_url = self.chapter_list_page_url(1, book_url)
        return await super().get_chapter_list(book_url)

    def next_section_match(self, next_sec: str, chapter_sec: str) -> bool:
        """判断下一章节链接是否匹配当前章节链接"""
        nexturl = urlparse(next_sec)
        cururl = urlparse(chapter_sec)
        if nexturl.netloc != cururl.netloc or nexturl.path != cururl.path:
            return False
        nextpg = nexturl.query
        if not nextpg:
            return False
        return True
