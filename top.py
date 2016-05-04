from firebase import firebase
import re;
import operator;
import urllib2;
import sys;
import html2text;
from lxml import html;
import lxml.html;
from lxml.html.clean import clean_html;
from lxml.html.clean import Cleaner;
from bs4 import BeautifulSoup;
import chardet;
from cache import *;

createIfNotExists(CACHE_DIR);


firebase = firebase.FirebaseApplication('https://hacker-news.firebaseio.com/', None)
items = firebase.get('/v0/topstories', None)

def get_stop_words():
	f = open("stopwords.txt");
	words = f.read();
	words = words.split("\n");
	return words;

def readUrl(url):
    try:
        response = cache_get(url);
        if ( response == None ):
            response = urllib2.urlopen(url);
            response = response.read();
            cache_put(url, response);
        return response;
    except urllib2.HTTPError as f:
		e = sys.exc_info()[0];
		print e;
		return "";

def stripHTML(str, stripperBackend=0):
    if( stripperBackend == 0 ):
        h = html2text.HTML2Text();
        return h.handle(str);
    elif( stripperBackend == 1 ):
        cleaner = Cleaner(allow_tags=[''], remove_unknown_tags=False)
        root = lxml.html.fromstring(str);
        root = cleaner.clean_html(root);
        return lxml.html.tostring(root);
    elif( stripperBackend == 2 ):
        return ''.join(BeautifulSoup(str).findAltl(text=True));


def processHTML(url, str, stripperBackend=0):
	try:
		encoding = chardet.detect(str);
		print encoding['encoding'];
		result = stripHTML(str.decode('utf8'), stripperBackend);
		return result;
	except:
		e = sys.exc_info()[0];
		print e;
		print "Level 2"
		print url;
		try:
			if(encoding['encoding'] == "ISO-8859-2"):
				result = stripHTML(str.decode('iso-8859-2'), stripperBackend);
			elif(encoding['encoding'] == "ISO-8859-1"):
				result = stripHTML(str.decode('iso-8859-1'), stripperBackend);
			else:
				result = stripHTML(str, stripperBackend);
			return result;
		except:
			f = sys.exc_info()[0];
			print f;
			print "Level 3"
			print url;
			return "";

def replacer(astr):
	replace = ["\n","[","#","]","*","(",")","+","]","[","}","{"];
	for item in replace:
		astr = astr.replace(item,'');
	return astr;

r = re.compile(r"(http://[^ ]+)")
rs = re.compile(r"(https://[^ ]+)");
rsym = re.compile(r'[^\w]');

count = 1;
readTotalStories = 10;
stopwords = get_stop_words();
totalWordCounter = 0;

for item in items:
	print item;
	countWords = {}
	theItem = firebase.get('v0/item/{0}.json?print=pretty'.format(item), None)

	if "url" in theItem and theItem["url"].find(".pdf") == -1:

		text = processHTML(theItem['url'], readUrl(theItem['url']), 1)

		#	Remove URLS		
		text = r.sub('', text)
		text = rs.sub('', text)

		filteredtext = ['']

		for aword in text.split(" "):

			aStrip = aword.strip();
			aRemoveSlashN = replacer(aStrip)
			aRemoveSymbols = rs.sub('',aRemoveSlashN);

			afinal = aRemoveSymbols;

			if not afinal in stopwords and afinal != '':
				filteredtext.append(afinal)

				if not afinal in countWords:
					countWords[afinal]=1;
				else:
					countWords[afinal] = countWords[afinal] + 1;

		importantWords = {}
		for key in countWords:
			if countWords[key] > 1:
				importantWords[key] = countWords[key];
				totalWordCounter = totalWordCounter + 1;

		print sorted(importantWords, key=importantWords.get	)
		print "_____________________________________________________" + str(count) + "___________________________________________________________________________";

	if count == readTotalStories:
		break;
	else:
		count = count + 1