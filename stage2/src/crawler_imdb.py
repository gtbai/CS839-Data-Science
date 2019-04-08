#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-02-25
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

import requests
from bs4 import BeautifulSoup as BS

IMDB_BASE_URL = 'https://www.imdb.com'
FILM_LIST_TEMPLATE = 'https://www.imdb.com/search/title?title_type=feature&sort=boxoffice_gross_us,desc&start={}&ref_=adv_nxt' # feature film list sorted by U.S. box office descending
DATA_FOLDER_PATH = 'data/'
NUM_DOCS = 50

def get_video_list_from_imdb_list(list_url):
    """Given a url for a film list on IMDb, returns a list of (video_name, video_url) on that film list"""
    video_list = list()
    webpage = requests.get(list_url)
    soup = BS(webpage.content, 'html.parser')
    for div in (soup.find_all('div', class_='lister-item mode-advanced')):
        # print(div)
        div_content = div.find('div', class_='lister-item-content')
        a_title = div_content.h3.a
        video_name, video_relative_url = a_title.string, a_title.get('href')
        video_list.append( (video_name, IMDB_BASE_URL + video_relative_url) )

    return video_list

def get_info_from_imdb_video(video_url):
    """Given a url for a video on IMDb, returns info that video"""
    webpage = requests.get(video_url)
    soup = BS(webpage.content, 'html.parser')

    # extract title and year
    h1_title = soup.find('div', class_='title_wrapper').h1
    title = h1_title.contents[0].strip()
    year = h1_title.span.a.string

    return title, year


if __name__ == '__main__':
    doc_id = 0
    # movie_list = get_video_list_from_imdb_chart(TOP_MOVIE_CHART_URL)
    # tv_list = get_video_list_from_imdb_chart(TOP_TV_CHART_URL)

    # for video_name, video_url in movie_list + tv_list[:150]:
    #     doc_id += 1
    #     doc_f = open(DOC_FOLDER+str(doc_id)+'.txt', 'w')
    #     doc_f.write('# ' + video_name + '\n\n')
    #     storyline = get_storyline_from_imdb_video(video_url).strip()
    #     doc_f.write(storyline)

    while doc_id < NUM_DOCS:
        movie_list = get_video_list_from_imdb_list(FILM_LIST_TEMPLATE.format(doc_id+1))

        for video_name, video_url in movie_list:
            get_info_from_imdb_video(video_url)

        doc_id += len(movie_list)


