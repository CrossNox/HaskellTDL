#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import urllib2
import json
from datetime import datetime, timedelta
import time
import argparse

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def dateGen(start,end):
    for x in range(0, (end-start).days):
        yield (start + timedelta(days=x)).date()

def reposPorDia(date,per_page,language):
    languageStr = ""
    if (language != "all"):
        languageStr = "+language:"+language
    request = urllib2.Request('https://api.github.com/search/repositories?q=created:'+date+languageStr+'&per_page='+str(per_page), 
                    headers={"Accept" : "application/vnd.github.mercy-preview+json",
                    "Authorization" : "token b076eb711f84200f2a7fd10d91826069e9e26d6a"})
    response = urllib2.urlopen(request)
    json_resp = json.loads(response.read()) 
    return (date,json_resp["total_count"],response.info().getheader('X-RateLimit-Remaining'),response.info().getheader('X-RateLimit-Reset'))

def query(language, start_date, end_date, per_page):
    filename = (language)
    with open(language+"_"+str(start_date.date())+"_"+str(end_date.date())+".csv","w") as salida:
        for i in dateGen(start_date,end_date):
            done = False
            while(not done):
                try:
                    res = reposPorDia(str(i),per_page,language)
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

def getRepos():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", 
        "--language", 
        help = "The language has to be a string", 
        default = "all")
    parser.add_argument(
        "-s", 
        "--start", 
        help = "The start date format is YYYY-MM-DD", 
        type = valid_date, 
        default = "2007-1-1")
    parser.add_argument(
        "-e", 
        "--end", 
        help = "The end date format is YYYY-MM-DD", 
        type = valid_date, 
        default = datetime.today().strftime("%Y-%m-%d"))
    parser.add_argument(
        "-p", 
        "--per_page", 
        help = "Default value of 10 results per page", 
        default = 100)
    args = parser.parse_args()
    if (args.end <= args.start):
        raise Exception("Invaid date")
    query(args.language,args.start,args.end,args.per_page)

getRepos()