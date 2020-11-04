import vk_api
import cexprtk as calculator
from vk_api.longpoll import VkLongPoll, VkEventType

from random import seed
from random import random


CHAT_ID = 2000000001

seed(1)

def write(message):
    vk.method('messages.send', {'peer_id' : CHAT_ID, 'random_id' : random(), 'message' : message})

token = "1432f7b6fbeaf1168c58e9afec35418b180b77a433cef4e1e5b0d298c9160ce3d1221fa8e3f0e97074c0f"

vk = vk_api.VkApi(token=token)

longpoll = VkLongPoll(vk)

muted = False

write("Князева активирована")
for event in longpoll.listen():
    if event.type == VkEventType.USER_TYPING_IN_CHAT and muted == False:
        write("Ну кто опять блямкает????")
    elif event.type == VkEventType.MESSAGE_NEW:
        if event.to_me and event.text[:6] == "Князь,":
            messageText = event.text[7:]
            command = messageText[:4]
            if muted:
                if command == "Back":
                    if False == True:
                        write("Не поняла? Я тут, ты чего хочешь? Домашку сдать по геометрии? Ну так сдавай")
                    else:
                        muted = False
                        write("Княжий балдеж закончился, сдаем дз по геометрии")
            else:
                if command == "Stfu":
                    muted = True
                    write("У меня Княжий Балдеж, оставляю вас в покое")
                elif command == "Куку":
                    write("Ку!")
                elif command == "Calc":
                    try:
                        mathResult = calculator.evaluate_expression(messageText[5:].replace("pi", "3.14159"), {})
                    except:
                        mathResult = "Ты хоть условие перепиши нормально, я ничего не поняла из того, что ты написал"
                    write(mathResult)
                else:
                    write("Ты сам понял что сказал?")