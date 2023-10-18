# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## JSONのReferencesをHTMLに

from logging import getLogger, FileHandler, Formatter, DEBUG
import json
episode_number = '18'
episode_name = 'episode' + episode_number

# +
logger = getLogger(f'postproduction-{episode_name}')
logger.setLevel(DEBUG)

f_handler = FileHandler(f'../log/{episode_name}.log',)
f_handler.setLevel(DEBUG)

# ログ出力フォーマット設定
handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(handler_format)
logger.addHandler(f_handler)


# -

# ## Header と References

# +
def create_header_html(speakers_dict, topics_list, comments=None):
    result = '<div class="content-head">\n'
    speakers_list = list(speakers_dict.values())
    for speaker in speakers_list:
        if speaker==speakers_list[-1]:
            result += f'<b class="speaker">{speaker}</b>'
            break
        result += f'<b class="speaker">{speaker}</b>, '
    result += f'が\n'
    result += '<p class="topics">'
    
    for topic in topics_list:
        if topic==topics_list[-1]:
            result += topic
            break
        result += f'{topic}, '
    result += '</p>について話しました。'
    
    if comments is not None:
        result += f'<p class="comments">{comments}</p>'
        
    result += '</div>'
    return result
    
def create_references_html(references_dict):
    result = '<div class="references">\n'
    result += '<ul>\n'
    for text, link in references_dict.items():
        result += f'<li><a href="{link}">{text}</a></li>\n'
    result += '</ul>\n\n'
    result += '</div>'
    return result


# +
with open(f'../json/{episode_name}.json', 'r') as f:
    data = json.load(f)

number = data["Number"]
title = data["Title"]
starr = ", ".join(data["Starr"])

if episode_name.split('episode')[-1]!=number:
    raise ValueError('Episode number is wrong.')

title = f'#{number} {title} ({starr})'
speakers = data['Starr']
topics = data['Topics']
comments = None

references = data['References']
header_html = create_header_html(speakers, topics, comments)
references_html = create_references_html(references)
print(title)
print(header_html)
print()
print(references_html)
print('<p class="desc-iOS">Podcastアプリにチャプタ機能があれば気になるトピックにスキップすることができます。</p>')
# -

# ---

# #15-1 郡山のポーカーサークル (Gota, Kondo, Takumi, Katashin)
# <div class="content-head">
# <b class="speaker">Gota Shirato</b>, <b class="speaker">Ryosuke Kondo</b>, <b class="speaker">Takumi Sato</b>, <b class="speaker">Shin Katayama</b> discussed...
# <p class="topics">ワーホリ, 一人旅, 郡山のポーカーサークル</p></div>
#
# <div class="references">
# <ul>
# <li><a href="https://www.ippudo.co.uk/">IPPUDO LONDON</a></li>
# <li><a href="https://www.lemontroyal.qc.ca/en">モン・ロワイヤル</a></li>
# <li><a href="https://twitter.com/allinfukushima">郡山のポーカーサークル(オールイン福島)</a></li>
# <li><a href="https://ja.wikipedia.org/wiki/%E3%83%A9%E3%82%A4%E3%83%B3%E3%83%BB%E3%83%95%E3%83%AA%E3%83%BC%E3%83%89%E3%83%AA%E3%83%92%E3%83%BB%E3%83%B4%E3%82%A3%E3%83%AB%E3%83%98%E3%83%AB%E3%83%A0%E5%A4%A7%E5%AD%A6%E3%83%9C%E3%83%B3">ボン大学</a></li>
# <li><a href="https://www.farmstayplanet.com/farm-stay-rural-travel-guides/australia/">ファームステイ</a></li>
# <li><a href="https://dktokyo.com/blog/cigarette/">オーストラリアではタバコ1箱4500円以上に！2020年までに値上げの予定</a></li>
# <li><a href="http://madame.ayapro.ne.jp/">マダム・イン・ニューヨーク</a></li>
# <li><a href="https://ja.wikipedia.org/wiki/%E3%82%AD%E3%83%B3%E3%82%B0%E3%82%B9%E3%83%BB%E3%82%AF%E3%83%AD%E3%82%B9%E9%A7%85">キングス・クロス駅</a></li>
# <li><a href="https://ja.wikipedia.org/wiki/BELIEVE_(%E6%9D%89%E6%9C%AC%E7%AB%9C%E4%B8%80%E3%81%AE%E6%9B%B2)">Believe</a></li>
# <li><a href="https://www.shiruporuto.jp/public/data/survey/yoron/">家計の金融行動に関する世論調査</a></li>
# </ul>
#
# </div>
# <p class="desc-iOS">Podcastアプリにチャプタ機能があれば気になるトピックにスキップすることができます。</p>

logger.info(title)
logger.info(header_html)
logger.info(references_html)


