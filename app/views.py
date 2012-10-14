from app.models import Player
from django.http import HttpResponse

def index(request):
	output = '<h1>Minnesota ballers</h1>'
	output += '<ul>'
	minny = Player.objects.filter(team = "Minnesota Men's Basketball")
	for player in minny:
		output += '<li>' + player.name + ' | ' + player.town + '</li>'
	output += '</ul>'
	return HttpResponse(output)