#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-02-25
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

import requests
from bs4 import BeautifulSoup as BS

IMDB_BASE_URL = 'https://www.imdb.com'
TOP_MOVIE_CHART_URL = 'https://www.imdb.com/chart/top'
TOP_TV_CHART_URL = 'https://www.imdb.com/chart/toptv'
DOC_FOLDER = 'orig_documents/'

def get_video_list_from_imdb_chart(chart_url):
    """Given a url for a chart on IMDb, returns a list of (video_name, video_url) on that char"""
    video_list = list()
    webpage = requests.get(chart_url)
    soup = BS(webpage.content, 'html.parser')
    for td in (soup.find_all('td', class_='titleColumn')):
        video_name, video_relative_url = td.a.get_text(), td.a.get('href')
        video_list.append( (video_name, IMDB_BASE_URL + video_relative_url) )
    return video_list

def get_storyline_from_imdb_video(video_url):
    """Given a url for a video on IMDb, returns the storyline of that video"""
    webpage = requests.get(video_url)
    soup = BS(webpage.content, 'html.parser')

    h2_tag = soup.find('h2', string='Storyline')
    div_tag = h2_tag.next_sibling.next_sibling
    return div_tag.p.span.get_text()

if __name__ == '__main__':
    doc_id = 0
    movie_list = get_video_list_from_imdb_chart(TOP_MOVIE_CHART_URL)
    tv_list = get_video_list_from_imdb_chart(TOP_TV_CHART_URL)

    for video_name, video_url in movie_list + tv_list[:150]:
        doc_id += 1
        doc_f = open(DOC_FOLDER+str(doc_id)+'.txt', 'w')
        doc_f.write('# ' + video_name + '\n\n')
        storyline = get_storyline_from_imdb_video(video_url).strip()
        doc_f.write(storyline)


