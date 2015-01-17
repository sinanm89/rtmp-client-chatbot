# import requests
# import hashlib

# # api_key = "1095ec7d8868990d86638db92009d525"
# # api_secret = "1f575bab7ffc44ceacb2ec3c093b8400"

# # room = "rinternetfriends"
# # m = hashlib.md5()
# # auth = m.update(api_secret+":"+room+":roomlist")
# # auth=m.digest()

# # params = {
# # 	"result": "json",
# # 	"room": room,
# # 	"key":api_key,
# # 	"auth":auth
# # }
# # request = requests.get("http://tinychat.apigee.com/roominfo",params=params)


# url = "http://tinychat.com/api/find.room/roomname?site=rinternetfriends"
# req = requests.get(url)
# import ipdb
# ipdb.set_trace()

import rtmp_protocol
import httplib
from xml.dom.minidom import parseString
import thread
import time
import random
 
# Tinychat Library by MegaLoler
 
DEBUG = False
 
def httpRequest(server, resource):
        conn = httplib.HTTPConnection(server)
        conn.request("GET", resource)
        r1 = conn.getresponse()
        data1 = r1.read()
        conn.close()
        return data1
       
class TinychatMessage():
        def __init__(self, msg, nick, user=None, recipient=None, color=None):
                self.msg = msg
                self.nick = nick
                self.user = user
                self.recipient = recipient
                self.color = color
       
        def printFormatted(self):
                print(self.recipient + ": " + self.nick + ": " + self.msg)
 
class TinychatUser():
        def __init__(self, nick, id=None, color=None, lastMsg=None):
                self.nick = nick
                self.id = id
                self.color = color
                self.lastMsg = lastMsg
 
TINYCHAT_COLORS = ["#7db257", "#a78901", "#9d5bb5", "#5c1a7a", "#c53332", "#821615", "#a08f23", "#487d21", "#c356a3", "#1d82eb", "#919104", "#a990", "#b9807f", "#7bb224", "#1965b6", "#32a5d9"]
 
class TinychatRoom():
        # Manages a single room connection     
        def __init__(self):
                self.room = "sinanm89"
                self.tcUrl = self._getTcUrl()
                parts = self.tcUrl.split("/")
                server = parts[2].split(":")
                self.server = server[0]
                self.port = int(server[1])
                self.app = parts[3]
                self.url = "http://tinychat.com/sinanm89"
                self.connected = False
                self.queue = []
                self.color = TINYCHAT_COLORS[random.randint(0, len(TINYCHAT_COLORS) - 1)]
                self.nick = "GloomBot"
                self.users = {}
                self.echo = __name__ == "__main__"
                self.stack = False
 
        def connect(self):
                print 'TRYING TO CONNECT'
                self.connection = rtmp_protocol.RtmpClient(self.server, self.port, self.tcUrl, self.url, '', self.app)
                print "connected"
                print self.room
                import ipdb; ipdb.set_trace()
                self.connection.connect([self.room])
                print  "roomed"
                self.connected = True
                self._listen()
       
        def disconnect(self):
                self.connected = False
       
        def poll(self):
                q = self.queue
                self.queue = []
                return q
               
        # Commands
        def say(self, msg):
                if len(msg) > 152: return
                self._sendCommand("privmsg", [u"" + self._encodeMessage(msg), u"" + self.color + ",en"])
               
        def pm(self, msg, recipient):
                if len(msg) > 152: return
                self._sendCommand("privmsg", [u"" + self._encodeMessage("/msg " + recipient + " " + msg), u"" + self.color + ",en", u"n" + self._getUser(recipient).id + "-" + recipient])
               
        def setNick(self, nick=None):
                if not nick: nick = self.nick
                self.nick = nick
                self._sendCommand("nick", [u"" + nick])
       
        def cycleColor(self):
                try:
                        i = TINYCHAT_COLORS.index(self.color)
                except:
                        i = TINYCHAT_COLORS[random.randint(0, len(TINYCHAT_COLORS) - 1)]
                i = (i + 1) % len(TINYCHAT_COLORS)
                self.color = TINYCHAT_COLORS[i]
       
        # Events
        def onMessage(self, user, message):
                if self.echo: message.printFormatted()
       
        def onQuit(self, user):
                if self.echo: print(self.room + ": " + user.nick + " left the room.")
       
        def onJoin(self, user):
                if self.echo: print(self.room + ": " + user.nick + " entered the room.")
       
        def onRegister(self, user):
                if self.echo: print("You have connected to " + self.room + ".")
       
        def onNickChange(self, new, old, user):
                if self.echo: print(self.room + ": " + old + " changed nickname to " + new + ".")
       
        # Helper methods
        def _listen(self):
                while self.connected:
                        msg = self.connection.reader.next()
                        if DEBUG: print("SERVER: " + str(msg))
                        if msg['msg'] == rtmp_protocol.DataTypes.COMMAND:
                                pars = msg['command']
                                cmd = pars[0].encode("ascii", "ignore").lower()
                                if len(pars) > 3:
                                        pars = pars[3:]
                                else:
                                        pars = []
                                for i in range(len(pars)):
                                        if type(pars[i]) == str: pars[i] = pars[i].encode("ascii", "ignore")
                                if cmd == "privmsg":
                                        recipient = pars[0]
                                        message = pars[1]
                                        color = pars[2].lower().split(",")[0]
                                        nick = pars[3]
                                        if recipient[0] == "#":
                                                recipient = "^".join(recipient.split("^")[1:])
                                        else:
                                                recipient = "-".join(recipient.split("-")[1:])
                                        user = self._getUser(nick)
                                        message = TinychatMessage(self._decodeMessage(message), nick, user, recipient, color)
                                        user.lastMsg = message
                                        user.color = color
                                        if self.stack: self.queue.append(message)
                                        self.onMessage(user, message)
                                elif cmd == "registered":
                                        if self.nick: self.setNick()
                                        user = self._getUser(pars[0])
                                        user.id = pars[1]
                                        self.onRegister(user)
                                elif cmd == "nick":
                                        user = self._getUser(pars[0])
                                        old = user.nick
                                        user.nick = pars[1]
                                        self.onNickChange(user.nick, old, user)
                                elif cmd == "quit":
                                        user = self.users[pars[0].lower()]
                                        del self.users[pars[0].lower()]
                                        self.onQuit(user)
                                elif cmd == "join":
                                        user = self._getUser(pars[1])
                                        user.id = pars[0]
                                        self.onJoin(user)
                                elif cmd == "joins":
                                        for i in range((len(pars) - 1) / 2):
                                                user = self._getUser(pars[i*2 + 2])
                                                user.id = pars[i*2 + 1]
                                                self.onJoin(user)
                                       
        def _getUser(self, nick):
                if not nick.lower() in self.users.keys(): self.users[nick.lower()] = TinychatUser(nick)
                return self.users[nick.lower()]
   
        def _decodeMessage(self, msg):
                chars = msg.split(",")
                msg = ""
                for i in chars:
                        msg += chr(int(i))
                return msg
           
        def _encodeMessage(self, msg):
                msg2 = []
                for i in msg:
                        msg2.append(str(ord(i)))
                return ",".join(msg2)
       
        def _sendCommand(self, cmd, pars=[]):
                msg = {"msg": rtmp_protocol.DataTypes.COMMAND, "command": [u"" + cmd, 0, None] + pars}
                if DEBUG: print("CLIENT: " + str(msg))
                self.connection.writer.write(msg)
                self.connection.writer.flush()
       
        def _getTcUrl(self):   
                return parseString(httpRequest("tinychat.com", "/api/find.room/" + self.room)).getElementsByTagName("response")[0].getAttribute("rtmp")
 
if __name__ == "__main__":
        room = TinychatRoom()
        thread.start_new_thread(room.connect, ())
        while not room.connected: time.sleep(1)
        while room.connected: room.say(raw_input())


