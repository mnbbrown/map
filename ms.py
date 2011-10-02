#!/usr/bin/env python
# encoding: utf-8
"""
ms.py
Created by Matthew Brown on 2011-10-02.
"""

import sys
import httplib2
import csv

code = sys.argv[1]

def finDownload(code,report):
	h = httplib2.Http('.cache')
	url = 'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t=' + code + '&region=AUS&culture=en_us&reportType='+ report + '&period=12&dataType=A&order=asc&columnYear=5&rounding=1&view=raw&productCode=usa&denominatorView=raw&number=1'
	headers, data = h.request(url)
	data = data.split("\n")
	return data
	
balancesheet = csv.reader(finDownload(code,'is'))
for row in balancesheet:
	print row

