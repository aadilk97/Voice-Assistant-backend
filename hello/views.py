from django.shortcuts import render
from django.http import HttpResponse
from .models import Greeting

import pyowm
import nltk
from nltk import word_tokenize

import requests

# Create your views here.



def get_temp(w):
    loc = ""
    #return HttpResponse(w.subtrees())
    for i in w.subtrees():
        if i.label() == 'GPE':
            loc = i[0][0]

    owm = pyowm.OWM('a0fd740e29e007169ed8a60f187ef972')
    obs = owm.weather_at_place(loc)
    w = obs.get_weather()
    return ("It is ", w.get_temperature('celsius')['temp'], " degrees in", loc)



def test(request, s):
    nltk.download('tokenizer')
    tokens = word_tokenize(s)
    tags = nltk.pos_tag(tokens)

    nouns = []
    adjectives = []
    verbs = []

    for tag in tags:
        if tag[1] == 'NN':
            nouns.append(tag[0])

        if tag[1] == 'JJ':
            verbs.append(tag[0])

    w = (nltk.ne_chunk(tags))

    for noun in nouns:
        if noun == 'temperature':
            return HttpResponse(get_temp(w))

    #return HttpResponse(nouns)


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})

def index(test):
    r = requests.get('http://httpbin.org/status/418')
    print(r.text)
    return HttpResponse('<pre>' + r.text + '</pre>')

