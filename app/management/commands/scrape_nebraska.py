from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
from app.models import Player

import django
import html5lib
import json
import requests

class Command(BaseCommand):
	
	def handle(self, *args, **kwargs):
		base_url = 'http://www.huskers.com/SportSelect.dbml?spid=24&spsid=23&db_oem_id=100'
		self.scrape_team(base_url)

	def scrape_team(self, home_url):
		player_payload = []

		request = requests.get(home_url)
		soup = BeautifulSoup(request.content)

		team = {'team': "Nebraska Men's Basketball"}
		#player_payload.append({'team': team_title[0]})

		table = soup.select('table')[4]
		rows = table.select('tr')[14:]
		
		for row in rows:
			player_data = {}

			cells = row.select('td')

			#roster formats with position
			#if len(cells) >= 8:

			player_data.update(team)

			number = {'number': cells[0].get_text().split()[0].strip('\\u00a0\\u00a')}
			player_data.update(number)

			name_list = cells[1].get_text().split()
			backwards_name = ''
			for word in name_list:
				backwards_name = backwards_name + word + ' '
			self.process_name(backwards_name, player_data)

			position = {'position': cells[2].get_text().split()[0]} 
			player_data.update(position)

			#TO DO: HEIGHT WEIGHT CHALLENGING TO SCRAPE
			#height = {'height': cells[-4].get_text()}
			#player_data.update(height)

			#some sports don't list weight
			#if len(cells) != 9:
			#	weight = {'weight': cells[-3].get_text()}
			#	player_data.update(weight)

			year = {'year': cells[-2].get_text().split()[0]}
			player_data.update(year)

			town_school = cells[-1].get_text()
			self.process_town_school(town_school, player_data)
			self.save_player(player_data)
			player_payload.append(player_data)
		print json.dumps(player_payload, sort_keys=True, indent=4)
		return player_payload

	def process_name(self, backwards_name, player_data):
		try:
			last_first = backwards_name.split(',')
			last_name = last_first[0]
			first_name = last_first[1]
			#cut off lead space
			first_name = first_name[1:]
			name = {'name': first_name + last_name}
			player_data.update(name)

		except IndexError:
			player_data.update({'name': backwards_name})

		return player_data

	def process_town_school(self, town_school, player_data):

		try:
			split = town_school.split('(')
			town = split[0]
			town = town.split()
			location = ''
			for place in town:
				location = location + ' ' + place
			#cut off extra space
			location = location[1:]

			school = split[1]
			school = school.split()
			the_school = ''
			#lp stands for learning place
			for lp in school:
				the_school = the_school + lp + ' '
			#cut off the extra space and ')'
			the_school = the_school[:-2]

		#some players only have a hometown listed
		except IndexError:
			town = town_school
			school = ''

		player_data.update({'town': location})
		player_data.update({'school': the_school})

		return player_data

	def save_player(self, player_data):
		player_name = player_data['name']
		player_school = player_data['school']
		player_town = player_data['town']
		player_team = player_data['team']

		try:
			player = Player.objects.get(name=player_name, school=player_school, town=player_town, team = player_team)
			print 'EXISTING PLAYER FOUND!!!'
		except Player.DoesNotExist:
			player = Player(**player_data)
			player.save()