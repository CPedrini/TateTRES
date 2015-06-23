import tornado.web
import tornado.websocket
import tornado.ioloop

import threading, time, uuid

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    pong = {'status': True, 'lastValue': '123'}
    connected = True

    def __init__(self, application, request, **kwargs):
        self.designated = {}
        # Data format: {'2206': 'random_uuid'}

        self.external_storage = kwargs['external_storage']
        self.bot = kwargs['bot']
        kwargs = {}

        tornado.web.RequestHandler.__init__(self, application, request,
                                            **kwargs)
        self.stream = request.connection.stream
        self.ws_connection = None

    def open(self):
        self.id = str(uuid.uuid4())

        self.external_storage[self.id] = {'id': self.id, 'instance': self, 'user_id': None, 'mu': None}

        th = threading.Thread(target=self.ping, args=())
        th.daemon = True
        th.start()

    def ping(self):
        try:
            while self.connected == True:
                if self.pong['status'] == False:
                    self.close()

                    break
                else:
                    self.write_message('PING:123')

                    self.pong['status'] = False
                    self.pong['lastValue'] = '123'

                    time.sleep(10)
        except:
            pass

    def on_message(self, message):
        try:
            #print('Received: %s' % message)

            parts = message.split(':', 1)

            #print(parts[0])
            #print(parts[1])

            if parts[0] == 'PONG':
                if parts[1] == self.pong['lastValue']:
                    self.pong['status'] = True
            elif parts[0] == 'NICK':
                self.external_storage[self.id]['user_id'] = parts[1]
            elif parts[0] == 'MU':
                self.external_storage[self.id]['mu'] = parts[1]

                if parts[1] not in self.bot.ingame_mu:
                    self.close()
                else:
                    if parts[1] not in self.designated:
                        self.designated[parts[1]] = self.id
            elif parts[0] == 'MESSAGE':
                mu = self.external_storage[self.id]['mu']

                if mu is not None:
                    if self.designated[mu] == self.id:
                        if parts[1][0] == '!':
                            if parts[1][1:].lower() == 'ordenes':
                                for zone in self.bot.orders:
                                    data = (zone, self.bot.orders[zone]['id'], self.bot.orders[zone]['d1'], self.bot.orders[zone]['d2'], self.bot.orders[zone]['d3'], self.bot.orders[zone]['d4'], self.bot.orders[zone]['side'])
                                    self.write_message('MESSAGE:Zona: %s || Link: http://erpk.org/b/%d || Div 1: %s || Div 2: %s || Div 3: %s || Div 4: %s || Side: %s' % data)

                                    time.sleep(1)
        except:
            pass

    def on_close(self):
        try:
            id = self.id
            mu = self.external_storage[self.id]['mu']

            del self.external_storage[self.id]

            if self.designated[mu] == id:
                del self.designated[mu]

                for x in self.external_storage:
                    if self.external_storage[x]['mu'] == mu:
                        self.designated[mu] = self.external_storage[x]['id']
                        break

            self.connected = False
        except:
            pass

class ServerSocket:
    def __init__(self, bot):
        self.bot = bot
        self.external_storage = {}
        # Data format: {'random_uuid': {'id': 'random_uuid', 'instance': WebSocketHandler(), 'user_id': '2990096', 'mu': '2206'}}

        th = threading.Thread(target=self.initialize, args=())
        th.daemon = True
        th.start()

    def initialize(self):
        application = tornado.web.Application([
            (r"/", WebSocketHandler, {'bot': self.bot, 'external_storage': self.external_storage}),
        ])

        application.listen(1989)

        tornado.ioloop.IOLoop.instance().start()

    def send(self, message):
        th = threading.Thread(target=self.th_send, args=(message,))
        th.daemon = True
        th.start()

    def th_send(self, message):
        sent_mu = []

        for x in self.external_storage:
            mu = self.external_storage[x]['mu']

            if mu in self.bot.ingame_mu:
                if mu not in sent_mu:
                    sent_mu.append(mu)
                    self.external_storage[x]['instance'].write_message('MESSAGE:%s' % message)
            else:
                self.external_storage[x]['instance'].close()
