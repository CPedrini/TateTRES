#-*- encoding: utf-8 -*-

import time, threading, re, hashlib, sys
from collections import deque

from requests import session

class Events():
    # Metodo constructor, seteos basicos necesarios de configuracion, instancia objetos utiles
    def __init__(self, bot):
        self.country_id = {
            'Brazil': '9',
            'Canada': '23',
            'Saudi-Arabia': '164',
            'Italy': '10',
            'Ireland': '54',
            'USA': '24',
            'India': '48',
            'Lithuania': '72',
            'France': '11',
            'United-Kingdom': '29',
            'Slovakia': '36',
            'Peru': '77',
            'Argentina': '27',
            'Bolivia': '76',
            'Norway': '37',
            'North-Korea': '73',
            'Republic-of-Macedonia-FYROM': '79',
            'Israel': '58',
            'Belarus': '83',
            'Iran': '56',
            'Singapore': '68',
            'Venezuela': '28',
            'Malaysia': '66',
            'Montenegro': '80',
            'New-Zealand': '84',
            'Slovenia': '61',
            'China': '14',
            'Republic-of-China-Taiwan': '81',
            'Chile': '64',
            'Belgium': '32',
            'Thailand': '59',
            'Germany': '12',
            'Philippines': '67',
            'Poland': '35',
            'Spain': '15',
            'Ukraine': '40',
            'Netherlands': '31',
            'Colombia': '78',
            'Denmark': '55',
            'Turkey': '43',
            'Indonesia': '49',
            'Romania': '1',
            'South-Korea': '47',
            'Sweden': '38',
            'Australia': '50',
            'Czech-Republic': '34',
            'Finland': '39',
            'Hungary': '13',
            'Switzerland': '30',
            'Russia': '41',
            'United-Arab-Emirates': '166',
            'Pakistan': '57',
            'South-Africa': '51',
            'Albania': '167',
            'Estonia': '70',
            'Portugal': '53',
            'Mexico': '26',
            'Croatia': '63',
            'Uruguay': '74',
            'Serbia': '65',
            'Egypt': '165',
            'Austria': '33',
            'Latvia': '71',
            'Republic-of-Moldova': '52',
            'Greece': '44',
            'Paraguay': '75',
            'Japan': '45',
            'Cyprus': '82',
            'Bosnia-Herzegovina': '69',
            'Bulgaria': '42'
        }

        self.channels = []

        self.data = {}
        # Data format: {'Argentina': deque(['link 1', 'link 2'])}

        # Bandera de ejecucion, util en caso de que se decida matar de forma manual los threads para actualizar y guardar los datos
        self.run = True

        # Almacenada referencia a instancia del bot para envio de mensajes y revision de canales ¿Guardar referencia solo a metodo de envio?
        self.bot = bot

        # Iniciar thread loader
        th = threading.Thread(target=self.start_loader)
        th.daemon = True
        th.start()

    # Thread loader, restaura datos de eventos de archivo fisico e inicia threads de parseo de eventos nuevos
    def start_loader(self):
        for c in self.country_id.keys():
            th = threading.Thread(target=self.atomic_loader, args=[c])
            th.daemon = True

            th.start()

            time.sleep(5)

    # Thread particular de evento de un pais
    # Busca eventos de forma periodica, si hay nuevos los envia a los canales que tienen evento habilitado
    def atomic_loader(self, country):
        first = True

        while self.run:
            try:
                c = session()

                request = c.get('http://www.erepublik.com/es/main/news/military/all/%s/1/rss' % country)
                
                request.encoding = 'utf-8'

                links = re.findall('<a href=\"(.*)</a>', request.text)

                for link in links:
                    parts = link.split('">')

                    if parts[0].find('<') > -1 or parts[1].find('<') > -1:
                        continue

                    if country not in self.data.keys():
                        self.data[country] = deque([])

                    if parts[0] not in self.data[country]:
                        self.data[country].append(parts[0])

                        # DEBUG: print('Country: %s - %d' % (country, len(self.data[country])))

                        if first == False:
                            if(len(self.data[country]) > 11):
                                self.data[country].popleft()

                            send_to = self.bot.channels_events

                            if(len(send_to) > 0):
                                self.bot.queue_append('PRIVMSG %s :\x030,4\02EVENTO:\02\x03 %s | %s' % ((',').join(send_to), parts[0], parts[1]))
            except:
                # DEBUG: print(sys.exc_info())
                pass
            
            time.sleep(350)
            first = False

            #15.7 - New-Zealand
            #15.6
            #16.3
            #16.6
            #16.7
            #16.8
            #16.9