#!/usr/bin/env python
# encoding: utf-8
"""
findata.py

Created by Matthew Brown on 2011-10-11.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import requests
import inspect
import csv
import time
from BeautifulSoup import BeautifulSoup
import MySQLdb



def initHTTP():
	cookiefile = "./.tmp/cookies"
	url = "http://www.aspecthuntley.com.au.ezp01.library.qut.edu.au/af/finhome?xtm-licensee=finanalysis"
	headers = {"User-Agent" : "User-Agent: Mozilla/5.0 Gecko/20100101 Firefox/6.0.2"}
	with requests.session() as session:
		
		if os.path.isfile(cookiefile):
			session.cookies.load(cookiefile, True, True)
		
		r = session.get(url, headers=headers, allow_redirects = False)
		if r.status_code != 200:
			session.cookies.clear()
			print "Not Authenticated: " + str(r.status_code) + " Attempting to Authenticate..."
			session = authenticate("***REMOVED***", "***REMOVED***", session)
			session.cookies.save(cookiefile, True, True)
		
	return session
			
	
	
	
	

def authenticate(username, password, session):
	
	
	
	#Begin Session
	
	
		
	#Authenticate with QUT Enterprise Sign-On Engine

	url = "https://esoe.qut.edu.au/signin"
	data = {'esoeauthn_user' : username, 'esoeauthn_pw' : password}
	headers = {
	'Content-type' : 'application/x-www-form-urlencoded',
	'User-Agent' : "User-Agent: Mozilla/5.0 Gecko/20100101 Firefox/6.0.2",
	}

	r = session.post(url, data, headers=headers)

	#Authenticate with EzProxy
	
	url = 'https://login.ezp01.library.qut.edu.au/login'
	headers = {"User-Agent" : "User-Agent: Mozilla/5.0 Gecko/20100101 Firefox/6.0.2"}
	
	r = session.get(url, headers=headers)
	
	#Parse SAML Request from EzProxy with BeautifulSoup
	
	soup = BeautifulSoup(''.join(r.content))
	SAMLTag = soup.find('input',attrs={'name':'SAMLRequest', 'type':'hidden'}) #Find the SAMLRequest tag
	SAMLRequest = SAMLTag['value']
	
	#Post SAML Request to ESOE
	
	url = 'https://esoe.qut.edu.au/sso'
	data = {'SAMLRequest' : SAMLRequest}
	
	r = session.post(url, data, headers=headers)
	
	#Parse SAML Response from ESOE with BeautifulSoup
	
	soup = BeautifulSoup(''.join(r.content))
	SAMLTag = soup.find('input',attrs={'name':'SAMLResponse', 'type':'hidden'})
	SAMLResponse = SAMLTag['value']
	
	#Post SAML Response to EzProxy
	
	url = 'https://ezpauth.library.qut.edu.au/spep/sso'
	data = {'SAMLResponse' : SAMLResponse, 'RelayState' : ''}
	
	r = session.post(url, data, headers=headers)

	
	return session
	
def finDownload(code = None, reportID = None):
	
	
	url = 'http://www.aspecthuntley.com.au.ezp01.library.qut.edu.au/af/company/csv/annual'+ reportID + '?ASXCode=' + code + '&download=csv&filetype=csv&xtm-licensee=finanalysis'
	data = session.get(url).content
	data = data.splitlines()
	lines = list(csv.reader(data))
	
	lines.pop(0)
	lines[0].pop(0)
	lines[0].pop()
	for i,datestr in enumerate(lines[0]):
		datestr = time.strptime(datestr,"%B/%Y")
		lines[0][i] = time.strftime("%Y-%m-%d",datestr)
	
	lines[0].insert(0,"Accounts")

	for i,line in enumerate(lines):
		if line == []:
			lines.pop(i)
	conn = MySQLdb.connect(host="one.mnbbrown.com",user="root",passwd="@admin13",db="finData")
	cursor = conn.cursor()
	i = iter(lines)
	i.next()
	for account in i:
		if len(account) > 1 and account[0].find("Total") != 0:
			account[0] = account[0].replace(".","")
			account[0] = account[0].split(" ")
			abbrev = {"CA":"Current Assets","CL":"Current Liabilities","NCA":"Non-Current Assets","NCL":"Non-Current Liabilities","S/T":"Short Term", "L/T":"Long Term", "PP&E":"Property, Plant and Equipment"}
			for i, string in enumerate(account[0]):
				if string == "CA" or string == "CL" or string == "NCA" or string == "NCL" or string == "S/T" or string == "L/T" or string == "PP&E":
					account[0][i] = abbrev[string]
			accountName = "%".join(account[0])
			accountName += "%"
			query = "SELECT accountID FROM accounts WHERE name LIKE \'%s\'" % accountName
			query
			cursor.execute(query)
			result = cursor.fetchone()
			try: accountID
			except NameError: accountID = '0'
			print account[0][0]
			if int(accountID) > 100 and account[0][0] == "Inventories": 
				result = ['104']
			if int(accountID) > 200 and account[0][0] == "Inventories": 
				result = ['202']
			for i in result:
				accountID = i
			print accountID
			j = iter(account)
			j.next()
			for c, balance in enumerate(j):
				if balance != '':
					balanceDate = lines[0][c+1]
					balanceValue = float(balance.replace(",",""))
					query = "INSERT INTO balances (balanceID, date, accountID, reportID, amount, stockCode) VALUES (NULL, \'%s\', \'%s\', \'%s\', %s, \'%s\')" %  (balanceDate, accountID, reportID, balanceValue, code)
					#cursor.execute(query)
					#conn.commit()
	cursor.close()
	conn.close()
		
		

	#Write to clean CSV
	
	dataFile = csv.writer(open("data.csv",'w'))
	for row in lines:
		dataFile.writerow(row)
	
session = initHTTP()
finDownload("NHC","bs")



