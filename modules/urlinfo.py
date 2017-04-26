#!/usr/bin/env python
"""
urlinfo.py - Show URL Info to Channel

http://code.google.com/p/barn-phenny-plugins/
http://inamidst.com/phenny/
"""
import re, urllib2, HTMLParser

class urlinfo_open(object):
	def __init__(self, v_url):
		if not v_url.startswith('http'): 
			return
		try:
			self.url = v_url
			self.request = urllib2.Request(self.url)
			self.opener = urllib2.build_opener()
			self.urlobj = self.opener.open(self.request)
			self.data = self.urlobj.read()
			self.info = self.urlobj.info()
			self.finalurl = self.urlobj.geturl()
			self.urlobj.close()
		except urllib2.HTTPError, err:
			self.data = False
			return

def urlinfo_title(phenny, input):
	m = re.search('(http(s|)://[^ ]*)', input)
	if m:
		url = m.group(0)
		
		exclude = ['https?:\/\/(.*\.)?wikipedia\.org', 'https:\/\/(.*\.)?gazellegames\.net']
		for expattern in exclude:
			if(re.match(expattern, url)):
				return
		
		if url.startswith('http://gazellegames.net'):
			sslified = re.sub(r'^http', 'https', url, re.I)
			phenny.say("10[ 3SSL:07 %s 10]" % (sslified))
		else:
			urlobj = urlinfo_open(url)
			if urlobj.data:
				mre = re.compile(r'<title>(.+)</title>', re.I | re.M)
				m = mre.search(urlobj.data)
				if m:
					title = m.group(0)
					title = title[title.find(">")+1:]
					title = title[:title.rfind("<")]
					h = HTMLParser.HTMLParser()
					title = h.unescape(title)
					try:
						phenny.say("10[ 3Title:07 {0} 10]".format(title))
					except:
						print("Title: Couldn't say the title - non-ascii?")
				else:
					print("Title: Failed to find title")
	else:
		print("Title: Failed to parse page")

#urlinfo_title.rule = r'.*http(s|)://.*'
#urlinfo_title.priority = 'high'
#urlinfo_title.thread = False

if __name__ == '__main__': 
   print __doc__.strip()
