#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-04-08
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

import requests
from bs4 import BeautifulSoup as BS
from multiprocessing import Pool
import csv

IMDB_BASE_URL = 'https://www.imdb.com'
FILM_LIST_TEMPLATE = 'https://www.imdb.com/search/title?title_type=feature&sort=boxoffice_gross_us,desc&start={}&ref_=adv_nxt' # feature film list sorted by U.S. box office descending
OUTPUT_FILE_PATH = '../data/imdb.csv'
NUM_VIDEOS = 4000
NUM_PROC = 8

def get_persons_related_to_imdb_video(video_url):
    """Given a url for a video on IMDb, returns persons (in particular, directors, writers and actors) related to the video"""
    directors, writers, actors = '', '', ''
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
        persons = ';'.join(persons)
        if person_type == 'Directed by':
            directors = persons
        elif person_type == 'Writing Credits':
            writers = persons
        elif person_type == 'Cast':
            actors = persons
    return directors, writers, actors

def get_info_about_imdb_video(video_url):
    """Given a url for a video on IMDb, returns info about that video, including title, year, genres, language, runtime, budget, revenue, directors, writers and actors"""
    webpage = requests.get(video_url)
    soup = BS(webpage.content, 'html.parser')

    # extract title and year
    h1_title = soup.find('div', class_='title_wrapper').h1
    title = h1_title.contents[0].strip()
    year = h1_title.span.a.get_text()

    # extract genres
    genres = list()
    div_storyline = soup.find('div', id='titleStoryLine')
    for div in (div_storyline.find_all('div', class_='see-more inline canwrap')):
        if 'Genre' in div.h4.string:
            for a_genre in div.find_all('a'):
                genres.append(a_genre.get_text().strip())
            break
    genres = ';'.join(genres)

    # extract languagem runtime, budget and revenue
    language, runtime, budget, revenue = '', '', '', ''
    div_details = soup.find('div', id='titleDetails')
    for div_txt_block in div_details.find_all('div', class_='txt-block'):
        try:
            attr_type = div_txt_block.h4.get_text()[:-1]
        except Exception:
            continue
        if attr_type not in ['Language', 'Budget', 'Runtime', 'Cumulative Worldwide Gross']:
            continue
        if attr_type == 'Language':
            language = div_txt_block.a.get_text()
        if attr_type == 'Budget':
            budget_str = div_txt_block.contents[2]
            budget = budget_str[budget_str.find('$')+1:].strip().replace(',', '')
        elif attr_type == 'Runtime':
            runtime = div_txt_block.time.string.split()[0]
        else:
            revenue_str = div_txt_block.contents[2]
            revenue = revenue_str[revenue_str.find('$')+1:].strip().replace(',', '')

    # extract directors, writers and actors
    directors, writers, actors = get_persons_related_to_imdb_video(video_url)

    return title, year, genres, language, runtime, budget, revenue, directors, writers, actors

def get_info_list_from_imdb_list(start_id):
    """Given a start id, return a list of info tuple, one for each video with id in range [start_id, start_id+50)"""
    info_list = []
    list_url = FILM_LIST_TEMPLATE.format(start_id)
    webpage = requests.get(list_url)
    # print(list_url, webpage)
    soup = BS(webpage.content, 'html.parser')
    for div in (soup.find_all('div', class_='lister-item mode-advanced')):
        div_content = div.find('div', class_='lister-item-content')
        video_relative_url = div_content.h3.a.get('href')
        try:
            info_list.append(get_info_about_imdb_video(IMDB_BASE_URL + video_relative_url))
        except Exception:
            continue
    print("Crawled movie {} to {}".format(start_id, start_id+50-1))
    return info_list

if __name__ == '__main__':
    pool = Pool(NUM_PROC)

    output_file = open(OUTPUT_FILE_PATH, 'w')
    csv_writer = csv.writer(output_file, delimiter=',')

    # start_ids = [1]
    start_ids = [start_id for start_id in range(1, NUM_VIDEOS, 50)]

    csv_writer.writerow(['title', 'year', 'genres', 'language', 'runtime', 'budget', 'revenue', 'directors', 'writers', 'actors'])
    id = 1
    for info_list in pool.map(get_info_list_from_imdb_list, start_ids):
        for info in info_list:
            csv_writer.writerow([id] + list(info))
            id += 1
