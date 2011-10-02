#!/usr/bin/env python
from BeautifulSoup import BeautifulSoup
from openpyxl.reader.excel import load_workbook
import urllib2
import urllib
import httplib
import cookielib
import sys

code = sys.argv[1]
print code

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):     
    def http_error_301(self, req, fp, code, msg, headers):  
        result = urllib2.HTTPRedirectHandler.http_error_301( 
            self, req, fp, code, msg, headers)              
        result.status = code                                 
        return result                                       

    def http_error_302(self, req, fp, code, msg, headers):   
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)              
        result.status = code
	result.headers = headers.dict
	result.path = headers.dict['location']                                
        return result

def initHTTPHandler():
	cj = cookielib.CookieJar();
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), SmartRedirectHandler())
	urllib2.install_opener(opener)
	return opener

def esoeAuth(username, password):
	authURL = 'https://esoe.qut.edu.au/signin'
	authData = urllib.urlencode({'esoeauthn_user' : username, 'esoeauthn_pw' : password})
	authHeaders = {
	'Content-type' : 'application/x-www-form-urlencoded',
	'User-Agent' : "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:6.0.2) Gecko/20100101 Firefox/6.0.2",
	}
	req = urllib2.Request(authURL, authData, authHeaders)
	response = opener.open(req)
	return response
	
def ezpAuth():
	url = 'https://login.ezp01.library.qut.edu.au/login'
	headers = {
		"User-Agent" : "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:6.0.2) Gecko/20100101 Firefox/6.0.2",
		"Accept" : "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language" : "en-gb,en;q=0.5",
		"Connection" : "keep-alive" }
	data = None
	req = urllib2.Request(url, data, headers)
	response = opener.open(req)
	
	url = response.path
	req = urllib2.Request(url, data, headers)
	response = opener.open(req)
	url = response.path
	req = urllib2.Request(url, data, headers)
	response = opener.open(req)
	soup = BeautifulSoup(''.join(response.read()))
	SAMLTag = soup.find('input',attrs={'name':'SAMLRequest', 'type':'hidden'}) #Find the proper tag
	SAMLRequest = SAMLTag['value']
	
	url = 'https://esoe.qut.edu.au/sso'
	data = urllib.urlencode({'SAMLRequest' : SAMLRequest})
	req = urllib2.Request(url, data, headers)
	response = opener.open(req)
	soup = BeautifulSoup(''.join(response.read()))
	SAMLTag = soup.find('input',attrs={'name':'SAMLResponse', 'type':'hidden'})
	SAMLResponse = SAMLTag['value']

	url = 'https://ezpauth.library.qut.edu.au/spep/sso'
	data = urllib.urlencode({'SAMLResponse' : SAMLResponse, 'RelayState' : ''})
	req = urllib2.Request(url, data, {'Referer' : 'https://esoe.qut.edu.au/sso'})
	response = opener.open(req)
	return response
	
def finDownload(code):
	url = 'http://datanalysis.morningstar.com.au.ezp01.library.qut.edu.au/af/company/financialdownload?xsl_dltab=financial10yrs&download=xls&filetype=xls&ASXCode='+ code + '&xtm-licensee=dat'
	xls = opener.open(url).read()
	filename = '/Users/mnbbrown/Desktop/fin' + code + '.xls'
	local = open(filename, "w")
	local.write(xls)
	local.close()
	return filename	

opener = initHTTPHandler()
#Authenticate with Enterprise Sign On Engine
esoeAuth('***REMOVED***', '***REMOVED***')
ezpAuth()
file = finDownload(code)
print file

