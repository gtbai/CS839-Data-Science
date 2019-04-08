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
    video_list = []
    webpage = requests.get(list_url)
    soup = BS(webpage.content, 'html.parser')
    for div in (soup.find_all('div', class_='lister-item mode-advanced')):
        div_content = div.find('div', class_='lister-item-content')
        a_title = div_content.h3.a
        video_name, video_relative_url = a_title.string, a_title.get('href')
        video_list.append( (video_name, IMDB_BASE_URL + video_relative_url) )

    return video_list

def get_persons_related_to_imdb_video(video_url):
    directors, writers, actors = [], [], []
    credits_url = video_url[:video_url.rfind('?')] + 'fullcredits'
    webpage = requests.get(credits_url)
    soup = BS(webpage.content, 'html.parser')
    div_credits_content = soup.find('div', id='fullcredits_content')
    for h4 in div_credits_content.find_all('h4'):
        person_type = h4.contents[0].strip()
        if person_type not in ['Directed by', 'Writing Credits', 'Cast']:
            continue
        persons = []
        person_table = h4.find_next_sibling('table')

        for tr in person_table.find_all('tr'):
            class_filter = None if person_type == 'Cast' else 'name'
            td_name = tr.find('td', class_=class_filter)
            if td_name == None:
                continue
            persons.append(td_name.a.string.strip())
        if person_type == 'Directed by':
            directors = persons
        elif person_type == 'Writing Credits':
            writers = persons
        elif person_type == 'Cast':
            actors = persons
    return directors, writers, actors

def get_info_from_imdb_video(video_url):
    """Given a url for a video on IMDb, returns info that video"""
    webpage = requests.get(video_url)
    soup = BS(webpage.content, 'html.parser')

    # extract title and year
    h1_title = soup.find('div', class_='title_wrapper').h1
    title = h1_title.contents[0].strip()
    year = h1_title.span.a.string

    # extract genres
    genres = list()
    div_storyline = soup.find('div', id='titleStoryLine')
    for div in (div_storyline.find_all('div', class_='see-more inline canwrap')):
        if 'Genre' in div.h4.string:
            for a_genre in div.find_all('a'):
                genres.append(a_genre.string)
            break

    # extract budget, runtime and revenue
    budget, runtime, revenue = '', '', ''
    div_details = soup.find('div', id='titleDetails')
    for div_txt_block in div_details.find_all('div', class_='txt-block'):
        try:
            number_type = div_txt_block.h4.string[:-1]
        except Exception:
            continue
        if number_type not in ['Budget', 'Runtime', 'Cumulative Worldwide Gross']:
            continue
        if number_type == 'Budget':
            budget_str = div_txt_block.contents[2]
            budget = budget_str[budget_str.find('$')+1:].strip().replace(',', '')
        elif number_type == 'Runtime':
            runtime = div_txt_block.time.string.split()[0]
        else:
            revenue_str = div_txt_block.contents[2]
            revenue = revenue_str[revenue_str.find('$')+1:].strip().replace(',', '')

    # extract directors, writers and actors
    directors, writers, actors = get_persons_related_to_imdb_video(video_url)

    return title, year, genres, budget, runtime, revenue, directors, writers, actors

if __name__ == '__main__':
    doc_id = 0

    while doc_id < NUM_DOCS:
        movie_list = get_video_list_from_imdb_list(FILM_LIST_TEMPLATE.format(doc_id+1))

        for video_name, video_url in movie_list:
            print(get_info_from_imdb_video(video_url))

        doc_id += len(movie_list)
