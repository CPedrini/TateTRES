#-*- encoding: utf-8 -*-

import random, time, sys

# Librerias de mi autoria, permiten respectivamente: Scrapear eRepublik, scrapear datos de RW's, scrapear eventos de eRepublik de forma automatica
from erapi import ErAPI
from watcher import Watcher
from events import Events
from serversocket import ServerSocket

class FEAHandler:
    # Metodo constructor, seteos basicos necesarios de configuracion, instancia objetos utiles
    def __init__(self, bot):
        self.bot = bot
        self.erepublik = ErAPI()
        self.watcher = Watcher()

        # Requires bot for automatic messages
        self.events = Events(bot)

        self.serversocket = ServerSocket(bot)

    # Manejador inutil, existe solo para probar paralelismo y control de errores de nivel superior al objeto
    def HANDLE_SARASA(self, sender, params, is_pm):
        # Error intensional para demostrar que ante un error imprevisto esta todo manejado y que
        #   soporta multiples comandos al mismo tiempo (ejecutar varios .sarasa para probar)
        time.sleep(10)
        raise Exception('sarasa')
        if(is_pm):
            self.bot.queue_append(*['PRIVMSG %s :%s' % (sender, 'Mensajes de a bloques 1.'), 'PRIVMSG %s :%s\n' % (sender, 'Mensaje de a bloques 2.')])
        else:
            channel = params[0]
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, 'Hola.'))

    # Manejador del MASS CALL, ilumina todos los nicks y envia mensaje
    def HANDLE_CHE(self, sender, params, is_pm):
        self.HANDLE_KUAK(sender, params, is_pm)

    # Manejador del MASS CALL, ilumina todos los nicks y envia mensaje
    def HANDLE_KUAK(self, sender, params, is_pm):
        if(is_pm == False):
            channel = params[0].lower()

            if(self.bot.has_level(channel, sender, '%') or self.bot.has_permission(sender, '%')):
                users = [self.bot.data[channel]['users'][i:i+35] for i in range(0, len(self.bot.data[channel]['users']), 35)]

                for sublist in users:
                    self.bot.queue_append('PRIVMSG %s :%s' % (channel, ' '.join(sublist)))

                self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x030,4\02¡ATENCION!\02\x03\x031,0\02 %s\x03' % params[1]))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (channel, '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador de sorteo, sortea lo que se envie por parametro al azar entre los miembros del canal, incluso el bot puede ganar ^.^
    def HANDLE_SORTEAR(self, sender, params, is_pm):
        if(is_pm == False):
            channel = params[0].lower()

            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x030,4\02¡ATENCION!\02\x03\x031,7\02 Comienza el sorteo de: %s\02\x03' % params[1]))
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x031,7\02Chan chan chan\02\x03'))

            time.sleep(1)
            
            winner = random.choice(self.bot.data[channel]['users'])

            if(winner == self.bot.nick):
                self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x030,3\02Muajaja, gane yo, denme el premio!\02\x03'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x030,3\02Felicidades %s, ganaste: %s\02\x03' % (winner, params[1])))

    # Manejador del SYNC, actualiza ordenes
    def HANDLE_SYNC(self, sender, params, is_pm):
        if(is_pm):
            if(self.bot.has_permission(sender, '%')):
                self.bot.refresh_orders()

                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Ordenes actualizadas.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
        else:
            channel = params[0]

            if(self.bot.has_permission(sender, '%')):
                self.bot.refresh_orders()
                self.bot.queue_append('PRIVMSG %s :%s' % (channel, '%s: Ordenes actualizados.' % sender))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (channel, '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del ANUNCIOKUAK, hace un KUAK y luego muestra el ANUNCIO en todos los canales donde esta el bot
    def HANDLE_ANUNCIOKUAK(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '&')):
            self.serversocket.send('¡ANUNCIO! %s dice: %s' % (sender, params[1]))
            
            for channel in self.bot.data:
                users = [self.bot.data[channel]['users'][i:i+35] for i in range(0, len(self.bot.data[channel]['users']), 35)]

                for sublist in users:
                    self.bot.queue_append('PRIVMSG %s :%s' % (channel, ' '.join(sublist)))

                self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x030,4\02¡ANUNCIO!\02\x03\x030,5 %s dice:\x03\x031,0\02 %s\02\x03' % ('%s\'%s' % (sender[:-1], sender[-1:]), params[1])))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del ANUNCIO, muestra un mensaje en todos los canales donde esta el bot
    def HANDLE_ANUNCIO(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '@')):
            self.serversocket.send('¡ANUNCIO! %s dice: %s' % (sender, params[1]))
            
            for channel in self.bot.data:
                self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x030,4\02¡ANUNCIO!\02\x03\x030,5 %s dice:\x03\x031,0\02 %s\02\x03' % ('%s\'%s' % (sender[:-1], sender[-1:]), params[1])))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del DONAR, muestra los links de donacion del perfil de eR asociado al nick, o si se especifica, de otro nick
    def HANDLE_DONAR(self, sender, params, is_pm):
        channel = sender if is_pm == True else params[0]

        try:
            if(len(params) > 1):
                if(bool(params[1].strip())):
                    sender = params[1].strip(' \r\n')

            id = str(self.erepublik.get_id(sender))

            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x03\02%s\02 - \02Donar items:\02\x03 http://www.erepublik.com/es/economy/donate-items/%s\x03 - \02Donar dinero:\02 \x03http://www.erepublik.com/es/economy/donate-money/%s' % (sender, id, id)))
        except:
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x031,4\02Error:\02\x03 Nick \02"%s"\02 no esta registrado.' % sender))

    # Manejador del FC, muestra estadisticas del perfil de eR asociado al nick, o si se especifica, de otro nick
    def HANDLE_FC(self, sender, params, is_pm):
        channel = sender if is_pm == True else params[0]

        try:
            if(len(params) > 1):
                if(bool(params[1].strip())):
                    sender = params[1].strip(' \r\n')

            id = self.erepublik.get_id(sender)
            level = self.erepublik.get_level(sender)
            strength = self.erepublik.get_strength(sender)
            rank_points = self.erepublik.get_rank_points(sender)
            citizenship = self.erepublik.get_citizenship(sender)
            nick = self.erepublik.get_nick(sender)

            rank_name = self.erepublik.calculate_rank_name(rank_points)

            q0 = self.erepublik.calculate_damage(rank_points, strength, 0, level, 1)
            q1 = self.erepublik.calculate_damage(rank_points, strength, 20, level, 1)
            q2 = self.erepublik.calculate_damage(rank_points, strength, 40, level, 1)
            q3 = self.erepublik.calculate_damage(rank_points, strength, 60, level, 1)
            q4 = self.erepublik.calculate_damage(rank_points, strength, 80, level, 1)
            q5 = self.erepublik.calculate_damage(rank_points, strength, 100, level, 1)
            q6 = self.erepublik.calculate_damage(rank_points, strength, 120, level, 1)
            q7 = self.erepublik.calculate_damage(rank_points, strength, 200, level, 1)

            #self.bot.queue_append('PRIVMSG %s :%s' % (channel, 'Nick: %s | ID: %d | Nivel: %d | Fuerza: %.2f | Rango: %s | Puntos de rango: %d | Ciudadania: %s ' % (nick, id, level, strength, rank_name, rank_points, citizenship)))
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x03\02%s\02\x03 (%s, %.2f de fuerza): \x0314[Q0: \02%d\02]\x03 \x033[Q1: \02%d\02]\x03 \x0312[Q2: \02%d\02]\x03 \x032[Q3: \02%d\02]\x03 \x037[Q4: \02%d\02]\x03 \x034[Q5: \02%d\02]\x03 \x035[Q6: \02%d\02]\x03 \x036[Q7: \02%d\02]\x03 \x030,3[Q7 + NE: \02%d\02]\x03 \x030,3[Q7 + 50%%: \02%d\02]\x03 \x030,3[Q7 + NE + 50%%: \02%d\02]\x03' % (nick, rank_name, strength, q0, q1, q2, q3, q4, q5, q6, q7, q7 * 1.1, q7 * 1.5, q7 * 1.65)))
        except:
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x031,4\02Error:\02\x03 Nick \02"%s"\02 no esta registrado.' % sender))

    # Manejador del LP, muestra estadisticas del perfil de eR asociado al nick, o si se especifica, de otro nick
    def HANDLE_LP(self, sender, params, is_pm):
        channel = sender if is_pm == True else params[0]

        try:
            if(len(params) > 1):
                if(bool(params[1].strip())):
                    sender = params[1].strip(' \r\n')

            id = self.erepublik.get_id(sender)
            level = self.erepublik.get_level(sender)
            strength = self.erepublik.get_strength(sender)
            rank_points = self.erepublik.get_rank_points(sender)
            citizenship = self.erepublik.get_citizenship(sender)
            nick = self.erepublik.get_nick(sender)

            rank_name = self.erepublik.calculate_rank_name(rank_points)

            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x03\02%s\02 [%d] | \02Nivel:\02 %d | \02Fuerza:\02 %.2f | \02Rango:\02 %s (%d) | \02Ciudadania:\02 %s\x03' % (nick, id, level, strength, rank_name, rank_points, citizenship)))
        except:
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x031,4\02Error:\02\x03 Nick \02"%s"\02 no esta registrado.' % sender))


    # Manejador del LINK, muestra el link del perfil de eR asociado al nick, o si se especifica, de otro nick
    def HANDLE_LINK(self, sender, params, is_pm):
        channel = sender if is_pm == True else params[0]

        try:
            if(len(params) > 1):
                if(bool(params[1].strip())):
                    sender = params[1].strip(' \r\n')

            id = self.erepublik.get_id(sender)

            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x03El link al perfil de \02%s\02 es:\x03 http://www.erepublik.com/es/citizen/profile/%d' % (sender, id)))
        except:
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x031,4\02Error:\02\x03 Nick \02"%s"\02 no esta registrado.' % sender))

    # Manejador del REGID, registra el ID asociado al nick que envia el comando
    def HANDLE_REGID(self, sender, params, is_pm):
        channel = sender if is_pm == True else params[0]

        try:
            self.erepublik.reg_nick_write(sender, params[1])

            self.bot.queue_append('PRIVMSG %s :%s' % (channel, 'Usuario registrado.'))
        except:
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, 'Error al registrar usuario.'))

    # Manejador del ORDENES, muestra las ordenes en lista segun prioridad
    def HANDLE_ORDENES(self, sender, params, is_pm):
        channel = params[0]

        if(is_pm):
            channel = sender

        for zone in self.bot.orders:
            for div in ['d1', 'd2', 'd3', 'd4']:
                if self.bot.orders[zone][div] == 'NO PEGAR':
                    self.bot.orders[zone][div] = '\x030,1\02 NO PEGAR \02\x03'
                elif self.bot.orders[zone][div] == 'BAJA':
                    self.bot.orders[zone][div] = '\x030,9\02 BAJA \02\x03'
                elif self.bot.orders[zone][div] == 'MEDIA':
                    self.bot.orders[zone][div] = '\x030,8\02 MEDIA \02\x03'
                elif self.bot.orders[zone][div] == 'ALTA':
                    self.bot.orders[zone][div] = '\x030,7\02 ALTA \02\x03'
                elif self.bot.orders[zone][div] == 'MAXIMA':
                    self.bot.orders[zone][div] = '\x030,4\02 MAXIMA \02\x03'

            data = (zone, self.bot.orders[zone]['id'], self.bot.orders[zone]['d1'], self.bot.orders[zone]['d2'], self.bot.orders[zone]['d3'], self.bot.orders[zone]['d4'], self.bot.orders[zone]['side'])
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, '\x030,4\02Zona:\02\x03 %s || \02Link: http://erpk.org/b/%d\02 || \02Div 1:\02 %s || \02Div 2:\02 %s || \02Div 3:\02 %s || \02Div 4:\02 %s || \02Side:\02 \x030,3%s\x03' % data))

    # Manejador del RW, muestra datos del estado de la rebelion de el/la region/pais indicad@
    def HANDLE_RW(self, sender, params, is_pm):
        channel = sender if is_pm == True else params[0]

        if(params[1][0] == '-'):
            type = params[1][1:params[1].find(' ')].lower()
            what = params[1][params[1].find(' ') + 1:].strip('\r\n ').lower()
            
            if(len(what) > 0 and what[0] != '-'):
                if(type == 'p' or type == 'a'):
                    if(type == 'a'):
                        what = self.watcher.get_country_name(what)

                    if(what != False):
                        self.bot.queue_append('PRIVMSG %s :Regiones cargadas en: %s' % (channel, what))

                        rws = self.watcher.get_by_country_name(what)

                        if(rws != False):
                            enabled = False

                            for rw in rws:
                                if(rw['enabled'] == True):
                                    enabled = True
                                    self.bot.queue_append('PRIVMSG %s :%s [%s] | Supporters: %d/10' % (channel, rw['region_name'], rw['region_initial'], len(rw['supporters'])))

                            if(enabled == False):
                                self.bot.queue_append('PRIVMSG %s :El pais no tiene rebeliones activas.' % (channel))
                        else:
                            self.bot.queue_append('PRIVMSG %s :\x031,4\02Error:\02\x03 Pais erroneo o no cargado en el sistema.' % channel)
                    else:
                        self.bot.queue_append('PRIVMSG %s :\x031,4\02Error:\02\x03 Abreviacion de pais erronea o inexistente.' % channel)
                elif(type == 's'):
                    rw = self.watcher.get_by_region_initial(what)

                    if(rw != False):
                        if(rw['enabled'] == True):
                            self.bot.queue_append('PRIVMSG %s :%s [%s] | Pais: %s [%s] | Supporters: %d/10' % (channel, rw['region_name'], rw['region_initial'], rw['country_name'], rw['country_initial'],len(rw['supporters'])))
                        else:
                            self.bot.queue_append('PRIVMSG %s :La region %s no tiene una rebelion activa.' % (channel, rw['region_name']))
                    else:
                        self.bot.queue_append('PRIVMSG %s :\x031,4\02Error:\02\x03 Region incorrecta o no cargada en el sistema.' % channel)
                else:
                    self.bot.queue_append('PRIVMSG %s :\x031,4\02Error:\02\x03 tipo de parametro incorrecto.' % channel)
            else:
                self.bot.queue_append('PRIVMSG %s :\x031,4\02Error:\02\x03 No se especifico valor del parametro.' % channel)
        else:
            self.bot.queue_append('PRIVMSG %s :\x031,4\02Error:\02\x03 No se especifico tipo de parametro.' % channel)

    # Manejador del HELP, muestra link al HTML de ayuda del bot
    def HANDLE_HELP(self, sender, params, is_pm):
        if(is_pm):
            self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Hoja de ayuda: %s' % self.bot.help_html))
        else:
            channel = params[0]
            self.bot.queue_append('PRIVMSG %s :%s' % (channel, 'Hoja de ayuda: %s' % self.bot.help_html))

    # Manejador del JOIN, une el bot a un canal, parametro opcional de contraseña
    def HANDLE_JOIN(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '&')):
            self.bot.queue_append('JOIN %s\n' % params[1].strip('\r\n'))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))
    
    # Manejador del PART, hace salir al bot de un canal y borra dicho canal de la lista temporal de canales
    def HANDLE_PART(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '&')):
            self.bot.queue_append('PART %s\n' % params[1].strip('\r\n'))

            self.bot.del_channel(params[1].strip('\r\n'))
            self.bot.del_channel_event(params[1].strip('\r\n'))

            self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Canal eliminado de la lista de canales temporales y de canales de evento. No olvides hacerlo efectivo con ".update".'))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del STAY, añade el canal especificado a la lista temporal de canales, parametro opcional la contraseña del canal
    def HANDLE_STAY(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '&')):
            parts = params[1].strip('\r\n').split(' ', 1)

            if len(parts) > 1:
                self.bot.add_channel(parts[0], parts[1])
            else:
                self.bot.add_channel(parts[0], '')

            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Canal agregado para autoinicio. No olvides hacerlo efectivo con ".update".'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: Canal agregado para autoinicio. No olvides hacerlo efectivo con ".update".' % sender))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del DEL, elimina el nick ESPECIFICADO de la lista temporal del permiso ESPECIFICADO
    def HANDLE_DEL(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '&')):
            parts = params[1].strip('\r\n').split(' ', 1)

            if len(parts) > 1:
                if((parts[1] != '~' and parts[1] != '&') or self.bot.has_permission(sender, '~')):
                    self.bot.del_permission(parts[0], parts[1])

                    if(is_pm):
                        self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Permiso eliminado correctamente. No olvides hacerlo efectivo con ".update".'))
                    else:
                        self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: Permiso eliminado correctamente. No olvides hacerlo efectivo con ".update".' % sender))
                else:
                    if(is_pm):
                        self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No puedes eliminar permisos iguales o superiores al tuyo.'))
                    else:
                        self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No puedes eliminar permisos iguales o superiores al tuyo.' % sender))
            else:
                if(is_pm):
                    self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'El formato del comando es erroneo.'))
                else:
                    self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: El formato del comando es erroneo.' % sender))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del ADD, agrega el nick ESPECIFICADO en la lista temporal del permiso ESPECIFICADO
    def HANDLE_ADD(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '&')):
            parts = params[1].strip('\r\n').split(' ', 1)

            if len(parts) > 1:
                if((parts[1] != '~' and parts[1] != '&') or self.bot.has_permission(sender, '~')):
                    self.bot.add_permission(parts[0], parts[1])

                    if(is_pm):
                        self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Permiso asignado correctamente. No olvides hacerlo efectivo con ".update".'))
                    else:
                        self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: Permiso asignado correctamente. No olvides hacerlo efectivo con ".update".' % sender))
                else:
                    if(is_pm):
                        self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Solo puedes asignar permisos inferiores al tuyo.'))
                    else:
                        self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: Solo puedes asignar permisos inferiores al tuyo.' % sender))
            else:
                if(is_pm):
                    self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'El formato del comando es erroneo.'))
                else:
                    self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: El formato del comando es erroneo.' % sender))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del UPDATE, actualiza hojas de datos de permisos y canales con los datos actuales del bot
    def HANDLE_UPDATE(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '&')):
            self.bot.update_permission()
            self.bot.update_channels()
            self.bot.update_channels_events()

            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Base de datos de permisos y canales actualizadas.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: Base de datos de permisos y canales actualizadas.' % sender))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del SAY, hace hablar al bot en el canal especificado diciendo el mensaje del parametro
    def HANDLE_SAY(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '~')):
            parts = params[1].split(' ', 1)

            if(parts[0].lower() != self.bot.nick.lower()):
                if(parts[1][0] != '.'):
                    self.bot.queue_append('PRIVMSG %s :%s' % (parts[0], parts[1]))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del ACT, hace actuar al bot en el canal especificado diciendo el mensaje del parametro
    def HANDLE_ACT(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '~')):
            parts = params[1].split(' ', 1)

            if(parts[0].lower() != self.bot.nick.lower()):
                if(parts[1][0] != '.'):
                    self.bot.queue_append('PRIVMSG %s :\01ACTION %s\01' % (parts[0], parts[1].strip('\r\n')))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))
    
    # Manejador del REBOOT, reinicia el bot, por consecuencia se actualizan listas de canales y permisos desde las hojas de calculo
    def HANDLE_REBOOT(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '~')):
            self.bot.running = False
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del SHUTDOWN, desconecta el bot de forma remota evitando su reinicio. Finaliza todos los threads
    def HANDLE_SHUTDOWN(self, sender, params, is_pm):
        if(self.bot.has_permission(sender, '~')):
            self.bot.dont_reconnect = True
            self.bot.queue_append('QUIT :%s' % 'Debo irme, mi planeta me necesita.')
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del MATAR, "mata" al nick indicado
    def HANDLE_MATAR(self, sender, params, is_pm):
        if(is_pm == False):
            target = params[1][:params[1].find(' ')]

            if('xxciro' in target.lower()):
                if('xxciro' in sender.lower()):
                    self.bot.queue_append(*['PRIVMSG %s :No podria vivir sin usted, no me oblige, nooooooooooo!' % params[0],
                        'PRIVMSG %s :\01ACTION mata a %s y se suicida.\01' % (params[0], target)])
                else:
                    self.bot.queue_append(*['PRIVMSG %s :¿Osas intentar matar a mi creador?' % params[0],
                        'PRIVMSG %s :\01ACTION captura a %s y lo encierra en una jaula. El creador decidira que hacer contigo.\01' % (params[0], sender)])
            elif(self.bot.nick.lower() in target.lower()):
                if('xxciro' in sender.lower()):
                    self.bot.queue_append(*['PRIVMSG %s :Si mi amo!' % params[0],
                        'PRIVMSG %s :\01ACTION se suicida.\01' % params[0]])
                else:
                    self.bot.queue_append(*['PRIVMSG %s :¿Me tomas por idiota?' % params[0],
                        'PRIVMSG %s :\01ACTION mata a %s y juega con sus tripas :3\01' % (params[0], sender)])
            else:
                self.bot.queue_append('PRIVMSG %s :\01ACTION mata a %s y juega con sus tripas :3\01' % (params[0], target))

    # Manejador del ABRAZAR, "abraza" al nick indicado mediante un ACT
    def HANDLE_ABRAZAR(self, sender, params, is_pm):
        if(is_pm == False):
            target = params[1][:params[1].find(' ')]

            if('xxciro' in target.lower()):
                self.bot.queue_append('PRIVMSG %s :\01ACTION abraza a su creador :3\01' % params[0])
            elif(self.bot.nick.lower() in target.lower()):
                self.bot.queue_append('PRIVMSG %s :\01ACTION se autoabraza.\01' % params[0])
            else:
                self.bot.queue_append('PRIVMSG %s :\01ACTION abraza a %s :3\01' % (params[0], target))

    # Manejador del EJECT, kickbanea al nick indicado durante x segundos
    def HANDLE_EJECT(self, sender, params, is_pm):
        if(is_pm == False):
            if(self.bot.has_level(params[0].lower(), self.bot.nick, '%')):            
                if(self.bot.has_level(params[0].lower(), sender, '%')):
                    target = params[1][:params[1].find(' ')]

                    ban_time = random.randrange(10)

                    if('xxciro' in target.lower()):
                        if('xxciro' in sender.lower()):
                            self.bot.queue_append('PRIVMSG %s :No podria vivir sin usted, no me oblige, nooooooooooo!' % params[0])

                            self.bot.queue_append('PRIVMSG %s :El creador ha sido ejecutado durante %d segundos' % (params[0], ban_time))
                            self.bot.queue_append('MODE %s +b %s' % (params[0], target))
                            self.bot.queue_append('KICK %s %s :A VOOOLLLLAAARRR!!!!!!! Regresa dentro de %d segundos!!!' % (params[0], target, ban_time))
                            
                            time.sleep(ban_time)

                            self.bot.queue_append('MODE %s -b %s' % (params[0], target))
                        else:
                            self.bot.queue_append('PRIVMSG %s :¿Osas intentar matar a mi creador?' % params[0])

                            self.bot.queue_append('PRIVMSG %s :%s ha sido ejecutado por %s durante %d segundos' % (params[0], sender, self.bot.nick, ban_time))
                            self.bot.queue_append('MODE %s +b %s' % (params[0], sender))
                            self.bot.queue_append('KICK %s %s :A VOOOLLLLAAARRR!!!!!!! Regresa dentro de %d segundos!!!' % (params[0], sender, ban_time))

                            time.sleep(ban_time)

                            self.bot.queue_append('MODE %s -b %s' % (params[0], sender))
                    elif(self.bot.nick.lower() in target.lower()):
                        self.bot.queue_append('PRIVMSG %s :¿Me tomas por idiota?' % params[0])

                        self.bot.queue_append('PRIVMSG %s :%s ha sido ejecutado por %s durante %d segundos' % (params[0], sender, self.bot.nick, ban_time))
                        self.bot.queue_append('MODE %s +b %s' % (params[0], sender))
                        self.bot.queue_append('KICK %s %s :A VOOOLLLLAAARRR!!!!!!! Regresa dentro de %d segundos!!!' % (params[0], sender, ban_time))

                        time.sleep(ban_time)

                        self.bot.queue_append('MODE %s -b %s' % (params[0], sender))
                    else:
                        self.bot.queue_append('PRIVMSG %s :%s ha sido ejecutado por %s durante %d segundos' % (params[0], target, sender, ban_time))
                        self.bot.queue_append('MODE %s +b %s' % (params[0], target))
                        self.bot.queue_append('KICK %s %s :A VOOOLLLLAAARRR!!!!!!! Regresa dentro de %d segundos!!!' % (params[0], target, ban_time))
                        
                        time.sleep(ban_time)

                        self.bot.queue_append('MODE %s -b %s' % (params[0], target))
                else:
                    self.bot.queue_append('PRIVMSG %s :%s: No tienes accesos suficientes como para ejecutar este comando.' % (params[0], sender))
            else:
                self.bot.queue_append('PRIVMSG %s :%s: No tengo accesos suficientes como para ejecutar este comando, necesito HOP.' % (params[0], sender))

    # Manejador del FUSILAR, kickbanea al nick indicado durante x segundos
    def HANDLE_FUSILAR(self, sender, params, is_pm):
        if(is_pm == False):
            if(self.bot.has_level(params[0].lower(), self.bot.nick, '%')):            
                if(self.bot.has_level(params[0].lower(), sender, '%')):
                    target = params[1][:params[1].find(' ')]

                    if('xxciro' in target.lower()):
                        if('xxciro' in sender.lower()):
                            self.bot.queue_append('PRIVMSG %s :No podria vivir sin usted, no me oblige, nooooooooooo!' % params[0])

                            self.bot.queue_append(*['PRIVMSG %s :\01ACTION le pone un cigarro a %s y lo prende\01' % (params[0], target),
                                'PRIVMSG %s :\01ACTION deja que %s diga sus ultimas palabras\01' % (params[0], target),
                                'PRIVMSG %s :\01ACTION Apunta!!!\01' % (params[0]),
                                'MODE %s +b %s' % (params[0], target),
                                'KICK %s %s :PUUUUMMMMMMM!!!!!! You\'re DEAD!' % (params[0], target),
                                'MODE %s -b %s' % (params[0], target)])
                        else:
                            self.bot.queue_append('PRIVMSG %s :¿Osas intentar matar a mi creador?' % params[0])

                            self.bot.queue_append(*['PRIVMSG %s :\01ACTION le pone un cigarro a %s y lo prende\01' % (params[0], sender),
                                'PRIVMSG %s :\01ACTION deja que %s diga sus ultimas palabras\01' % (params[0], sender),
                                'PRIVMSG %s :\01ACTION Apunta!!!\01' % (params[0]),
                                'MODE %s +b %s' % (params[0], sender),
                                'KICK %s %s :PUUUUMMMMMMM!!!!!! You\'re DEAD!' % (params[0], sender),
                                'MODE %s -b %s' % (params[0], sender)])
                    elif(self.bot.nick.lower() in target.lower()):
                        self.bot.queue_append('PRIVMSG %s :¿Me tomas por idiota?' % params[0])

                        self.bot.queue_append(*['PRIVMSG %s :\01ACTION le pone un cigarro a %s y lo prende\01' % (params[0], sender),
                            'PRIVMSG %s :\01ACTION deja que %s diga sus ultimas palabras\01' % (params[0], sender),
                            'PRIVMSG %s :\01ACTION Apunta!!!\01' % (params[0]),
                            'MODE %s +b %s' % (params[0], sender),
                            'KICK %s %s :PUUUUMMMMMMM!!!!!! You\'re DEAD!' % (params[0], sender),
                            'MODE %s -b %s' % (params[0], sender)])
                    else:
                        self.bot.queue_append(*['PRIVMSG %s :\01ACTION le pone un cigarro a %s y lo prende\01' % (params[0], target),
                            'PRIVMSG %s :\01ACTION deja que %s diga sus ultimas palabras\01' % (params[0], target),
                            'PRIVMSG %s :\01ACTION Apunta!!!\01' % (params[0]),
                            'MODE %s +b %s' % (params[0], target),
                            'KICK %s %s :PUUUUMMMMMMM!!!!!! You\'re DEAD!' % (params[0], target),
                            'MODE %s -b %s' % (params[0], target)])
                else:
                    self.bot.queue_append('PRIVMSG %s :%s: No tienes accesos suficientes como para ejecutar este comando.' % (params[0], sender))
            else:
                self.bot.queue_append('PRIVMSG %s :%s: No tengo accesos suficientes como para ejecutar este comando, necesito HOP.' % (params[0], sender))

    # Manejador del EVENTO, añade el canal especificado a la lista temporal de canales, parametro opcional la contraseña del canal
    def HANDLE_EVENTO(self, sender, params, is_pm):
        parts = params[1].strip(' \r\n').split(' ', 1)

        if(self.bot.has_level(params[0].lower(), sender, '&') or self.bot.has_permission(sender, '~')):
            if len(parts) == 2 and (parts[1].lower() == 'enable' or parts[1].lower() == 'disable'):
                if parts[1].lower() == 'enable':
                    self.bot.add_channel_event(parts[0])

                    if(is_pm):
                        self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Canal agregado temporalmente para evento. No olvides hacerlo efectivo con ".update".'))
                    else:
                        self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: Canal agregado  temporalmente para evento. No olvides hacerlo efectivo con ".update".' % sender))
                else:
                    self.bot.del_channel_event(parts[0])

                    if(is_pm):
                        self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Canal eliminado temporalmente para evento. No olvides hacerlo efectivo con ".update".'))
                    else:
                        self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: Canal eliminado  temporalmente para evento. No olvides hacerlo efectivo con ".update".' % sender))
            else:
                if(is_pm):
                    self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'Formato del comando invalido.'))
                else:
                    self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: Formato del comando invalido.' % sender))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))

    # Manejador del ADMIN, permite visualizar valores de variables
    def HANDLE_ADMIN(self, sender, params, is_pm):
        if self.bot.has_permission(sender, '~'):
            parts = params[1].strip(' \r\n').split(' ', 1)

            str_exit = 'Formato de comando invalido'

            if len(parts) >= 1:
                if parts[0].lower() == 'evento':
                    str_exit = ', '.join(self.bot.channels_events)
                elif parts[0].lower() == 'channels':
                    channels_list = []

                    for channel in self.bot.data:
                        channels_list.append(channel)

                    str_exit = ', '.join(channels_list)
                elif parts[0].lower() == 'data':
                    str_exit = str(self.bot.data)
                else:
                    str_exit = 'Valor de busqueda invalido'
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, str_exit))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: %s' % (sender, str_exit)))
        else:
            if(is_pm):
                self.bot.queue_append('PRIVMSG %s :%s' % (sender, 'No tienes permiso para utilizar ese comando.'))
            else:
                self.bot.queue_append('PRIVMSG %s :%s' % (params[0], '%s: No tienes permiso para utilizar ese comando.' % sender))