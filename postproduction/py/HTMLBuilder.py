from typing import Dict, List


class HTMLBuilder:
    @staticmethod
    def create_header_html(comments=None) -> str:
        result = '<div class="content-head">\n'
        if comments:
            result += f'<p class="comments">{comments}</p>'
        result += "</div>"
        return result

    @staticmethod
    def create_references_html(references_dict) -> str:
        result = '<div class="references">\n<ul class="list_test-wrap">\n'
        for text, link in references_dict.items():
            result += f'<li class="list_test"><a href="{link}">{text}</a></li>\n'
        result += "</ul>\n</div>"
        return result

    @staticmethod
    def generate_related_episodes_header() -> str:
        return "<h3>関連エピソード</h3>"

    @staticmethod
    def generate_related_episodes_list(links: List[Dict[str, str]]) -> str:
        links_list = "\n".join([l["link"] for l in links])
        return f"<ul>\n{links_list}\n</ul>"
