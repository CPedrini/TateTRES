#-*- encoding: utf-8 -*-

class Watcher():
    # Metodo constructor, seteos basicos necesarios de configuracion
	def __init__(self):
		self.initials = {'arg': 'Argentina', 'bo': 'Bolivia', 'pe': 'Peru'}
		self.regions = [{'enabled': True, 'region_id': 1, 'country_name': 'Argentina', 'country_initial': 'arg', 'region_name': 'Region 1', 'region_initial': 'r1','supporters': []}]
		
		# TODO: Iniciar threads para de forma paralela monitorear las regiones

    # ---------------------------------------------------------------------------------- #
    # @ PUBLIC METHODS                                                                   #
    # ---------------------------------------------------------------------------------- #

    # Metodo para devolver lista de diccionarios con datos de las regiones del pais especificado
	def get_by_country_name(self, country):
		rw = [x for x in self.regions if x['country_name'].lower() == country.lower()]

		if(len(rw) > 0):
			return rw

		return False

	# Metodo para devolver nombre del pais segun la inicial especificada
	def get_country_name(self, initial):
		if(initial.lower() in self.initials.keys()):
			return self.initials[initial.lower()]

		return False

	# Metodo para devolver diccionario de la region correspondiente a la inicial de region especificada
	def get_by_region_initial(self, region_initial):
		for x in self.regions:
			if x['region_initial'].lower() == region_initial.lower():
				return x

		return False