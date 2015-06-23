#-*- encoding: utf-8 -*-

import socket, time, string, threading, signal, sys, os

from time import sleep
from collections import deque

# Librerias de mi autoria, permiten manejar mensajes y realizar acciones en Google Docs respectivamente
from handler import FEAHandler
from google import Google

class FEABot():
    # Metodo constructor, seteos basicos necesarios de configuracion, instancia objetos utiles
    def __init__(self, server, port, nick, password, channel_key, permissions_key, orders_csv, help_html, gmail_user, gmail_password):
        # Se guardan los datos de configuracion en variables de instancia
        self.server = server
        self.port = port
        self.nick = nick
        self.password = password

        self.help_html = help_html

        # Objeto encargado de conectar con Google, se incumple POO estricto a fines de encapsular de forma severa
        self.google = Google(channel_key, permissions_key, orders_csv, gmail_user, gmail_password)

        self.channels = self.google.get_channels(True)
        # Data format: [(#channel, password)]
        self.permissions = self.google.get_permissions(True)
        # Data format: {'~': [], '&': [], '@': [], '%': [], '+': []}
        self.orders = self.google.get_orders(True)
        # Data format: {'region_name': {'id': 123, 'd1': 'prioridad', 'd2': 'prioridad', 'd3': 'prioridad', 'd4': 'prioridad', 'side': 'Rumania'}}
        self.channels_events = self.google.get_channels_evento()
        # Data format: ['#canal1', '#canal2']
        self.ingame_mu = ['2206', '2496', '2401', '2807', '1845', '665', '371', '255', '561', '4396', '4298', '398', '2105', '229', '261', '1011', '1550', '414', '3043', '2564', '2552', '4502', '1310', '542', '3199']
        # Data format: ['2206', '229']

        # Bandera de conexion, utilizada en thread principal iniciador para re-conectar
        self.running = False
        # Bandera de re-conexion, utilizada en thread principal iniciador para evitar re-conexion
        self.dont_reconnect = False

        # Diccionario utilizado para interpretar los codigos numericos de respuesta de IRC
        self.sym_to_num = {
            "RPL_WELCOME": '001',
            "RPL_YOURHOST": '002',
            "RPL_CREATED": '003',
            "RPL_MYINFO": '004',
            "RPL_ISUPPORT": '005',
            "RPL_BOUNCE": '010',
            "RPL_USERHOST": '302',
            "RPL_ISON": '303',
            "RPL_AWAY": '301',
            "RPL_UNAWAY": '305',
            "RPL_NOWAWAY": '306',
            "RPL_WHOISUSER": '311',
            "RPL_WHOISSERVER": '312',
            "RPL_WHOISOPERATOR": '313',
            "RPL_WHOISIDLE": '317',
            "RPL_ENDOFWHOIS": '318',
            "RPL_WHOISCHANNELS": '319',
            "RPL_WHOWASUSER": '314',
            "RPL_ENDOFWHOWAS": '369',
            "RPL_LISTSTART": '321',
            "RPL_LIST": '322',
            "RPL_LISTEND": '323',
            "RPL_UNIQOPIS": '325',
            "RPL_CHANNELMODEIS": '324',
            "RPL_NOTOPIC": '331',
            "RPL_TOPIC": '332',
            "RPL_INVITING": '341',
            "RPL_SUMMONING": '342',
            "RPL_INVITELIST": '346',
            "RPL_ENDOFINVITELIST": '347',
            "RPL_EXCEPTLIST": '348',
            "RPL_ENDOFEXCEPTLIST": '349',
            "RPL_VERSION": '351',
            "RPL_WHOREPLY": '352',
            "RPL_ENDOFWHO": '315',
            "RPL_NAMREPLY": '353',
            "RPL_ENDOFNAMES": '366',
            "RPL_LINKS": '364',
            "RPL_ENDOFLINKS": '365',
            "RPL_BANLIST": '367',
            "RPL_ENDOFBANLIST": '368',
            "RPL_INFO": '371',
            "RPL_ENDOFINFO": '374',
            "RPL_MOTDSTART": '375',
            "RPL_MOTD": '372',
            "RPL_ENDOFMOTD": '376',
            "RPL_YOUREOPER": '381',
            "RPL_REHASHING": '382',
            "RPL_YOURESERVICE": '383',
            "RPL_TIME": '391',
            "RPL_USERSSTART": '392',
            "RPL_USERS": '393',
            "RPL_ENDOFUSERS": '394',
            "RPL_NOUSERS": '395',
            "RPL_TRACELINK": '200',
            "RPL_TRACECONNECTING": '201',
            "RPL_TRACEHANDSHAKE": '202',
            "RPL_TRACEUNKNOWN": '203',
            "RPL_TRACEOPERATOR": '204',
            "RPL_TRACEUSER": '205',
            "RPL_TRACESERVER": '206',
            "RPL_TRACESERVICE": '207',
            "RPL_TRACENEWTYPE": '208',
            "RPL_TRACECLASS": '209',
            "RPL_TRACERECONNECT": '210',
            "RPL_TRACELOG": '261',
            "RPL_TRACEEND": '262',
            "RPL_STATSLINKINFO": '211',
            "RPL_STATSCOMMANDS": '212',
            "RPL_ENDOFSTATS": '219',
            "RPL_STATSUPTIME": '242',
            "RPL_STATSOLINE": '243',
            "RPL_UMODEIS": '221',
            "RPL_SERVLIST": '234',
            "RPL_SERVLISTEND": '235',
            "RPL_LUSERCLIENT": '251',
            "RPL_LUSEROP": '252',
            "RPL_LUSERUNKNOWN": '253',
            "RPL_LUSERCHANNELS": '254',
            "RPL_LUSERME": '255',
            "RPL_ADMINME": '256',
            "RPL_ADMINLOC": '257',
            "RPL_ADMINLOC": '258',
            "RPL_ADMINEMAIL": '259',
            "RPL_TRYAGAIN": '263',
            "ERR_NOSUCHNICK": '401',
            "ERR_NOSUCHSERVER": '402',
            "ERR_NOSUCHCHANNEL": '403',
            "ERR_CANNOTSENDTOCHAN": '404',
            "ERR_TOOMANYCHANNELS": '405',
            "ERR_WASNOSUCHNICK": '406',
            "ERR_TOOMANYTARGETS": '407',
            "ERR_NOSUCHSERVICE": '408',
            "ERR_NOORIGIN": '409',
            "ERR_NORECIPIENT": '411',
            "ERR_NOTEXTTOSEND": '412',
            "ERR_NOTOPLEVEL": '413',
            "ERR_WILDTOPLEVEL": '414',
            "ERR_BADMASK": '415',
            "ERR_UNKNOWNCOMMAND": '421',
            "ERR_NOMOTD": '422',
            "ERR_NOADMININFO": '423',
            "ERR_FILEERROR": '424',
            "ERR_NONICKNAMEGIVEN": '431',
            "ERR_ERRONEUSNICKNAME": '432',
            "ERR_NICKNAMEINUSE": '433',
            "ERR_NICKCOLLISION": '436',
            "ERR_UNAVAILRESOURCE": '437',
            "ERR_USERNOTINCHANNEL": '441',
            "ERR_NOTONCHANNEL": '442',
            "ERR_USERONCHANNEL": '443',
            "ERR_NOLOGIN": '444',
            "ERR_SUMMONDISABLED": '445',
            "ERR_USERSDISABLED": '446',
            "ERR_NOTREGISTERED": '451',
            "ERR_NEEDMOREPARAMS": '461',
            "ERR_ALREADYREGISTRED": '462',
            "ERR_NOPERMFORHOST": '463',
            "ERR_PASSWDMISMATCH": '464',
            "ERR_YOUREBANNEDCREEP": '465',
            "ERR_YOUWILLBEBANNED": '466',
            "ERR_KEYSET": '467',
            "ERR_CHANNELISFULL": '471',
            "ERR_UNKNOWNMODE": '472',
            "ERR_INVITEONLYCHAN": '473',
            "ERR_BANNEDFROMCHAN": '474',
            "ERR_BADCHANNELKEY": '475',
            "ERR_BADCHANMASK": '476',
            "ERR_NOCHANMODES": '477',
            "ERR_BANLISTFULL": '478',
            "ERR_NOPRIVILEGES": '481',
            "ERR_CHANOPRIVSNEEDED": '482',
            "ERR_CANTKILLSERVER": '483',
            "ERR_RESTRICTED": '484',
            "ERR_UNIQOPPRIVSNEEDED": '485',
            "ERR_NOOPERHOST": '491',
            "ERR_NOSERVICEHOST": '492',
            "ERR_UMODEUNKNOWNFLAG": '501',
            "ERR_USERSDONTMATCH": '502',
            "NOTICE": 'NOTICE',
        }

        # Diccionario de codigos de IRC invertido ¿Innecesario? proximamente sera removido
        self.num_to_sym = {}
        for k, v in self.sym_to_num.items():
            self.num_to_sym[v] = k
    
    # Metodo de conexion, crea el socket, instancia el handler de mensajes y los threads de envio/recepcion
    def connect(self):
        # Se crea socket de conexion
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server, self.port))

        # Bandera de conexion, utilizada en thread principal iniciador para re-conectar
        self.running = True

        # Cola de mensajes tipo FIFO
        self.queue = deque([])
        self.data = {}
        # Data format: {'#channel_name': {'joined': True, 'users': [], '~': [], '&': [], '@': [], '%': [], '+': []}}
        
        self.identified = {}
        # Data format: {'XXCiro': 1, 'pab_mac': 3}

        # Objeto encargado de manejar los mensajes '.<comando> [opciones]', se ignora POO estricto a fines de encapsulacion severa
        self.handler = FEAHandler(self)

        # Thread de recepcion, permite paralelizar envios/recepciones con demas procesos
        self.inputThread = threading.Thread(target=self.processInput)
        # Threads como demonio, morira cuando muera el thread original
        self.inputThread.daemon = True
        # Se dispara
        self.inputThread.start()

        # Thread de envio, permite paralelizar envios/recepciones con demas procesos
        self.outputThread = threading.Thread(target=self.processOutput)
        # Threads como demonio, morira cuando muera el thread original
        self.outputThread.daemon = True
        # Se dispara
        self.outputThread.start()

        # Se añaden mensajes de identificacion a la cola de mensajes
        self.queue_append('NICK %s' % self.nick)
        self.queue_append('USER %s %s %s : %s' % (self.nick, self.nick, self.nick, self.nick))
        
        # Se para acá hasta que muera el thread de salida, cuando esto termine se retomara el thread original de forma externa, permitiendo entrar al bucle de reconexion
        self.outputThread.join()

    # Metodo de desconexion, solo llamado de forma externa via una señal de sistema (ctrl + c)
    def disconnect(self, signum, frame):
        # Bandera para evitar reconexion
        self.dont_reconnect = True
        # Muere thread principal, mueren hijos demonios \o/
        exit(0)

    # Metodo de entrada, solo llamado como metodo del thread de entrada
    def processInput(self):
        # Mientras se este conectado
        while self.running:
            # Se lee un segmento del socket
            readbuffer = self.socket.recv(4096)
            try:
                # Separamos segmento leido en lineas "humanas"
                lines = str(readbuffer).split('\n')

                # Se procesa cada linea
                for line in lines:
                    # Si la linea tiene longitud aceptable y no es un mero salto de linea o similar
                    if(len(line.strip()) > 0):
                        # DEBUG: Mostramos la linea en la consola
                        # print(line)
                        # Interpretamos linea
                        try:
                            prefix = ''
                            trailing = []
                        
                            if(line[0] == ':'):
                                prefix, line = line[1:].split(' ', 1)
                        
                            if(line.find(' :') != -1):
                                line, trailing = line.split(' :', 1)
                                params = line.split()
                                params.append(trailing)
                            else:
                                params = line.split()
                        
                            command = params.pop(0).upper()
                        
                            if(command in self.num_to_sym):
                                command = self.num_to_sym[command]
                            
                            # Se busca el metodo de acuerdo al codigo de IRC del mensaje
                            method = getattr(self, 'RESPONSE_%s' % command, None)
                            
                            # Si se encontro un metodo implementado, se invoca en un hilo nuevo y se procede con los demas mensajes
                            # sino, se envia al manejador de codigos desconocidos donde es ignorado ¿Innecesario?
                            if(method is not None):
                                # DEBUG: 
                                th = threading.Thread(target=method, args=(prefix, params))
                                # DEBUG: 
                                th.daemon = True
                                # DEBUG: 
                                th.start()
                            else:
                                self.RESPONSE_UNKNOWN(prefix, command, params)
                        except:
                            # Si hubo una excepcion cuando se interpretaba la linea, entonces la misma esta corrupta
                            # Puede ser porque el segmento corto la linea a la mitad, lo ignoramos. ¿Solucion real?
                            # DEBUG: print("Bad line, ignore it")
                            print(sys.exc_info())
                            pass
            except:
                # Se ignoran errores extras no manejados
                print(sys.exc_info())
                pass

            # Util para bajar el nivel del CPU del 99% al ~1%
            time.sleep(0.2)
        
    # Metodo de salida, solo llamado como metodo del thread de salida
    def processOutput(self):
        # Se implementa un mini-control de flood, solo se envian mensajes cada 0.7 segundos
        flood = 0

        # Mientras se este conectado
        while self.running:
            if(len(self.queue) > 0):
                if(flood <= (time.time() - 0.7)):
                    flood = time.time()

                    # Enviar mensaje y retirarlo de la lista
                    out = self.queue.popleft()
                    try:
                        self.socket.send(out)
                    except UnicodeEncodeError:
                        pass
                    
                    # DEBUG: Mostramos la linea en la consola
                    # print(out)

            # Si murio el thread de entrada se corta este metodo, matando consecuentemente el thread invocador
            if(self.inputThread.is_alive() == False):
                # DEBUG: 
                # print('inputThread not alive.\n')
                break

            # Util para bajar el nivel del CPU del 99% al ~1%
            time.sleep(0.2)

    # Metodo manejador de mensajes tipo PING, solo llamado desde processInput
    # Se debe responder con el correspondiente PONG para evitar desconexion desde el servidor
    def RESPONSE_PING(self, prefix, params):
        self.queue_append('PONG :%s' % params[-1])

    # Metodo manejador de mensajes tipo RPL_NAMREPLY, solo llamado desde processInput
    # Se recibe luego de conectarse a un canal, es la lista de los nicks unidos al mismo
    def RESPONSE_RPL_NAMREPLY(self, prefix, params):
        # Se almacenan los datos del canal, especificamente los usuarios y sus niveles de acceso
        users = params[3].strip('\r\n').split(' ')
        channel = params[2].strip('\r\n').lower()

        self.data[channel]['users'] = [x.translate(None, '~&@%+') for x in users]
        
        for level in ['~', '&', '@', '%', '+']:
            self.data[channel][level] = [u[1:] for u in users if(u[0] == level)]

    # Metodo manejador de mensajes tipo RPL_WELCOME, solo llamado desde processInput
    # Se recibe luego de entrar al servidor de IRC, luego se envian datos de identificacion
    # Implementado aqui para asegurar identificacion en tiempo correcto
    def RESPONSE_RPL_WELCOME(self, prefix, params):
        # Enviamos mensaje de identificacion al servicio de NickServ
        self.queue_append('PRIVMSG NickServ :IDENTIFY %s\n' % self.password)

        # Añadimos a la cola de mensajes para entrar a todos los canales del bot
        for channel in self.channels:
            if(channel[1] is None):
                self.queue_append('JOIN %s' % channel[0])
            else:
                self.queue_append('JOIN %s %s' % (channel[0], channel[1]))

    # Metodo manejador de mensajes tipo JOIN, solo llamado desde processInput
    # Se recibe cuando o bien el bot entra a un canal o un nick entra al canal donde esta el bot
    def RESPONSE_JOIN(self, prefix, params):
        # Un nick entro a un canal, o el mismo bot lo hizo

        user = prefix[0:prefix.index('!')]
        channel = params[0].strip('\r\n').lower()

        if(user == self.nick):
            # Bandera interna del canal, ¿En desuso?
            self.data[channel] = {'joined': True}
        else:
            # Se agrega nick a la lista de usuarios del canal, si tiene algun tipo de nivel de acceso el mismo se indicara mediante otro mensaje tipo MODE desde el servidor por lo que nada se hace aqui
            self.data[channel]['users'].append(user)



    # Metodo manejador de mensajes tipo MODE, solo llamado desde processInput
    # Se recibe cuando hay un cambio de modo en algun canal
    def RESPONSE_MODE(self, prefix, params):
        # {'q':'~', 'a':'&', 'o':'@', 'h':'%', 'v':'+'}
        # Ocurrio un cambio de modo a cierto nick, se actualizan las listas de accesos del nick en canal correspondiente
        if(params[0] != self.nick):
            channel = params[0].lower()
            user = params[2]

            for level in ['q', 'a', 'o', 'h', 'v']:
                if(params[1][1] == level):
                    # Transformamos el char a su correspondencia en los indices usados, ya que difieren del estandar (Podria cambiarse, pero tiene muchas referencias fijas)
                    level = level.translate(string.maketrans('qaohv', '~&@%+'))

                    # Si se agrega el modo, se agrega a la lista, sino, se lo elimina de ella
                    try:
                        if(params[1][0] == '+'):
                            self.data[channel][level].append(user)
                        else:
                            self.data[channel][level].remove(user)
                        break
                    except:
                        pass

    # Metodo manejador de mensajes tipo PART, solo llamado desde processInput
    # Se recibe cuando un nick sale de un canal donde esta el bot
    def RESPONSE_PART(self, prefix, params):
        # Un nick salio del canal, por lo que se eliminan todas sus referencias en los datos del correspondiente canal
        user = prefix[0:prefix.index('!')]
        channel = params[0].lower()

        self.data[channel]['users'].remove(user)

        for level in ['~', '&', '@', '%', '+']:
            try:
                self.data[channel][level].remove(user)
            except:
                pass

    # Metodo manejador de mensajes tipo QUIT, solo llamado desde processInput
    # Se recibe cuando un nick se desconecta del servidor y este esta en un mismo canal que el bot
    def RESPONSE_QUIT(self, prefix, params):
        # Un nick se desconecto, por lo que se eliminan todas sus referencias en los datos de canales
        user = prefix[0:prefix.index('!')]

        for channel in self.data:
            try:
                self.data[channel]['users'].remove(user)

                for level in ['~', '&', '@', '%', '+']:
                    try:
                        self.data[channel][level].remove(user)
                    except:
                        pass
            except:
                pass

    # Metodo manejador de mensajes tipo NICK, solo llamado desde processInput
    # Se recibe cuando hay un cambio de nick de alguien que comparte canal con el bot
    def RESPONSE_NICK(self, prefix, params):
        # Hubo un cambio de nick, se actualizan todas las referencias del nick viejo al nick nuevo
        nick_old = prefix[0:prefix.index('!')]
        nick_new = params[0].strip('\r\n')

        for channel in self.data:
            try:
                self.data[channel]['users'].remove(nick_old)
                self.data[channel]['users'].append(nick_new)

                for level in ['~', '&', '@', '%', '+']:
                    try:
                        self.data[channel][level].remove(nick_old)
                        self.data[channel][level].append(nick_new)
                    except:
                        pass
            except:
                pass

    # Metodo manejador de mensajes tipo KICK, solo llamado desde processInput
    # Se recibe cuando un nick es echado del mismo canal que el bot o bien cuando echan al bot del canal
    def RESPONSE_KICK(self, prefix, params):
        # Si se echa al mismo bot, entonces se borran datos del canal para ahorrar memoria
        # sino, se quita al usuario echado de la informacion del canal y de cualquier lista de acceso que integrase
        if(params[1] == self.nick):
            channel = params[0].strip('\r\n').lower()

            self.data.pop(channel, None)
        else:
            channel = params[0].lower()
            user = params[1]

            self.data[channel]['users'].remove(user)

            for level in ['~', '&', '@', '%', '+']:
                try:
                    self.data[channel][level].remove(user)
                except:
                    pass

    # Metodo manejador de mensajes tipo PRIVMSG, solo llamado desde processInput
    # Se recibe cuando llega un mensaje normal a un canal donde esta el bot, o bien por query al mismo
    def RESPONSE_PRIVMSG(self, prefix, params):
        # Prefix: XXCiro!XXCiro@Dura.Lex.Sed.Lex
        # Params: ['LeBot', '.sarasa\r']
        # 		  ['#FEA', '.sarasa\r']

        # Si el cuerpo del mensaje inicia con un punto es un comando del bot
        if(params[1][0] == '!'):
            command = params[1].strip('\r\n')[1:]

            if(command.find(' ') > 0):
                command = command[0:command.index(' ')]

            params[1] = params[1][1 + len(command):].lstrip(' ')

            # Se presume mensaje no privado a menos que se demuestre lo contrario
            is_pm = False

            if(params[0] == self.nick):
                is_pm = True

            # Se busca un manejador para el comando dentro del objeto Handler()
            method = getattr(self.handler, 'HANDLE_%s' % command.upper(), None)
        
            # Si el metodo esta implementado se lo llama, si ocurre un error al ejecutarlo se envia un mensaje notificando el error de ejecucion
            if(method is not None):
                sender = prefix[0:prefix.index('!')]

                try:
                    method(sender, params, is_pm)
                except:
                    # DEBUG: Mostramos en consola errores para debuguear ¡Nunca en produccion!
                    print(sys.exc_info())
                    raise

                    # Se envia por PM o al canal segun sea un comando enviado por query o no
                    if(is_pm):
                        self.queue_append('PRIVMSG %s :%s' % (sender, 'Error al ejecutar el comando.'))
                    else:
                        self.queue_append('PRIVMSG %s :%s' % (params[0], 'Error al ejecutar el comando.'))
        else:
            # Mensaje normal, se ignora
            pass

    # Metodo manejador de mensajes tipo ERROR, solo llamado desde processInput
    # Llega cuando ocurre un error, como por ejemplo, reconectarse demasiado rapido
    def RESPONSE_ERROR(self, prefix, params):
        if(params[0].strip('\r') == 'Trying to reconnect too fast.'):
            # DEBUG: print('Waiting...')
            time.sleep(10)

        # Se coloca la bandera en falsa para forzar una desconexion, luego se reconectara debido al bucle externo del thread principal
        self.running = False

    # Metodo manejador de mensajes tipo NOTICE, solo llamado desde processInput
    # Llega para comunicar entre el servidor y el cliente de IRC
    def RESPONSE_NOTICE(self, prefix, params):
        # Prefix: NickServ!service@rizon.net
        # Params: ['LeBot', 'STATUS XXCiro|BNC 3\r']
        if(len(params) == 2):
            parts = params[1].strip('\r\n').split(' ')
            if(parts[0] == 'STATUS'):
                self.identified[parts[1]] = parts[2]


    # Metodo manejador de mensajes tipo UNKNOWN, solo llamado desde processInput
    # Llega cuando no existe un metodo correcto implementado para resolver el codigo de algun mensaje de IRC
    def RESPONSE_UNKNOWN(self, prefix, command, params):
        pass

    # Metodo para codificar un string unicode como cadena bytestring de charset UTF-8
    def encode(self, text):
        return text

    # ---------------------------------------------------------------------------------- #
    # @ PUBLIC METHODS                                                                   #
    # ---------------------------------------------------------------------------------- #

    # Agregar mensaje a la lista de envio, mensajes tipo materia prima respetando el estandar de IRC
    def queue_append(self, *messages):
        for msg in messages:
            msg = '%s\r\n' % msg.strip('\r\n')
            self.queue.append(self.encode(msg))

    # Recargar permisos desde la hoja de calculo correspondiente
    def refresh_permission(self):
        self.permissions = self.google.get_permissions(True)

    # Recargar ordenes desde la hoja de calculo correspondiente
    def refresh_orders(self):
        self.orders = self.google.get_orders(True)

    # Subir permisos a la hoja de calculo correspondiente
    def update_permission(self):
        self.google.set_permissions(self.permissions)

    # Subir canales a la hoja de calculo correspondiente
    def update_channels(self):
        self.google.set_channels(self.channels)

    # Subir canales a la hoja de calculo correspondiente
    def update_channels_events(self):
        self.google.set_channels_events(self.channels_events)

    # Agregar canal a la lista de canales temporales, se perdera si no se sube a la hoja de calculo
    def add_channel(self, channel, password=''):
        self.channels.append((channel, password))

    # Agregar canal a la lista de canales temporales, se perdera si no se sube a la hoja de calculo
    def add_channel_event(self, channel):
        self.channels_events.append(channel)

    # Agregar nick a la lista del diccionario de permisos temporales, se perdera si no se sube a la hoja de calculo
    def add_permission(self, nick, permission):
        self.permissions[permission].append(nick)

    # Eliminar nick de la lista del diccionario de permisos temporales, se perdera si no se sube a la hoja de calculo
    def del_permission(self, nick, permission):
        self.permissions[permission].remove(nick)

    # Eliminar canal de la lista de canales temporales, se perdera si no se sube a la hoja de calculo
    def del_channel(self, channel):
        for ch in self.channels:
            if ch[0] == channel:
                self.channels.remove(ch)
                break

    # Eliminar canal de la lista de canales temporales para evento, se perdera si no se sube a la hoja de calculo
    def del_channel_event(self, channel):
        for ch in self.channels_events:
            if ch.lower() == channel.lower():
                self.channels_events.remove(ch)
                break

    # Verificar si cierto nick tiene el nivel especificado o superior en el canal indicado
    def has_level(self, channel, nick, level):
        perm_to_level = {'~': 5, '&': 4, '@': 3, '%': 2, '+': 1}

        for n in ['~', '&', '@', '%', '+']:
            if nick in self.data[channel.lower()][n]:
                if(perm_to_level[n] >= perm_to_level[level]):
                    return True

        return False

    # Verificar si cierto nick tiene cierto permiso o superior
    def has_permission(self, nick, permission):
        self.queue_append('PRIVMSG NickServ :STATUS %s\n' % nick)

        while nick not in list(self.identified.keys()):
            # Util para bajar el nivel del CPU del 99% al ~1%
            time.sleep(0.2)

        if self.identified[nick] != '3':
            del self.identified[nick]
            return False

        del self.identified[nick]

        perm_to_level = {'~': 5, '&': 4, '@': 3, '%': 2, '+': 1}

        for n in self.permissions:
            if nick in self.permissions[n]:
                if(perm_to_level[n] >= perm_to_level[permission]):
                    return True

        return False

# Funcion inicializadora
def main():
    config = {'server': 'irc.rizon.net',
              'port': 6667, 
              'nick': 'BotName', 
              'password': 'BotPassword',
              'channel_key': '1UOQ2z3KP3AyCyiD4Uefy5quJvrM0sw9uU2wZhE5pafE',
              'permissions_key': '1UOQ2z3KP3AyCyiD4Uefy5quJvrM0sw9uU2wZhE5pafE',
              'orders_csv': 'https://docs.google.com/spreadsheet/pub?key=0Ao9AwgenLRqIdDNCWGVGa3pZakNSNjRqWUhoNlk2SFE&output=csv',
              'help_html': 'http://bit.ly/1k7Fc0d',
              'gmail_user': 'gmailUsername@gmail.com',
              'gmail_password': 'gmailPassword'}

    # Instanciar con la configuracion, se expande el diccionario con el doble asterisco
    c = FEABot(**config)

    # Manejamos la señal de 'ctrl + c' invocando el metodo disconnect para cerrar todo de forma limpia
    signal.signal(signal.SIGINT, c.disconnect)

    # Si no esta corriendo lo re-conectamos a menos que la bandera de reconexion indique lo contrario
    while True:
        if(c.dont_reconnect == True):
            break

        if(c.running == False):
            c.connect()

        # Util para bajar el nivel del CPU del 99% al ~1%
        time.sleep(0.2)

# Setear proxy en nulo, necesario en el VPS para poder resolver los DNS de forma directa
os.environ['http_proxy'] = ''

main()