import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from random import seed
from random import random

seed(1)

def write_msg(peer_id, message):
    vk.method('messages.send', {'peer_id' : peer_id, 'random_id' : random(), 'message' : message})

token = "1432f7b6fbeaf1168c58e9afec35418b180b77a433cef4e1e5b0d298c9160ce3d1221fa8e3f0e97074c0f"

vk = vk_api.VkApi(token=token)

longpoll = VkLongPoll(vk)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            if request == "Привет":
                write_msg(event.peer_id, "Ку!")
            else:
                write_msg(event.peer_id, "Ты сам понял что сказал?")