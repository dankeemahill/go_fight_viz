from django.contrib.gis.db import models

class Player(models.Model):
	name = models.CharField(max_length=255, blank=True, null=True)
	number = models.IntegerField(blank=True, null=True)
	position = models.CharField(max_length=255, blank=True, null=True)
	school = models.CharField(max_length=255, blank=True, null=True)
	town = models.CharField(max_length=255, blank=True, null=True)
	year = models.CharField(max_length=50, blank=True, null=True)
	team = models.CharField(max_length=255, blank=True, null=True)