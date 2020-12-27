from datetime import date
from random import random, randint, seed

import bs4
import json
import time
from vk_api import audio
import requests
from time import time
import os
import cexprtk as calculator
import vk_api
from vk_api import audio
import re   
from pymongo import MongoClient
from vk_api.longpoll import VkLongPoll, VkEventType

from dbLogger import CommandLogger

CONNECTION_PORT = 27017
TOKEN = '1432f7b6fbeaf1168c58e9afec35418b180b77a433cef4e1e5b0d298c9160ce3d1221fa8e3f0e97074c0f'

# Setup randomizer
seed(1)

# default bot state = active (unmuted)
muted = False

# Setup database 
mongoConnection = MongoClient('localhost', CONNECTION_PORT, event_listeners=[CommandLogger()])
knyazevaDatabase = mongoConnection['knyazeva']
knyazevaCollection = knyazevaDatabase['quotes']

# Setup VK connection
vk = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk)
login = '+79687308990' #your telephone number shout be put here
password = '******'  #your vk pass shout be put here
user_audio_id = ''
vk_session = vk_api.VkApi(login=login, password=password)
vk_session.auth()
vk1 = vk_session.get_api()
vk_audio = audio.VkAudio(vk_session)

def write(message, peer_id):
    vk.method('messages.send', {
        'peer_id': peer_id,
        'random_id': random(),
        'message': message
    })


def useIdGetter(url):
    return vk1.utils.resolveScreenName(screen_name=url[15:])['object_id']


def audioGetter(audio_id):                               #audio JSON parser (it searches name of track in JSON). Returns track's url
    resultUrl = {0:"Go to demons, there isn't your audio"}
    #my_id = '296839363' #id of audio-reading user
    audio1 = JSONReader()
    j = 0
    for i in audio1:
        if audio_id in i["title"]:
            resultUrl[j] = i["url"]
            j+=1

    return resultUrl

def audioJSONGetter(my_id):                                     #audio JSON getter throw user id
    #resultUrl = {0:"Go to demons, there isn't your audio"}
    #my_id = '296839363' #id of audio-reading user
    audio1 = vk_audio.get(owner_id=my_id)
    print(audio1)
    return audio1


def JSONreWriter(new_json):                                     #JSON rewriter method
    with open('audio.json', "w") as f:
        json.dump(new_json, f)

def JSONReader():                                               #JSON reader method
    with open('audio.json', 'r', encoding='utf-8') as fh:
        return json.load(fh)


# write('Князева активирована', 2000000001)
buf = False
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me and event.text[:6] == 'Князь,':
            peer_id = event.peer_id
            messageText = event.text[7:]
            if buf==False or "ASto" in messageText or "AUrl" in messageText:
                command = messageText[:4]
                buf = False
            if muted:
                if command == 'Back':
                    if muted == False:
                        write('Не поняла? Я тут, ты чего хочешь? Домашку сдать по геометрии? Ну так сдавай', peer_id)
                    else:
                        muted = False
                        write('Княжий балдеж закончился, сдаем дз по геометрии', peer_id)
            else:
                #Audio commands:
                if buf == True:                                 #giving new audio-link as answer to name of track 
                    result = audioGetter(messageText)
                    buf = True
                    print(result)
                    for i in result.values():
                        write(i, peer_id)
                if command == 'ASto':                           #stop
                    write('Knyazz DJ has been turned off', peer_id)
                    command = ''
                if command == 'ASta':                           #start
                    user_audio_id = peer_id
                    JSONreWriter(audioJSONGetter(user_audio_id))
                    buf = True
                    command = ''
                    write('Ready for sending some audio-files. Please, send their names to me', peer_id)
                if command == 'AUrl':
                    print(command)
                    messageText = messageText[5:]
                    print(messageText)
                    user_audio_id = useIdGetter(messageText)    #Rewriting throw other user's url
                    JSONreWriter(audioJSONGetter(user_audio_id))
                    buf = True
                    write('Author setting accomplished', peer_id)
                    command = ''
                #Help command:
                if command == 'Help':
                    write("Тут обитает супер крутой бот - Елена Князь. Пока у нее доступны следующие команды: (Любую "
                          "команду нужно начинать с 'Князь, '. Собственно, команды: Help. Князь покажет напишет это "
                          "сообщение\nCalc (выражение). Елена Князь "
                          "посчитает за вас математическое выражение.\nStfu. Князь перестанет отвечать на ваши "
                          "сообщения, пока ей не напишут Back\nAddQ авторЦитаты&Цитата\nGetQ Автор&ИмяАвтора или "
                          "Цитата&СодержаниеЦитаты или Год&ГодЦитаты\nНапример,\nAddQ ЕЮ&Блямкает\nGetQ "
                          "Автор&ЕЮ\nGetQ Цитата&Блямкает\nGetQ Год&2020", peer_id)
                #Quote commands:
                elif command == 'AddQ':
                    splitQuote = messageText[4:].lstrip().split('&', 1)
                    knyazevaCollection.insert_one({'author': splitQuote[0].lstrip(),
                                                   'quote': splitQuote[1][4:].lstrip(),
                                                   'date': date.today().strftime('%Y')
                                                   })
                    write("Хватит блямкать и сбивать меня, сейчас я всё сохраню", peer_id)

                elif command == 'GetQ':
                    splitQuote = messageText[4:].lstrip().split('&', 1)
                    searchType = splitQuote[0]
                    searchField = 'no'
                    if searchType == 'Автор':
                        searchField = 'author'
                    elif searchType == 'Год':
                        searchField = 'date'
                    elif searchType == 'Цитата':
                        searchField = 'quote'
                    else:
                        write('Ты сам понял что сказал?', peer_id)
                    if searchField != 'no':
                        searchPattern = re.compile(splitQuote[1][4:].lstrip(), re.I)
                        if knyazevaCollection.count_documents({searchField: {'$regex': searchPattern}}) == 0:
                            write('Корней нет', peer_id)
                        else:
                            foundQuotes = knyazevaCollection.find({searchField: {'$regex': searchPattern}}).sort('date')
                            for doc in foundQuotes:
                                write('{author}: {quote}'.format(author=doc['author'], quote=doc['quote']), peer_id)
                elif command == 'RndQ':
                    splitQuote = messageText[4:].lstrip().split('&', 1)
                    searchType = splitQuote[0]

                    searchField = 'no'
                    if searchType == 'Автор':
                        searchField = 'author'
                    elif searchType == 'Год':
                        searchField = 'date'
                    else:
                        write('Ты сам понял что сказал?', peer_id)
                    if searchField != 'no':
                        x = knyazevaCollection.find({searchField: splitQuote[1][4:].lstrip()}).limit(-1)
                        randomQuote = x.skip(randint(0, x.count() - 1)).next()
                        write('{author}: {quote}'.format(author=randomQuote['author'], quote=randomQuote['quote']),
                              peer_id)
                
                #Calculating commands:
                elif command == 'Stfu':
                    muted = True
                    write('У меня Княжий Балдеж, оставляю вас в покое', peer_id)
                elif command == 'куку':
                    write('Ку!', peer_id)
                elif command == 'Calc':
                    try:
                        mathResult = calculator.evaluate_expression(
                            ' ' + messageText[4:].replace('pi', '3.14159').lstrip(), {})
                    except:
                        mathResult = 'Ты хоть условие перепиши нормально, я ничего не поняла из того, что ты написал'
                    write(mathResult, peer_id)
                else:
                    write('Ты сам понял что сказал?', peer_id)
