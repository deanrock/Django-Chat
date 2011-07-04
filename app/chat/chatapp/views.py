# coding=utf8
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
import string, random, os, sys
from chatapp.models import Chatroom, Message, NicknameChatroom, File
from django.utils import simplejson
import datetime, time
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.http import Http404

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def change_nick(request, nickname):
	if len(nickname) <= 3:
		return False
	
	if nickname == 'system':
		return False
	
	try:
		NicknameChatroom.objects.get(nickname=nickname)
		return False
	except:
		pass
	
	request.session['nickname'] = nickname
	return True

def index(request):
	if not 'nickname' in request.session:
		return HttpResponseRedirect('/nickname')
	
	return render_to_response('chat.html', {}, context_instance=RequestContext(request))

def ajax(request):
	if not 'nickname' in request.session:
		return HttpResponseRedirect('/nickname')
	
	data = simplejson.loads(request.POST['data'])
	

	chatrooms = data['chatrooms']
	chatrooms2 = {}
	x=0
	#get rooms user is currently in
	nrooms = NicknameChatroom.objects.filter(nickname=request.session['nickname'])
	room_messages=[]
	for nroom in nrooms:
		#get messages from last id,
		#or get last id if room_id isn't in request
		
		room = Chatroom.objects.get(id=nroom.chatroom.id)
		
		if str(room.id) in chatrooms:
			x=x+1
			#get message from last id
			messages = Message.objects.filter(chatroom=room, id__gt = chatrooms[str(room.id)]['last_message_id']).order_by('id')
			
			#del chatrooms[str(room.id)]
			
			if len(messages) > 0:
			
				last_id = 0
				
				for message in messages:
					last_id = message.id
					room_messages.append({'id': message.id,
									 'nickname': message.nickname,
									 'color': message.color,
									 'time': str(message.datetime.hour)+':'+str(message.datetime.minute),
									 'message': message.message,
									 'chatroom': room.id})
				
				chatrooms2[str(room.id)] = {'name': room.name, 'id': room.id, 'last_message_id': last_id}
			else:
				chatrooms2[str(room.id)] = {'name': room.name, 'id': room.id, 'last_message_id': chatrooms[str(room.id)]['last_message_id']}
			
			
		else:
			
			messages = Message.objects.filter(chatroom=room).order_by('-id')[:1]
			
			if len(messages) > 0:
				msg = messages[0].id
			else:
				msg = 0
			
			chatrooms2[str(room.id)] = {'name': room.name, 'id': room.id, 'last_message_id': msg}
			
	r = { 'messages': room_messages, 'chatrooms': chatrooms2, 'x':x }
	
	return HttpResponse(simplejson.dumps(r))

def sidemenu(request):
	chatroom = request.POST['chatroom']
	
	if is_number(chatroom):
		chatroom = float(chatroom)
		
		if chatroom == 0:
			rooms = Chatroom.objects.filter(is_private=False).order_by('name')
			
			json_rooms = []
			
			for room in rooms:
				json_rooms.append({'name':room.name})
			
			return HttpResponse(simplejson.dumps({'rooms':json_rooms}))
		else:
			try:
				room = Chatroom.objects.get(id=chatroom)
				
				nicknames = room.nicknames.all().order_by('nickname')
				
				json_nicknames = []
			
				for nickname in nicknames:
					json_nicknames.append({'name':nickname.nickname})
					
				return HttpResponse(simplejson.dumps({'nicknames':json_nicknames}))
			except:
				pass
	else:
		return HttpResponse('error')
	
	

def message(request):
	if not 'nickname' in request.session:
		return HttpResponseRedirect('/nickname')
		
	chatroom = request.POST['chatroom']
	msg = request.POST['msg']
	
	r = {}
	
	if msg[0:7] == '/join #':
		#join chatroom
	
		name = msg[6:]
		
		try:
			room = Chatroom.objects.get(name=name)
			
			if room.is_private == True:
				return HttpResponse(simplejson.dumps({'message':'error'}))
			
			nc = NicknameChatroom(nickname = request.session['nickname'], chatroom = room, ping = datetime.datetime.now())
			nc.save()
		except:
			room = Chatroom(name=name)
			room.save()
			
			nc = NicknameChatroom(nickname = request.session['nickname'], chatroom = room, ping = datetime.datetime.now())
			nc.save()
		
		
		
	elif msg[0:6] == '/leave':
		#leave
		
		if chatroom != '0':
			try:
				room = Chatroom.objects.get(id=chatroom)
				
				nc = NicknameChatroom.objects.filter(chatroom=room,nickname=request.session['nickname'])
				
				nc.delete()
			except:
				r['message'] = 'Error'
			
		else:
			r['message'] = 'You are not in a chatroom!'
		
	elif msg[0:4] == "/msg":
		#msg
		
		nick = msg[5:]
		
		name = request.session['nickname']+'_' + nick
		
		
		room = Chatroom(name=name,is_private=True)
		room.save()
		
		nc = NicknameChatroom(nickname = request.session['nickname'], chatroom = room, ping = datetime.datetime.now())
		nc.save()
		
		nc = NicknameChatroom(nickname = nick, chatroom = room, ping = datetime.datetime.now())
		nc.save()
	
	elif msg[0:5] == '/nick':
		#change nick
		if change_nick(request, msg[6:]):
			r['message'] = 'Your nickname was successfully changed.'
		else:
			r['message'] = 'Selected nickname is too short or already in use'
	
	else:
		#it's a message
		if chatroom != '0':
			try:
				room = Chatroom.objects.get(id=chatroom)
				
				try:
					nc = NicknameChatroom.objects.get(chatroom=room,nickname=request.session['nickname'])
					
					#post message
					m = Message(chatroom=room,nickname=request.session['nickname'], message=msg)
					m.save()
				except:
					r['message'] = 'Wrong chatroom id!'
			except:
				r['message'] = 'Message couldn\'t be send!'
			
		else:
			r['message'] = 'You are not in a chatroom!'
	
	return HttpResponse(simplejson.dumps(r))

def nickname(request):
	if 'nickname' in request.session:
		return HttpResponseRedirect('/')
	
	error = ''
	
	if 'nickname' in request.POST:
		#change nick
		if change_nick(request, request.POST['nickname']):
			return HttpResponseRedirect('/')
		else:
			error = 'Selected nickname is too short or already in use'
		
	return render_to_response('nickname.html', {'error': error}, context_instance=RequestContext(request))

def download(request, id):
	try:
		f = File.objects.get(id=id, is_private=False)
		wrapper = FileWrapper(file(settings.FILES_PATH + '/' + str(f.id)))
		
		response = HttpResponse(wrapper, mimetype='application/force-download')
		response['Content-Disposition'] = 'attachment; filename=%s' % f.filename
		return response
	except:
		pass		
	
	return HttpResponse('File doesn\'t exist!')

def upload(request):
	if request.method == 'POST':
		
		try:
			i = File(filename = request.FILES['file'].name,
					nickname = request.session['nickname'])
			
			i.save() #save it to get id
			
			destination = open(settings.FILES_PATH + '/' + str(i.id), 'wb+')
			for chunk in request.FILES['file'].chunks():
				destination.write(chunk)
			
			destination.close()
			
			#send link to the file to appropriate chatroom
			c=Chatroom.objects.get(id=request.GET['id'],is_private=False)
			
			m=Message(chatroom=c,
					  nickname='system',
					  message=request.session['nickname'] + ' uploaded file: '+settings.DOMAIN+'/download/'+str(i.id))
			m.save()
		except:
			try:
				if len(code) > 0:
					os.remove(settings.FILES_PATH + '/' + i.id)
			except:
				#there might be a problem with removing folder/file
				None
			
			#try removing entry from DB
			try:
				i.delete()
			except:
				#entry not found, apparently we didn't create one, therefore we don't need to remove folder/file
				None
		
		return HttpResponse('File successfully uploaded!')
	else:
		if 'id' in request.GET:
			return render_to_response('upload.html', {'id': request.GET['id']}, context_instance=RequestContext(request))
