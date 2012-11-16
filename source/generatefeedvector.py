# -*- coding: utf-8 -*-
import feedparser
import re

import conf
import mongodb

# Returns title and dictionary of word counts for an RSS feed
def getwordcounts(feed_id):
  wc={}
  # Loop over all the entries
  for article in mongo.get_articles_from_collection(feed_id):
    summary = article["article_content"]

    # Extract a list of words
    words = getwords(feed["feed_title"] + ' ' + summary)
    for word in words:
      wc.setdefault(word,0)
      wc[word] += 1
  return feed["feed_title"], wc

def getwords(html):
  # Remove all the HTML tags
  txt=re.compile(r'<[^>]+>').sub('',html)

  # Split words by all non-alpha characters
  words=re.compile(r'[^A-Z^a-z]+').split(txt)

  # Convert to lowercase
  return [word.lower() for word in words if word!='']


apcount={}
wordcounts={}
mongo = mongodb.Articles(conf.MONGODB_ADDRESS, conf.MONGODB_PORT, \
                        conf.MONGODB_DBNAME, conf.MONGODB_USER, conf.MONGODB_PASSWORD)
feeds = mongo.get_all_feeds()
for feed in feeds:
  try:
    title,wc=getwordcounts(feed["feed_id"])
    wordcounts[title]=wc
    for word,count in list(wc.items()):
      apcount.setdefault(word,0)
      if count>1:
        apcount[word]+=1
  except:
    print('Failed to parse feed %s' % feed["feed_title"])

wordlist=[]
for w,bc in list(apcount.items()):
  frac=float(bc)/len(feeds)
  if frac>0.1 and frac<0.5:
    wordlist.append(w)

out=open('blogdata1.txt','w')
out.write('Blog')
for word in wordlist: out.write('\t%s' % word)
out.write('\n')
for blog,wc in list(wordcounts.items()):
  print(blog)
  out.write(blog)
  for word in wordlist:
    if word in wc: out.write('\t%d' % wc[word])
    else: out.write('\t0')
  out.write('\n')
