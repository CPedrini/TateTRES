#-*- encoding: utf-8 -*-

from collections import OrderedDict

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

# Libreria externa, permite conexion e identificacion en Google Docs de forma transparente
import gspread

class Google():
    # Metodo constructor, seteos basicos necesarios de configuracion
    def __init__(self, channel_key, permissions_key, orders_csv, gmail_user, gmail_password):
        self.channel_key = channel_key
        self.permissions_key = permissions_key
        self.orders_csv = orders_csv

        self.gmail_user = gmail_user
        self.gmail_password = gmail_password

        self.permissions = {'~': [], '&': [], '@': [], '%': [], '+': []}
        # Data format: {'~': [], '&': [], '@': [], '%': [], '+': []}
        self.channels = []
        # Data format: [(#channel, password)]
        self.orders = OrderedDict()
        # Data format: {'region_name': {'id': 123, 'd1': 'prioridad', 'd2': 'prioridad', 'd3': 'prioridad', 'd4': 'prioridad', 'side': 'Rumania'}}
        self.channels_evento = []
        # Data format: ['#canal1', '#canal2']

    # ---------------------------------------------------------------------------------- #
    # @ PUBLIC METHODS                                                                   #
    # ---------------------------------------------------------------------------------- #

    # Devuelve lista de tuplas de canales/contraseñas
    # Si se envia el parametro True se fuerza actualizacion contra la hoja de calculo en Google Docs
    def get_channels(self, reload=False):
        if(reload == True):
            gc = gspread.login(self.gmail_user, self.gmail_password)

            sht = gc.open_by_key(self.channel_key)

            worksheet = sht.worksheet("Canales")

            rng = worksheet.get_all_records()

            self.channels = []
            self.channels_evento = []

            for x in rng:
                self.channels.append((x['channel'], x['password']))

                if(x['evento'] == 'Si'):
                    self.channels_evento.append(x['channel'])

            # DEBUG: print(self.channels)

        return self.channels
        # DEBUG:
        #return [('#FEA', '')]

    # Devuelve diccionario de listas de permisos y nicks
    # Si se envia el parametro True se fuerza actualizacion contra la hoja de calculo en Google Docs
    def get_permissions(self, reload=False):
        if(reload == True):
            gc = gspread.login(self.gmail_user, self.gmail_password)

            sht = gc.open_by_key(self.permissions_key)

            worksheet = sht.worksheet("Permisos")

            rng = worksheet.get_all_records()

            self.permissions = {'~': [], '&': [], '@': [], '%': [], '+': []}

            for x in rng:
                for y in [('Q', '~'), ('SOP', '&'), ('AOP', '@'), ('HOP', '%'), ('VOP', '+')]:
                    if (x[y[0]] != ''):
                        self.permissions[y[1]].append(x[y[0]])

            # DEBUG: print(self.permissions)

        return self.permissions

    # Devuelve lista ordenada de ordenes
    # Si se envia el parametro True se fuerza actualizacion contra la hoja de calculo en Google Docs
    def get_orders(self, reload=False):
        if(reload == True):
            self.orders = OrderedDict()

            c = urlopen(self.orders_csv)
            ordenes = c.read()
            c.close()

            ordenes = ordenes.decode('utf-8').split('\n')

            for i in range(2, 10, 1):
                row = ordenes[i].split(',')

                if(row[1] == ''):
                    break

                try:
                    id = int(row[2][row[2].rfind('/')+1:])
                except:
                    pass

                self.orders[row[1]] = {'id': id, 'd1': row[3], 'd2': row[4], 'd3': row[5], 'd4': row[6], 'side': row[7]}


        return self.orders

    # Devuelve lista de canales con evento activado
    # Si se envia el parametro True se fuerza actualizacion contra la hoja de calculo en Google Docs
    def get_channels_evento(self, reload=False):
        if(reload == True):
            self.get_channels(True)

        return self.channels_evento
    

    # Actualiza datos internos de permisos y los vuelca en la hoja de calculo de Google Docs correspondiente
    def set_permissions(self, permissions):
        self.permissions = permissions

        gc = gspread.login(self.gmail_user, self.gmail_password)

        sht = gc.open_by_key(self.permissions_key)

        worksheet = sht.worksheet("Permisos")

        for c in [('A', '~'), ('B', '&'), ('C', '@'), ('D', '%'), ('E', '+')]:
            rng = worksheet.range('%s2:%s50' % (c[0],c[0]))

            for x in rng:
                x.value = ''

            worksheet.update_cells(rng)

            if len(permissions[c[1]]) > 0:
                rng = worksheet.range('%s2:%s%d' % (c[0],c[0],1 + len(permissions[c[1]])))

                for x, y in zip(rng, permissions[c[1]]):
                    x.value = y

                worksheet.update_cells(rng)

    # Actualiza datos internos de canales y los vuelca en la hoja de calculo de Google Docs correspondiente
    def set_channels(self, channels):
        self.channels = channels

        gc = gspread.login(self.gmail_user, self.gmail_password)

        sht = gc.open_by_key(self.channel_key)

        worksheet = sht.worksheet("Canales")

        rng = worksheet.range('A2:B70')

        for x in rng:
            x.value = ''

        worksheet.update_cells(rng)

        rng = worksheet.range('A2:B%d' % (1 + len(channels)))

        for val, cell in zip(list(sum(channels, ())), rng):
            cell.value = val
        
        worksheet.update_cells(rng)

    def set_channels_events(self, channels_evento):
        self.channels_evento = channels_evento

        gc = gspread.login(self.gmail_user, self.gmail_password)

        sht = gc.open_by_key(self.channel_key)

        worksheet = sht.worksheet("Canales")

        rng = worksheet.range('A2:A70')

        for cell in rng:
            if cell.value in channels_evento:
                worksheet.update_cell(cell.row, 4, 'Si')
            else:
                worksheet.update_cell(cell.row, 4, '')

