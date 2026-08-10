"""
晋江文学城书源解析器
针对晋江文学城类网站的特定解析逻辑
"""

from typing import List, Optional
from bs4 import BeautifulSoup
from app.parsers.base_parser import BaseBookSourceParser, ChapterInfo
from app.lofig import logger


class JjwxcParser(BaseBookSourceParser):
    """晋江文学城解析器"""
    source_config = {
        "name": "jjwxc",
        "show_name": "晋江文学城",
        "url": "https://www.jjwxc.net/",
        "encoding": "gb18030",
        "domains": ["jjwxc.net", "www.jjwxc.net"],
        "chapter_list": {
            "items":['#oneboolt tr[itemprop="chapter"]'],
        },
        "book": {
            "title": ["#oneboolt .bigtext h1"],
            "author": ["#oneboolt h2 a"],
            "description": ["#novelintro"],
            "cover_img": [
                'img.noveldefaultimage'
            ]
        },
        "content": {
            "selector": ".novelbody div",
            "remove_tags": [
                'div',
            ]
        }
    }

    def convert_chapter_links(self, links: List[BeautifulSoup], start_no: int=1) -> List[ChapterInfo]:
        chapters = []
        chapter_number = start_no
        for link in links:
            try:
                title_elem = link.select_one('a')
                # VIP 章节可能没有链接
                href = title_elem.get('href')
                ctx_elem = link.select_one('td:nth-of-type(3)')
                title = title_elem.text.strip() + ' ' + ctx_elem.text.strip()

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
