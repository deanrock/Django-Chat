from django.db import models

# Create your models here.
class Chatroom(models.Model):
	name = models.CharField(max_length=250)
	started_by = models.CharField(max_length=250, null=True)
	is_private = models.BooleanField(default=False)
	
class Message(models.Model):
	chatroom = models.ForeignKey(Chatroom, null=False)
	nickname = models.CharField(max_length=250, null=False)
	datetime = models.DateTimeField(auto_now_add=True)
	message = models.TextField()
	color = models.CharField(max_length=6, null=True)

class NicknameChatroom(models.Model):
	chatroom = models.ForeignKey(Chatroom, null=False, related_name='nicknames')
	nickname = models.CharField(max_length=250, null=False)
	ping = models.DateTimeField()

class File(models.Model):
	nickname = models.CharField(max_length=250, null=False)
	filename = models.CharField(max_length=250, null=False)
	path = models.CharField(max_length=250, null=False)