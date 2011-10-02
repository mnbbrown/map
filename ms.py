#!/usr/bin/env python
# encoding: utf-8
"""
ms.py
Created by Matthew Brown on 2011-10-02.
"""

import sys
import httplib2

def finDownload(code,report):
	h = httplib2.Http('.cache')
	url = 'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t=FGE&region=AUS&culture=en_us&reportType='+ report + '&period=12&dataType=A&order=asc&columnYear=5&rounding=3&view=raw&productCode=usa&denominatorView=raw&number=3'
	headers, csv = h.request(url)
	print headers.status
	print csv