#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-03-07 17:22:09
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

from geotext import GeoText

if __name__ == '__main__':
    text = open('../filtered_documents/289.txt').readlines()[2]
    print(text)
    places = GeoText(text)
    print (places.cities)