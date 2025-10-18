from parsers.base_parser import BaseBookSourceParser


class QidiyParser(BaseBookSourceParser):
    """启迪小说解析器"""
    source_config = {
        "name": "qidiy",
        "show_name": "启迪小说",
        "url": "http://www.qidiy.com/",
        "domains": ["www.qidiy.com", "qidiy.com"],
        "chapter_list": {
            "count_per_page": 20,
            "list": ['.section-box .section-list.fix'],
            "next": ".listpage .right a",
            "page_url": {
                "skip_endding": "/",
                "fmt": "{book_url}_{page}/"
            }
        },
        "book": {
            "title": ['.info h1'],
            "author": ['.info .fix p'],
            "description": ['.info .desc'],
            "cover_img": ['.imgbox img'],
        },
        "content": {
            "selector": "#content",
            "next": "div.section-opt.m-bottom-opt a:-soup-contains(\"下一页\")"
        }
    }

    async def parse_chapter_list(self, soup, book_url, chno = 0):
        links = []
        container_selector = self.chapter_links_container_selectors[0]
        container = soup.select(container_selector)[-1]
        if container:
            links = container.find_all('a', href=True)

        return self.convert_chapter_links(links, chno + 1)

    def next_section_match(self, next_sec: str, cur_sec: str) -> bool:
        """判断下一章节链接是否匹配当前章节链接"""
        next_sec = next_sec.rstrip('.html')
        cur_sec = cur_sec.rstrip('.html')
        if next_sec.startswith(cur_sec):
            return True
        next_id = int(next_sec.rsplit('/', 1)[-1])
        cur_id = int(cur_sec.rsplit('/', 1)[-1])
        return next_id == cur_id + 1
