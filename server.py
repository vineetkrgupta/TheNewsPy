# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 21:37:39 2020

@author: V1n33t

update on 19 jan 2021  , added caching and resolved newapi exceptions
"""

from flask import Flask
from flask import render_template ,url_for, request , redirect
from flask_caching import Cache
from newsapi import NewsApiClient
import os
import sys


import apikeys


newsapikey = apikeys.newsapikey

cache = Cache()
cachetime= 600
#newsapi = NewsApiClient(api_key='657ed2aa3c614fbdbcc8a5311bbeb2e8')
newsapi = NewsApiClient(api_key= newsapikey)
heading = " Here is some latest news related to "
length= 0 #this might be stupidity as we its a global variable and maybe if multiple people are browsing it might lead to some unexpected behavious TODO fix 

lis= ["business", "entertainment", "general", "health", "science", "sports", "technology"]

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)
env_name = os.getenv('FLASK_ENV')
print(env_name)


def error(errordata):
    data=[{'urlToImage':None, 'url':None , 'title':None ,'source':None, 'description':errordata}]
    return data


def getnews(name , pag=1):
    global length
    try:
        top_headlines = newsapi.get_top_headlines(
                                              category=name,
                                              language='en',
                                              country='in',
                                              page=pag)
        
        length = len(top_headlines['articles'] )
        print("Api is being called....")
        return top_headlines['articles']

    except:
        
        length = 1
        return(error(sys.exc_info()[1]))


def searchnews(search , page=1):
    global length
    try:
        headlines = newsapi.get_everything(q=search,
                                        language='en',
                                        sort_by='relevancy',
                                        page=page)
        
        length = len(headlines['articles'] )
        print("Api is being called....")
        return headlines['articles']
    except:
        length = 1
        return(error(sys.exc_info()[1]))




@app.route("/")
@cache.memoize(timeout=cachetime)
def index():
  new = getnews("technology")
  global heading
#  print(new)
#  print(length)
  return render_template("index.html",x= length , news=new ,head=heading , topic ="technology" , page=1 , lay="/")


@app.route("/<int:page>")
@cache.memoize(timeout=cachetime)
def index1(page):
  try:
      new = getnews("technology" , page)
  except:
      return render_template("index.html",x= length , news=new ,head="Error Occured" , topic ="" )
  return render_template("index.html",x= length , news=new ,head=heading , topic = ("technology page- "+ str(page)) , page= page, lay= "/" )
  




@app.route("/news/<string:element>")
@cache.memoize(timeout=cachetime)
def news(element=None):
  print(element)
  element=str(element)
  if(element==None):
      return 0
  try:
      new = getnews(element,1)
      return render_template("index.html",x= length , news=new , head=heading , topic =element , page=1, lay= "/news/" + element + "/")
  except:
      pass

@app.route('/news/<element>/<int:page>')
@cache.memoize(timeout=cachetime)
def newspg(element, page):
    
  #print(page)
  try:
      
      new = getnews(element , page)
      return render_template("index.html",x= length , news=new , head=heading , topic =element +" page- "+ str(page) , page= page ,lay="/news/"+element+"/" )
  except:
      page=1
      return render_template("index.html",x= length , news=new ,head="Error Occured" , topic ="" )
  
  






@app.route("/aboutus")
@cache.memoize(timeout=cachetime)
def aboutus():
    return render_template("about us.html")


@app.route("/contribute")
@cache.memoize(timeout=cachetime)
def contribute():
    return render_template("contribute.html")

@app.route("/servertype")
@cache.memoize(timeout=cachetime)
def servertype():
    return(request.environ['REMOTE_ADDR'])


@app.route('/search', methods=['GET', 'POST'])
@cache.memoize(timeout=cachetime)
def search():
    query= request.form['search_query'] 
    new =searchnews(query)
    print(query)
#    print(new)
#    print(length)
    return render_template("index.html",x= length , news=new , head=heading ,page=1, topic =query , lay="/search/"+query+"/")

@app.route('/search/<query>/<int:page>')
@cache.memoize(timeout=cachetime)
def searchpg(query, page):
    
    print(query , page)
    try:
        new =searchnews(query,page)
    except:
        page=1
        return render_template("index.html",x= length , news=new ,head="Error Occured" , topic ="" )
    
    return render_template("index.html",x= length , news=new , head=heading , topic =query +" page- "+ str(page) , page= page ,lay="/search/"+query+"/" )



#404 error redirect 
@app.route('/<path:subpath>')
@cache.memoize(timeout=cachetime)
def pagenotfound(subpath):
    print(subpath)
    return redirect (url_for('index'))
#    return index()
#    
    #return render_template("404.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    #app.run()