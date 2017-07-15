from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Greeting
import re

import json
import pyowm
import nltk
import feedparser
from nltk import word_tokenize
from bs4 import BeautifulSoup
from collections import OrderedDict

import requests
import random
import wikipedia

from gettingstarted.synm_dict import find_match



# Create your views here.

def verify(chunkGram, tags):
    chunkParser = nltk.RegexpParser(chunkGram)
    chunked = chunkParser.parse(tags)

    for t in chunked.subtrees():
        if t.label() == 'Chunk':
            return True

    return False

def small_talk(s, pronoun, nouns, adjectives, verbs):
    if pronoun == 'you' or pronoun == 'your':
    # If user asks about the bot
        s1 = ""
        s2 = "that"
        for verb in verbs:
            s1 += verb

        for noun in nouns:
            s2 = noun

        if len(verbs) > 0:
             vbs = [
                "Ya i " + s1 + s2 ,
                "I am an expert in " + s2,
                "No i have no idea about that"
             ]
             return random.choice(vbs)

        if len(adjectives) > 0:
            adj = [
                "I don't think I am " + adjectives[0],
                "Not really",
                "I am a lot better than that",
                "I already know that I am " + adjectives[0]
            ]
            return random.choice(adj)

        noun1 = [
                "I don't know my name but i was designed by Aadil",
                "Why do you want to know that",
                "That is a secret",
                "I don't think i can answer that",
                "I don't think that matters"
        ]
        return random.choice(noun1)

def get_temp(w):
    loc = ""
    #return HttpResponse(w.subtrees())
    for i in w.subtrees():
        if i.label() == 'GPE':
            loc = i[0][0]

    owm = pyowm.OWM('a0fd740e29e007169ed8a60f187ef972')
    obs = owm.weather_at_place(loc)
    w = obs.get_weather()
    return ("It is " +  str(w.get_temperature('celsius')['temp']) + " degrees in " + loc)

def convert(s):
    res = ""
    url = "https://www.google.co.in/search?q="
    url += s
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    try:
        res = soup.find(class_='_Qeb _HOb').get_text() + soup.find(class_='_Peb _rkc').get_text()
        return res
    except:
        try:
            soup = soup.find(class_='std _tLi').get_text()
            return soup
        except:
            print ("Nothing found")

def get_time(s, w):
    loc = ""
    for i in w.subtrees():
        if i.label() == 'GPE' or i.label == 'GPS':
            loc = " in " + i[0][0]

    url = "https://www.google.co.in/search?q="
    url += s
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html5lib')
    return "It is " + soup.find(class_='_rkc _Peb').get_text() + loc

def get_score(s):
    url = "https://www.google.co.in/search?q="
    url += s
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    return soup.find(class_='_Pc').get_text()

def no_match(s, nouns):
    def check(_class, soup):
        try:
            soup = soup.find(class_=_class)
            return soup.get_text()
        except:
            return 'null'

    url = "https://www.google.co.in/search?q=" + s
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    classes = ['_tXc', '_sPg']
    for c in classes:
        res = check(c, soup)
        if res != 'null':
            return res

    return 'null'

    # subject = ''
    # for noun in nouns:
    #     subject += noun + ' '
    #
    # data =  wikipedia.summary(subject, sentences=1)
    # re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>", data)
    # return data



def process(request, s):
    tasks = ['temperature', 'time', 'convert', 'score', 'alarm', 'open', 'navigate', 'news']
    small_talk_tags = ['you', 'your']

    tokens = word_tokenize(s)
    tags = nltk.pos_tag(tokens)

    nouns = []
    adjectives = []
    verbs = []
    numbers = []

    response = {}
    response['code'] = 100

    if s == "hi" or s == "hello":
        return HttpResponse(s)

    for tag in tags:
        if tag[1] == 'NN' or tag[1] == 'NNS' or tag[1] == 'NNP':
            nouns.append(tag[0])

        if tag[1] == 'JJ':
            adjectives.append(tag[0])

        if tag[1] == 'VB':
            verbs.append(tag[0])

        if tag[1] == 'CD':
            numbers.append(tag[0])

    w = (nltk.ne_chunk(tags))

    for pronoun in small_talk_tags:
        for tag in tags:
            if tag[1] == 'PRP' or tag[1] == 'PRP$':
                response['data'] = small_talk(s, tag[0], nouns, adjectives, verbs)
                return JsonResponse(response)

    match = ""
    for word in str(s).split():
        for task in tasks:
            if word == task:
                match = task

    if match == "":
        for word in str(s).split():
            match = find_match(word)
            if match != "":
                break


    if match == 'temperature':
        chunkGram1 = r"""Chunk: {<.>*<NN><IN><NNP>+}"""
        chunkGram2 = r"""Chunk: {<.>*<JJ.*><IN><NNP>+}"""

        if verify(chunkGram1, tags) or verify(chunkGram2, tags):
            response['data'] = get_temp(w)
            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            response['data'] = no_match(s)
            response['code'] = 101
            return JsonResponse(response)

    if match == 'convert':
        response['data'] = convert(s)
        return JsonResponse(response)

    if match == 'time':
        response['data'] = get_time(s, w)
        return JsonResponse(response)

    if match == 'score':
        response['data'] = get_score(s)
        return JsonResponse(response)

    if match == 'alarm':
        chunkGram = r"""Chunk: {<VB.*><DT.?>*<NN>}"""

        try:
            tmp = numbers[0].partition(":")
            hours = int(tmp[0])
            mins = int(tmp[-1])
        except:
            hours = int(numbers[0])
            mins = 0

        pmflag = False
        for noun in nouns:
            if noun == 'p.m' or noun == 'P.M':
                hours += 12
                pmflag = True

        if verify(chunkGram, tags):
            response['data'] = 'ALARM'
            response['hours'] = hours
            response['mins'] = mins
            response['flag'] = pmflag


        return JsonResponse(response)

    if match == 'open':
        s = s.replace('open', '')
        s = s.replace('launch', '')
        s = s.replace('start', '')
        response['data'] = s
        response['code'] = '102'

        return JsonResponse(response)

    if match == 'navigate':
        location = ''
        grammar = r"""Chunk: {<VB.*><NN.*>+}"""
        tokens = word_tokenize(s)
        tags = nltk.pos_tag(tokens)
        w = nltk.ne_chunk(tags)

        location = ''
        for t in w.subtrees():
            if t.label() == 'PERSON' or t.label() == 'ORGANIZATION':
                for leaf in t.leaves():
                    location += str(leaf[0]) + " "

        response['data'] = location
        response['code'] = 103
        return JsonResponse(response)

    if match == 'news':
        response = {}
        titles = []
        links = []
        d = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml')

        newscount = 0
        for item in d['items']:
            response.update({item['title']: item['link']})
            newscount += 1
            if newscount > 4:
                break


        response['code'] = 104
        response['data'] = 'Here are some of the latest headlines'
        return JsonResponse(response)

    #No match found open browser in app
    if match == "":
        response['data'] = no_match(s, nouns)
        response['code'] = 101

        return JsonResponse(response)


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

def index(test):
    r = requests.get('http://httpbin.org/status/418')
    print(r.text)
    return HttpResponse('<pre>' + r.text + '</pre>')

