from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
from app.models import Player

import django
import html5lib
import json
import requests

class Command(BaseCommand):
	
	def handle(self, *args, **kwargs):
		base_url = 'http://www.mgoblue.com/sports/m-baskbl/mtt/mich-m-baskbl-mtt.html'
		self.scrape_team(base_url)

	def scrape_team(self, home_url):
		player_payload = []

		request = requests.get(home_url)
		soup = BeautifulSoup(request.content)

		team = {'team': "Michigan Men's Basketball"}
		#player_payload.append({'team': team_title[0]})

		table = soup.select('#sortable_roster')[0]
		rows = table.select('tr')[1:]

		for row in rows:
			player_data = {}

			cells = row.select('td')

			#roster formats with position
			if len(cells) >= 8:

				player_data.update(team)

				number = {'number': cells[0].get_text()}
				player_data.update(number)

				backwards_name = cells[2].get_text()
				self.process_name(backwards_name, player_data)

				position = {'position': cells[-4].get_text()} 
				player_data.update(position)

				#TO DO: HEIGHT WEIGHT CHALLENGING TO SCRAPE
				#height = {'height': cells[-4].get_text()}
				#player_data.update(height)

				#some sports don't list weight
				#if len(cells) != 9:
				#	weight = {'weight': cells[-3].get_text()}
				#	player_data.update(weight)

				year = {'year': cells[-2].get_text()}
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
			first_name = last_first[1][1:]
			name = {'name': first_name + ' '+ last_name}
			player_data.update(name)

		except IndexError:
			player_data.update({'name': backwards_name})

		return player_data

	def process_town_school(self, town_school, player_data):

		try:
			split = town_school.split('(')
			#crop parentheses
			school = split[1][:-1]
			town = split[0][:-1]
		#some players only have a hometown listed
		except IndexError:
			town = town_school
			school = ''

		player_data.update({'town': town})
		player_data.update({'school': school})

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