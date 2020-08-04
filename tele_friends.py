from flask import Flask,request
import requests
import os
import re
import json
import urllib
import sys
import Queue
import threading
import time
from multiprocessing.pool import ThreadPool
reload(sys)
sys.setdefaultencoding("UTF8")

token = "" # Ganti Dengan Token bot mu
url = 'https://api.telegram.org/bot{}/'.format(token)
owner_id = "942592519" # Ganti dengan id mu
app = Flask(__name__)
user = open("user.txt").read().splitlines()
q = Queue.Queue()

chat_room = [[]]
qued = []

def checkroom(id):
    for i in chat_room:
        if id in i:
           return True
    return False

def getfid(id):
    for i in chat_room:
        if id in i:
           if i.index(id) == 0:
              return i[1]
           else:
              return i[0]

def getcroom(id):
    for i in chat_room:
        if id in i:
           return i

def sendBc(msg):
    id,msgs = msg[0],msg[1]
    requests.get(url+"sendMessage",params={"chat_id":id,"text":msgs})

antred = []
def sendMsg(msg,id):
    requests.get(url+"sendMessage",params={"chat_id":id,"text":msg})

nama_user = {}
def recvMsg(data):
  global qued,chat_room,user,antred
  try:
    asu = json.dumps(data,ensure_ascii=False)
    id = re.search('"id": (.*?),',asu).group(1).replace("}","")
    text = re.search('"text": "(.*?)",',asu).group(1).replace('\\"','"').replace("\\n","\n")
    first_name = re.search('"first_name": "(.*?)"',asu).group(1)
    if (text == "/start" or text == "/start@get_random_friends_bot") and id not in user:
       sendMsg("Welcome! find a new friends here!\n\nClick /random to find a new friends\n\nPlease share this bot,thanks :)",id)
       sendMsg("New user {}".format(first_name),owner_id)
    open("user.txt","a+").write(id+"\n") if id not in user else None
    user = open("user.txt").read().splitlines()
#    sendMsg(asu,owner_id)
    if "supergroup" in asu:
       id = "-"+re.search('"id": -(.*?),',asu).group(1).replace("}","")
       first_name = "Group Chat "+str(id)+"\nGroub = True"
       group = True
    else:
        group = False
    if text == "/random" or (text == "/random@get_random_friends_bot" and group):
       if checkroom(id):
           sendMsg("You are already in chat,please /end chat first to find a new one",id)
           return
       if group: sendMsg("Use /send (message) to send to target\n\nExample : /send hai (only for groub)",id)
       if id not in qued:
          qued.append(id)
          antred.append(id)
          nama_user[id] = first_name
          sendMsg("Searching for friends...",id)
       else:
          sendMsg("You are already in Queue,please wait for others people join",id)
          return
       if len(antred) == 2:
          chat_room.append(antred)
          [sendMsg("Teman telah ditemukan!\n\nNama : {}\n\n\nSapalah teman barumu \n\nKetik /end untuk mengahkhiri chat ini".format(nama_user[getfid(i)]),i) for i in antred]
          [qued.remove(i) for i in antred]
          for i in antred:
              del nama_user[i]
          antred = []
          return
    elif text == "/end":
       if checkroom(id):
          croom = getcroom(id)
          chat_room.remove(croom)
          [sendMsg("Chat ended :'(",fi) for fi in croom]
          return
       else:
          sendMsg("You are not in chat right now,to end a chat,please join using /random",id)
          return
    elif text == "/jumlahuser":
        sendMsg("User Amount : {}".format(len(user)),id)
        return
    elif text == "/jumlahroom":
        sendMsg("Chat room amount : {}".format(len(chat_room)),id)
        return
    elif text.startswith("/broadcast ") and id == owner_id:
        bclist = []
        for i in user:
              if [i,text.replace("/broadcast ","").replace("\\n","\n"),i] not in bclist:
                 bclist.append([i,text.replace("/broadcast ","").replace("\\n","\n"),i])
        tp = ThreadPool(45)
        tp.map(sendBc,bclist)
        sendMsg("Broadcast sent to {} users".format(len(bclist)),id)
    elif (text.startswith("/send ") and group) or checkroom(id):
        text = text.replace("/send ","") if group else text
        if text.startswith("/"):
           sendMsg("Please type a message,not a command",id)
           return
        else:
           friend_id = getfid(id)
           sendMsg(text,friend_id)
           return
    else:
        sendMsg("You are not in chat right now,please join using /random",id)
        return



  except Exception as e:
    print e
    sendMsg("Exception : {}".format(e),owner_id)

@app.route("/",methods=["POST","GET"])
def index():
    if request.method == "POST":
       recvMsg(request.get_json())
       return "Okee"
    else:
       return "Index"

if __name__ == "__main__":
   app.run(host='0.0.0.0',port=int(os.environ.get('PORT','5000')),debug=True)
