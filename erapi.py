#-*- encoding: utf-8 -*-

import csv, math, time, re, threading, sys

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

class ErAPI():
    # Metodo constructor, seteos basicos necesarios de configuracion, instancia objetos utiles
    def __init__(self):
        self.data = {}
        # Data format: {'XXCiro|BNC': {'id': 123456, 'nick': 'XXCiro', 'level': 49, 'strength': 532.5, 'rank_points': 1233354, 'citizenship': 'Argentina'}}
        
        # Diccionario de puntos/rango
        self.rank_required_points = {
            "Recruit": 0,
            "Private": 15,
            "Private*": 45,
            "Private**": 80,
            "Private***": 120,
            "Corporal": 170,
            "Corporal*": 250,
            "Corporal**": 350,
            "Corporal***": 450,
            "Sergeant": 600,
            "Sergeant*": 800,
            "Sergeant**": 1000,
            "Sergeant***": 1400,
            "Lieutenant": 1850,
            "Lieutenant*": 2350,
            "Lieutenant**": 3000,
            "Lieutenant***": 3750,
            "Captain": 5000,
            "Captain*": 6500,
            "Captain**": 9000,
            "Captain***": 12000,
            "Major": 15500,
            "Major*": 20000,
            "Major**": 25000,
            "Major***": 31000,
            "Commander": 40000,
            "Commander*": 52000,
            "Commander**": 67000,
            "Commander***": 85000,
            "Lt Colonel": 110000,
            "Lt Colonel*": 140000,
            "Lt Colonel**": 180000,
            "Lt Colonel***": 225000,
            "Colonel": 285000,
            "Colonel*": 355000,
            "Colonel**": 435000,
            "Colonel***": 540000,
            "General": 660000,
            "General*": 800000,
            "General**": 950000,
            "General***": 1140000,
            "Field Marshal": 1350000,
            "Field Marshal*": 1600000,
            "Field Marshal**": 1875000,
            "Field Marshal***": 2185000,
            "Supreme Marshal": 2550000,
            "Supreme Marshal*": 3000000,
            "Supreme Marshal**": 3500000,
            "Supreme Marshal***": 4150000,
            "National Force": 4900000,
            "National Force*": 5800000,
            "National Force**": 7000000,
            "National Force***": 9000000,
            "World Class Force": 11500000,
            "World Class Force*": 14500000,
            "World Class Force**": 18000000,
            "World Class Force***": 22000000,
            "Legendary Force": 26500000,
            "Legendary Force*": 31500000,
            "Legendary Force**": 37000000,
            "Legendary Force***": 42000000,
            "God of War": 50000000,
            "God of War*": 100000000 ,
            "God of War**": 200000000,
            "God of War***": 500000000,
            "Titan": 1000000000,
            "Titan*": 2000000000,
            "Titan**": 4000000000,
            "Titan***": 10000000000}

        # Lista ordenada de rangos segun importancia
        self.rank_to_pos = [
            "Recruit",
            "Private",
            "Private*",
            "Private**",
            "Private***",
            "Corporal",
            "Corporal*",
            "Corporal**",
            "Corporal***",
            "Sergeant",
            "Sergeant*",
            "Sergeant**",
            "Sergeant***",
            "Lieutenant",
            "Lieutenant*",
            "Lieutenant**",
            "Lieutenant***",
            "Captain",
            "Captain*",
            "Captain**",
            "Captain***",
            "Major",
            "Major*",
            "Major**",
            "Major***",
            "Commander",
            "Commander*",
            "Commander**",
            "Commander***",
            "Lt Colonel",
            "Lt Colonel*",
            "Lt Colonel**",
            "Lt Colonel***",
            "Colonel",
            "Colonel*",
            "Colonel**",
            "Colonel***",
            "General",
            "General*",
            "General**",
            "General***",
            "Field Marshal",
            "Field Marshal*",
            "Field Marshal**",
            "Field Marshal***",
            "Supreme Marshal",
            "Supreme Marshal*",
            "Supreme Marshal**",
            "Supreme Marshal***",
            "National Force",
            "National Force*",
            "National Force**",
            "National Force***",
            "World Class Force",
            "World Class Force*",
            "World Class Force**",
            "World Class Force***",
            "Legendary Force",
            "Legendary Force*",
            "Legendary Force**",
            "Legendary Force***",
            "God of War",
            "God of War*",
            "God of War**",
            "God of War***",
            "Titan",
            "Titan*",
            "Titan**",
            "Titan***",]

        # Bandera de ejecucion, util en caso de que se decida matar de forma manual los threads para actualizar y guardar los datos
        self.run = True

        # Se paraleliza la carga de datos en un hilo nuevo, el cual es demonio del invocador en caso de "muerte prematura"
        th = threading.Thread(target=self.data_loader)
        th.daemon = True
        th.start()

    # Metodo invocador, carga datos y crea threads para guardar y actualizar informacion, solo llamado desde constructor
    def data_loader(self):
        self.load_data()

        self.data_saver_th = threading.Thread(target=self.data_saver)
        self.data_saver_th.daemon = True
        self.data_saver_th.start()

        self.data_updater_th = threading.Thread(target=self.data_updater)
        self.data_updater_th.daemon = True
        self.data_updater_th.start()

    # Metodo para volcar informacion a archivo fisico, solo llamado de metodo data_loader
    def data_saver(self):
        while self.run:
            self.save_data()

            time.sleep(60)

    # Metodo para actualizar informacion, solo llamado de metodo data_loader
    def data_updater(self):
        while self.run:
            for irc_nick in self.data:
                self.update_data(irc_nick)
                time.sleep(30)

            time.sleep(600)

    # ---------------------------------------------------------------------------------- #
    # @ PUBLIC METHODS                                                                   #
    # ---------------------------------------------------------------------------------- #

    # Metodo para actualizar informacion local del objeto desde archivo
    def load_data(self):
        try:
            f = open('data/er_nick-data.csv', 'rt')
            reader = csv.reader(f)
            for nick_irc,id,nick_er,level,strength,rank_points,citizenship in reader:
                self.data[nick_irc] = {'id': int(id), 'nick': nick_er, 'level': int(level), 'strength': float(strength), 'rank_points': int(rank_points), 'citizenship': citizenship}
            f.close()
        except:
            pass

    # Metodo para guardar informacion local del objeto en archivo
    def save_data(self):
        try:
            f = open('data/er_nick-data.csv', 'wt')
            writer = csv.writer(f)
            for u in self.data:
                writer.writerow([u, self.data[u]['id'], self.data[u]['nick'], self.data[u]['level'], self.data[u]['strength'], self.data[u]['rank_points'], self.data[u]['citizenship']])
            f.close()
        except:
            pass

    # Metodo scraper para actualizar informacion local del objeto del nick de irc especificado
    def update_data(self, irc_nick):
        try:
            id = self.data[irc_nick]['id']

            c = urlopen('http://www.erepublik.com/es/citizen/profile/%d' % id)
            page = c.read()
            c.close()

            self.data[irc_nick]['nick'] = re.search('<meta name="title" content="(.+?) - Ciudadano del Nuevo Mundo" \/>', page.decode('utf-8')).group(1)
            self.data[irc_nick]['level'] = int(re.search('<strong class="citizen_level">(.+?)<\/strong>', page.decode('utf-8'), re.DOTALL).group(1))
            self.data[irc_nick]['strength'] = float(re.search('<span class="military_box_info mb_bottom">(.+?)</span>', page.decode('utf-8'), re.DOTALL).group(1).strip('\r\n\t ').replace(',',''))
            self.data[irc_nick]['rank_points'] = int(re.search('<span class="rank_numbers">(.+?) \/', page.decode('utf-8'), re.DOTALL).group(1).replace(',',''))
            self.data[irc_nick]['citizenship'] = re.search('<a href="http\:\/\/www.erepublik.com\/es\/country\/society\/([^ \t\n\x0B\f\r]+?)">', page.decode('utf-8')).group(1)
        except:
            pass

    # Metodo para actualizar informacion local del objeto con nick de irc e id especificados, fuerza actualizacion del mismo
    def reg_nick_write(self, nick, id):
        if(nick.lower() in self.data.keys()):
            self.data[nick.lower()]['id'] = int(id)
        else:
            self.data[nick.lower()] = {'id': int(id), 'nick': nick, 'level': 1, 'strength': 0, 'rank_points': 0, 'citizenship': ''}

        self.update_data(nick.lower())        

    # Metodo para obtener ID del nick de irc especificado
    def get_id(self, nick):
        return self.data[nick.lower()]['id']

    # Metodo para obtener LEVEL del nick de irc especificado
    def get_level(self, nick):
        return self.data[nick.lower()]['level']

    # Metodo para obtener STRENGTH del nick de irc especificado
    def get_strength(self, nick):
        return self.data[nick.lower()]['strength']

    # Metodo para obtener RANK POINTS del nick de irc especificado
    def get_rank_points(self, nick):
        return self.data[nick.lower()]['rank_points']

    # Metodo para obtener CITIZENSHIP del nick de irc especificado
    def get_citizenship(self, nick):
        return self.data[nick.lower()]['citizenship']

    # Metodo para obtener NICK INGAME del nick de irc especificado
    def get_nick(self, nick):
        return self.data[nick.lower()]['nick']

    # Metodo para obtener RANK NAME del nick de irc especificado
    def calculate_rank_name(self, rank_points):
        index = 0

        for k in [key for key in self.rank_required_points.keys() if self.rank_required_points[key] < rank_points]:
            if(self.rank_to_pos.index(k) > index):
                index = self.rank_to_pos.index(k)

        return self.rank_to_pos[index]

    # Metodo para calcular DAÑO del nick de irc especificado segun datos adicionales
    def calculate_damage(self, rank_points, strength, weapon_power, level, bonus):
        index = 0

        for k in [key for key in self.rank_required_points.keys() if self.rank_required_points[key] < rank_points]:
            if(self.rank_to_pos.index(k) > index):
                index = self.rank_to_pos.index(k)

        return(math.trunc(((index / 20) + 0.3) * ((strength / 10) + 40) * (1 + (weapon_power / 100)) * (1.1 if level > 99 else 1) * bonus))