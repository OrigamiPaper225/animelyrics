# coding: utf-8
from urllib.parse import urlparse

import googlesearch
import requests
from bs4 import BeautifulSoup

__BASE_URL__ = "www.animelyrics.com"


class NoLyricsFound(Exception):
    """Exception class to handle no lyrics found"""

    pass


class MissingTranslatedLyrics(Exception):
    """Exception class to handle lyrics with missing translated lyrics"""

    pass


class InvalidLanguage(ValueError):
    """Exception class to handle invalid language selection"""

    pass


def search_lyrics(query, lang="jp", show_title=False):
    """
    Search the given query string inside AnimeLyrics.

    :param str query: Query string. 
    :param str lang: Language to search in (jp, en)
    :param bool show_title: Show title at the top of the string

    :rtype: str
    :return: String of lyrics in given language
    """
    if lang != "en" and lang != "jp" and lang != "jp-kanji":
        raise InvalidLanguage("Unsupported language type")

    if lang == "jp":
        class_name = "romaji"
        song_idx = 0
    if lang == "jp-kanji":
        class_name = "kanji"
        song_idx = 0
    elif lang == "en":
        class_name = "translation"
        song_idx = 1

    url1 = get_1lyrics_url(query)
    url2 = get_2lyrics_url(query)

    soup = get_lyrics_soup(url1)
    soup2 = get_lyrics_soup(url2)

    if lang == "jp" or lang == "en":
        center_box = soup.find("div", {"class": "centerbox"})
        lyrics_table = center_box.find("table")
        lyrics = ""
        jplyrics = ""
        enlyrics = ""
        kanjilyrics = ""

        if lyrics_table is None:
            if lang == "en":
                raise MissingTranslatedLyrics("No translated lyrics found")

            lyrics = center_box.find("span", {"class": "lyrics"}).get_text()
        else:
            jplyrics_divs = lyrics_table.find_all("td", {"class": "romaji"})
            enlyrics_divs = lyrics_table.find_all("td", {"class": "translation"})
            for div in jplyrics_divs:
                jplyrics += div.get_text()
            for div in enlyrics_divs:
                enlyrics += div.get_text()

        kanjilyrics = soup2.find("div",{"id":"kanji"}).get_text()

    # remove trailing spaces and weird space
    enlyrics = enlyrics.replace("\xa0", " ").strip()
    jplyrics = jplyrics.replace("\xa0", " ").strip()
    kanjilyrics = kanjilyrics.replace("\xa0", " ").strip()

     # remove whitespaces from each line
    enstripped_lines = [line.strip() for line in enlyrics.splitlines()]
    jpstripped_lines = [line.strip() for line in jplyrics.splitlines()]
    kanjistripped_lines = [line.strip() for line in kanjilyrics.splitlines()]
    enlyrics = "\n".join(enstripped_lines)
    jplyrics = "\n".join(jpstripped_lines)
    kanjilyrics = "\n".join(kanjistripped_lines)


    enlyrics = enlyrics.splitlines()
    jplyrics = jplyrics.splitlines()
    kanjilyrics = kanjilyrics.splitlines()


    for item in range(len(kanjilyrics)):
        if kanjilyrics[item] == '' and kanjilyrics[item+1] == '' and kanjilyrics[item+2] == '':
            kanjilyrics[item] = ''
            kanjilyrics[item+1] = ''
            kanjilyrics[item+2] = ' '


    kanjilyrics = [space for space in kanjilyrics if space != '']


    lyricstuples = zip(enlyrics,jplyrics,kanjilyrics)
    finallyrics = '\n'.join(map(lambda x: str(x[0]) + '\n' + str(x[1]+ '\n' + str(x[2]) + '\n'), lyricstuples))
    print(finallyrics)

    if show_title:
        song_name, anime_name = get_song_info(soup)

        # song name might be english
        # set index to japanese name if english name not found
        if lang == "en" and len(song_name) == 1:
            song_idx = 0

        return "{} - {}\n\n{}".format(song_name[song_idx], anime_name, lyrics)
    else:
        return lyrics


def get_song_info(soup):
    """
    Retrieve the song name (english / japanese) and anime name

    :param BeautifulSoup soup: BeautifulSoup4 object of lyrics url

    :rtype [str, str]
    :return Tuple of song and anime name
    """
    crumbs = soup.find("ul", {"id": "crumbs"})
    crumbs_list = crumbs.find_all("li")
    song_name = [name.strip() for name in crumbs_list[-1].get_text().split("-")]
    anime_name = crumbs_list[-2].get_text()

    return (song_name, anime_name)


def get_lyrics_soup(url):
    """
    Get a BeautifulSoup4 representation of a url

    :param str url: URL to read

    :rtype: BeautifulSoup
    :return: BeautifulSoup4 object of the loaded url
    """
    html = requests.get(url)
    html.encoding = html.apparent_encoding
    html_text = html.content
    #print(html_text)
    soup = BeautifulSoup(html_text, "lxml")

    # convert all br into newlines
    for line_break in soup.find_all("br"):
        line_break.replace_with("\n")

    # remove all unwanted tags in the page
    tags_to_remove = ["dt", "sup"]

    for tag_name in tags_to_remove:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    return soup


def get_1lyrics_url(query):
    """
    Finds a url in AnimeLyrics website for a lyric

    :param str query: Query string.

    :rtype: str
    :return: String of the url page for the given query
    """
    for url in googlesearch.search("site:{} {}".format(__BASE_URL__, query), stop=10):
        # return the first page with .htm in the url as it contains lyrics
        # if str(url).endswith(".jis"):
        #     print (url)
        #     return url
        # else:
        if str(url).endswith(".htm"):

            return url

    # return none if query cannot find any pages
    raise NoLyricsFound

def get_2lyrics_url(query):
    """
    Finds a url in AnimeLyrics website for a lyric

    :param str query: Query string.

    :rtype: str
    :return: String of the url page for the given query
    """
    for url in googlesearch.search("site:{} {}".format(__BASE_URL__, query), stop=10):
        # return the first page with .htm in the url as it contains lyrics
        # if str(url).endswith(".jis"):
        #     print (url)
        #     return url
        # else:
        if str(url).endswith(".htm"):
            url = url.replace(".htm",".jis")
            print(url)
            return url

    # return none if query cannot find any pages
    raise NoLyricsFound

