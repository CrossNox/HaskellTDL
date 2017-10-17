#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import urllib2
import json
from datetime import datetime, timedelta
import time

def dateGen():
    start = datetime(2007,7,5)
    end = datetime.today()
    for x in range(0, (end-start).days):
        yield (start + timedelta(days=x)).date()

def reposPorDia(date):
    request = urllib2.Request('https://api.github.com/search/repositories?q=created:'+date+'&per_page=1', 
                    headers={"Accept" : "application/vnd.github.mercy-preview+json",
                    "Authorization" : "token b076eb711f84200f2a7fd10d91826069e9e26d6a"})
    response = urllib2.urlopen(request)
    json_resp = json.loads(response.read()) 
    return (date,json_resp["total_count"],response.info().getheader('X-RateLimit-Remaining'),response.info().getheader('X-RateLimit-Reset'))

def getRepos():
    with open("repos_totales_por_dia.csv","a") as salida:
        for i in dateGen():
            done = False
            while(not done):
                try:
                    res = reposPorDia(str(i))
                    salida.write("{},{}\n".format(res[0],res[1]))
                    print "{} --- {} => {} --- Remaining: {} until {}".format(datetime.now(),res[0],res[1],res[2],res[3])
                    if(int(res[2])==0):
                        sleepDuration = int(res[3])-time.time()
                        print "sleeping for {} minutes".format(sleepDuration/60)
                        time.sleep(sleepDuration)
                    done = True
                except Exception as e:
                    print "Exception!"
                    print e
                    time.sleep(30)
 

getRepos()