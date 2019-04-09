#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup as BS
from multiprocessing import Pool
import csv


TMDB_MOVIE_LIST_URL = 'https://www.themoviedb.org/movie?page='
TMDB_BASE_URL = 'https://www.themoviedb.org'

TOTAL_NUMBER = 4000 # TODO: change this to 4000
MOVIES_PER_PAGE = 20
NUM_PROC = 8 
OUTPUT_FILE_PATH = '../data/tmdb.csv'

def get_crew_list(soup, type):
    list = []
    crew = soup.find('h4', text=type).parent
    div_parts = crew.find_all('div', class_='info')
    for div in div_parts:
        list.append(div.find('a').get_text())
    return ';'.join(list)


def get_actors(soup):
    list = []
    candidates = soup.find_all('div', class_='split')
    for candidate in candidates:
        if candidate.find('h3') and candidate.find('h3').get_text().startswith('Cast'):
            lis = candidate.find_all('li')
            for li in lis:
                list.append(li.find('div', class_='info').find('a').get_text())
            break
    return ';'.join(list)


def get_movie_info(home_url):
    """
    Given a url for a page of a movie, return the movie info as a list
    """
    info = []
    home_page = requests.get(home_url)
    home_soup = BS(home_page.content, 'html.parser')
    cast_crew_url_suffix = home_soup.find('a', text='Full Cast & Crew').get('href')
    cast_crew_page = requests.get(TMDB_BASE_URL + cast_crew_url_suffix)
    cast_crew_soup = BS(cast_crew_page.content, 'html.parser')
    # title
    title = home_soup.find('h2').get_text()
    info.append(title)
    # print("Name: " + title)
    # year
    year = home_soup.find('span', class_='release_date').get_text()
    year = year[1:-1]
    info.append(year)
    # genres
    genres = []
    genre_sec = home_soup.find('bdi', text='Genres').parent.parent.find('ul').find_all('li')
    for g in genre_sec:
        genres.append(g.find('a').get_text())
    info.append(';'.join(genres))
    # language
    language_tag = home_soup.find('bdi', text='Original Language')
    raw_language = language_tag.parent.parent.get_text()
    language = raw_language.split(' ')[2]
    info.append(language)
    # runtime
    runtime_tag = home_soup.find('bdi', text='Runtime')
    raw_time = runtime_tag.parent.parent.get_text()
    split_time = raw_time.split()
    runtime = int(split_time[1][:-1]) * 60 + int(split_time[2][:-1])
    info.append(str(runtime))
    # budget
    budget_tag = home_soup.find('bdi', text='Budget')
    raw_budget = budget_tag.parent.parent.get_text().split()[1]
    budget = raw_budget[1:].split('.')[0].replace(',','')
    info.append(budget)
    # revenue
    revenue_tag = home_soup.find('bdi', text='Revenue')
    raw_revenue = revenue_tag.parent.parent.get_text().split()[1]
    revenue = raw_revenue[1:].split('.')[0].replace(',','')
    info.append(revenue)
    # directors
    directors = get_crew_list(cast_crew_soup, "Directing")
    info.append(directors)
    # writers
    writers = get_crew_list(cast_crew_soup, "Writing")
    info.append(writers)
    # actors
    actors = get_actors(cast_crew_soup)
    info.append(actors)
    return info


def get_movies_in_page(movie_list_url):
    """
    Given a url for a page of the movie list in TMDb, returns the movie info
    on that page as a list
    """
    movies = []
    movie_list = requests.get(movie_list_url)
    soup = BS(movie_list.content, 'html.parser')
    for link in soup.find_all('a', class_='title result'):
        url = TMDB_BASE_URL + link.get('href')
        try:
            movies.append(get_movie_info(url))
        except Exception:
            continue
    print("Crawled movie list on page {}".format(movie_list_url[movie_list_url.rfind('=')+1:]))
    return movies

if __name__ == '__main__':
    pool = Pool(NUM_PROC)

    output_file = open(OUTPUT_FILE_PATH, 'w')
    csv_writer = csv.writer(output_file, delimiter=',')

    # start_ids = [1]
    movie_list_urls = [TMDB_MOVIE_LIST_URL + str(page_no) for page_no in range(1, int(TOTAL_NUMBER / MOVIES_PER_PAGE)+1)]

    csv_writer.writerow(['title', 'year', 'genres', 'language', 'runtime', 'budget', 'revenue', 'directors', 'writers', 'actors'])
    id = 1
    for movies in (pool.map(get_movies_in_page, movie_list_urls)):
        for movie in movies:
            csv_writer.writerow([id] + list(movie))
            id += 1
