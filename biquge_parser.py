"""
笔趣阁书源解析器
针对笔趣阁类网站的特定解析逻辑
"""

from app.parsers.base_parser import BaseBookSourceParser
import re

# class BxwxParser(BaseBookSourceParser):
#     """笔下文学解析器"""
#     source_config = {
#         "name": "bxwx",
#         "show_name": "笔下文学",
#         "encoding": "gbk",
#         "url": "https://www.hen0.com/",
#         "domains": ["www.hen0.com","hen0.com"],
#         "chapter_list": {
#             "count_per_page": 60,
#             "next": ".listpage .right a",
#             "items": ['.card-body ul:last-of-type li a'],
#             "page_url": {
#                 "skip_endding": "/",
#                 "fmt": "{book_url}_{page}/"
#             }
#         },
#         "book": {
#             "title": ['h1.book-title'],
#             "author": ['p.book-author'],
#             "description": ['div.book-tags'],
#             "cover_img": ['img.book-cover-large'],
#         },
#         "content": {
#             "selector": "#chapter-content",
#             "next": ".text-end a",
#             "remove_tags": ["center"]
#         }
#     }

#     def build_chapter_next_section_url(self, chapter_url: str, next_sec: str):
#         return chapter_url.replace(chapter_url.rsplit('/', 1)[1] , next_sec)

#     def clean_content_soup(self, element):
#         text = element.select_one('style').get_text().strip()
#         contents = re.findall(r"\{content:'(.*?)'\}", text)
#         return self.join_paragraphs([p.strip() for p in contents if p.strip()])
