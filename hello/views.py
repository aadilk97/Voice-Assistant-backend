from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Greeting

import json
import pyowm
import nltk
from nltk import word_tokenize
from bs4 import BeautifulSoup

import requests
import random

# Create your views here.

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
    return ("It is " +  str(w.get_temperature('celsius')['temp']) +  " degrees in " + loc)

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
            soup = soup.find(id="search")
            r = soup.find(text=lambda text: text and "=" in text)
            return r
        except:
            print("Nothing found")

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


def process(request, s):
    tasks = ['temperature', 'time', 'convert', 'score']
    small_talk_tags = ['you', 'your']

    tokens = word_tokenize(s)
    tags = nltk.pos_tag(tokens)

    nouns = []
    adjectives = []
    verbs = []

    response = {}

    if s == "hi" or s == "hello":
        return HttpResponse(s)

    for tag in tags:
        if tag[1] == 'NN':
            nouns.append(tag[0])

        if tag[1] == 'JJ':
            adjectives.append(tag[0])

        if tag[1] == 'VB':
            verbs.append(tag[0])

    w = (nltk.ne_chunk(tags))

    for pronoun in small_talk_tags:
        for tag in tags:
            if tag[1] == 'PRP' or tag[1] == 'PRP$':
                response['data'] = small_talk(s, tag[0], nouns, adjectives, verbs)
                return JsonResponse(response)

    for task in tasks:
        for noun in nouns:
            if noun == task:
                match = noun

        for adjective in adjectives:
            if adjective == task:
                match = adjective

        for verb in verbs:
            if verb == task:
                match = verb


    if match == 'temperature':
        response['data'] = get_temp(w)
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    if match == 'convert':
        response['data'] = convert(s)
        return JsonResponse(response)

    if match == 'time':
        response['data'] = get_time(s, w)
        return JsonResponse(response)

    if match == 'score':
        response['data'] = get_score(s)
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

