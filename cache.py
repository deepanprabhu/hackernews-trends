import cPickle as pickle;
import hashlib;
import os.path;
import sys;
import base64;

CACHE_DIR = "./cache";

def createIfNotExists(dir):
	if not os.path.exists(dir):
		os.makedirs(dir);

def getFileName(url):
	m = hashlib.md5(url).digest();
	return base64.urlsafe_b64encode(m);

def cache_put(key, value):
	try:
		pickle.dump(value,open(os.path.join(CACHE_DIR, getFileName(key)),"wb"))
	except:
		e = sys.exc_info()[0];
		print e;

def cache_get(key):
	fileName = os.path.join(CACHE_DIR,getFileName(key));
	if(os.path.isfile(fileName)):
		return pickle.load(open(fileName,"rb"));
	else:
		return None;