import logging
import cexprtk as calculator
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import date
from pymongo import MongoClient, monitoring
from dbLogger import CommandLogger
from random import random, randint, seed

CONNECTION_PORT = 27017
TOKEN = '1432f7b6fbeaf1168c58e9afec35418b180b77a433cef4e1e5b0d298c9160ce3d1221fa8e3f0e97074c0f'

#Setup randomizer
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

def write(message, peer_id):
    vk.method('messages.send', {
                    'peer_id' : peer_id, 
                    'random_id' : random(), 
                    'message' : message
             })

write('Князева активирована', 2000000001)
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me and event.text[:6] == 'Князь,':
            peer_id = event.peer_id
            messageText = event.text[7:]
            command = messageText[:4]
            if muted:
                if command == 'Back':
                    if muted == False:
                        write('Не поняла? Я тут, ты чего хочешь? Домашку сдать по геометрии? Ну так сдавай', peer_id)
                    else:
                        muted = False
                        write('Княжий балдеж закончился, сдаем дз по геометрии', peer_id)
            else:
                if command == 'AddQ':
                    splitQuote = messageText[4:].lstrip().split('&', 1)
                    knyazevaCollection.insert_one({ 'author' : splitQuote[0].lstrip(), 
                                                    'quote' : splitQuote[1][4:].lstrip(),
                                                    'date' : date.today().strftime('%Y')
                                                })
                
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
                        for doc in knyazevaCollection.find({searchField : splitQuote[1][4:].lstrip()}).sort('date'):
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
                        x = knyazevaCollection.find({searchField : splitQuote[1][4:].lstrip()}).limit(-1)
                        randomQuote = x.skip(randint(0, x.count() - 1)).next()
                        write('{author}: {quote}'.format(author=randomQuote['author'], quote=randomQuote['quote']), peer_id)

                elif command == 'Stfu':
                    muted = True
                    write('У меня Княжий Балдеж, оставляю вас в покое', peer_id)
                elif command == 'куку':
                    write('Ку!', peer_id)
                elif command == 'Calc':
                    try:
                        mathResult = calculator.evaluate_expression(' ' + messageText[4:].replace('pi', '3.14159').lstrip(), {})
                    except:
                        mathResult = 'Ты хоть условие перепиши нормально, я ничего не поняла из того, что ты написал'
                    write(mathResult, peer_id)
                else:
                    write('Ты сам понял что сказал?', peer_id)