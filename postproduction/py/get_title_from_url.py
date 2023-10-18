
import re
import pyperclip
import requests
from bs4 import BeautifulSoup

def get_title(url):
    return BeautifulSoup(requests.get(url).text, 'html.parser').title.text

def copy_to_clipboard(title, url):
    pyperclip.copy(f'"{title}": "{url}",')
    print(f'A key-value pair was copied to clipboard!\ntitle:\n\t{title}\nurl:\n\t{url}')

def main():
    url = pyperclip.paste()
    title = get_title(url)
    copy_to_clipboard(title, url)


if __name__ == "__main__":
    main()
