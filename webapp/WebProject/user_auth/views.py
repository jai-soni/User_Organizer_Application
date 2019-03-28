# importing Django libraries
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from uuid import UUID
import json
import re
import base64
import time
import datetime
from .models import *
import sys
import boto3
from django.conf import settings
import logging
from django_statsd.clients import statsd
from boto3.dynamodb.conditions import Key, Attr

# #--------------------------------------------------------------------------------
# Define Logger
# --------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
if settings.DEBUG == True:
	logger.setLevel("DEBUG")
else:
	logger.setLevel("INFO")
#--------------------------------------------------------------------------------
# Function definitions for reading, saving, updating and deleting
# --------------------------------------------------------------------------------
def save_attachments(file_to_upload,filename,	note):
	logger.debug("settings.PROFILE : %s", settings.PROFILE)
	if (settings.PROFILE  == "dev"):
		attachment = save_attachment_to_s3(file_to_upload=file_to_upload,filename=filename,acl="public-read",note=note)
	else:
		attachment = save_attachment_to_local(file_to_upload,filename,note)
	return attachment

def get_attachment_details(attachment):
	note_attachment = {}
	note_attachment['id'] = attachment.id
	note_attachment['url'] = attachment.url
	return note_attachment

def get_note_details(note):
	note_details = {}
	note_details['id'] = note.id
	note_details['title'] = note.title
	note_details['content'] = note.content
	note_details['created_on'] = note.created_on
	note_details['last_updated_on'] = note.last_updated_on
	attachment_list = []
	attachments = Attachment.objects.filter(note=note.id)
	if (attachments):
		for attachment in attachments:
			attachment_list.append(get_attachment_details(attachment))
		note_details['attachments'] = attachment_list
	return note_details

def update_attachment(file_to_upload,filename,note,attachment):
	if (settings.PROFILE  == "dev"):
		new_attachment = update_attachment_to_s3(file_to_upload=file_to_upload,filename=filename,acl="public-read",note=note,attachment=attachment)
	else:
		new_attachment = update_attachment_to_local(file_to_upload,filename,note,attachment)
	return new_attachment

def delete_attachment(attachment):
	if (settings.PROFILE  == "dev"):
		response = delete_attachment_from_s3(attachment,acl="public-read")
	else:
		response = delete_attachment_from_local(attachment)
		return response


#--------------------------------------------------------------------------------
# Function definitions for CRUD on local - default profile
# --------------------------------------------------------------------------------
def save_attachment_to_local(file_to_upload,filename,note):
	url = os.path.join(settings.MEDIA_ROOT, filename)
	meta={}
	meta['note_id'] = str(note.id)
	meta['user_id'] = str(note.user)
	meta['filename'] = str(filename)
	metadata = str(meta)
	attachment = Attachment(url = url, note = note,metadata = metadata)
	attachment.save()
	filename, file_extension = os.path.splitext(filename)
	filename = str(attachment.id) + file_extension
	logger.info("Saving attachment to local : %s", filename)
	attachment.url = settings.MEDIA_URL+filename
	attachment.save()
	path = default_storage.save(filename, ContentFile(file_to_upload.read()))
	tmp_file = os.path.join(settings.MEDIA_ROOT, path)
	return attachment

def delete_attachment_from_local(attachment): 
	attachment_url = attachment.url
	filename=attachment_url[13:]
	logger.info("Deleting attachment from local : %s", filename)
	path = os.path.join(settings.MEDIA_ROOT, filename)
	default_storage.delete(path) 
	attachment.delete()
	return JsonResponse({'message': 'Attachment deleted from Local'}, status=200)

def update_attachment_to_local(file_to_upload,filename,note,attachment):
	logger.info("Updating attachment in local : %s", filename)
	delete_attachment_from_local(attachment)
	new_attachment = save_attachment_to_local(file_to_upload,filename,note)	
	return new_attachment

#--------------------------------------------------------------------------------
# Function definitions for AWS S3 - dev profile
# -------------------------------------------------------------------------------

def save_attachment_to_s3(file_to_upload,filename,acl,note):
#Get AWS keys from local aws_credentials file
	logger.info("Saving attachment to S3")
	session = boto3.Session()
	bucketName = settings.S3_BUCKETNAME
	url = "dummy"
	attachment = Attachment(url = url, note = note)
	attachment.save()	
	orignal_filename = filename
	filename, file_extension = os.path.splitext(filename)
	filename = str(attachment.id) + file_extension
	attachment.url = 'https://s3.amazonaws.com/'+bucketName+'/'+filename
	attachment.save()
	try:
		meta = {}
		meta['note_id'] = str(note.id)
		meta['user_id'] = str(note.user)
		meta['filename'] = str(orignal_filename)
		s3 = session.client('s3')
		s3.upload_fileobj(
			file_to_upload,
			bucketName,
			filename,
			ExtraArgs={
				"ACL": acl,
				"Metadata": meta
			}
		)
	except Exception as e:
		# This is a catch all exception, edit this part to fit your needs.
		logger.error("Something Happened: %s", e)
		return e

	logger.info("s3 attachment deleted : %s", filename)
	return attachment

def delete_attachment_from_s3(attachment,acl):
	attachment_url=attachment.url
	extension=os.path.splitext(attachment_url)[1]
	filename=str(attachment.id)+extension
	session = boto3.Session()
	bucketName = settings.S3_BUCKETNAME
	try:
		s3 = boto3.resource('s3')
		object=s3.Bucket(bucketName).Object(filename)
		object.delete()
		attachment.delete()
		logger.info("s3 attachment deleted : %s",filename)
		return JsonResponse({'message':'Note updated!'}, status=204)
	except Exception as e:
		logger.error("Something Happened: %s", e)
		return e

def update_attachment_to_s3(file_to_upload,filename,acl,note, attachment):
	#Get AWS keys from local aws_credentials file
	logger.info("Updating attachment in local : %s", filename)
	delete_attachment(attachment)
	new_attachment = save_attachments(file_to_upload,filename,note)
	return new_attachment

#--------------------------------------------------------------------------------
# Function definitions
# --------------------------------------------------------------------------------

# Verify signed in user
def validateSignin(meta):
	if 'HTTP_AUTHORIZATION' in meta:
		auth = meta['HTTP_AUTHORIZATION'].split()
		if len(auth) == 2:
			if auth[0].lower() == "basic":
				authstring = base64.b64decode(auth[1]).decode("utf-8")
				username, password = authstring.split(':', 1)
				if not username and not password:
					return JsonResponse({'message': 'Error : User not logged, Please provide credentials'}, status=401)
				user = authenticate(username=username, password=password)
				if user is not None:
					return user
	else:
		return False

# Validating passwords
def validatePassword(password):
	message = ""
	specialCharacters = ['$', '#', '@', '!', '*', '_', '-', '&', '^', '+', '%']
	if (len(password) == 0):
		return JsonResponse({'message': 'Password can\'t be blank'})

	if (8 > len(password) or len(password) >= 16):
		message += 'The password must be between 8 and 16 characters. : '
	password_strength = {}

	if not re.search(r'[A-Z]', password):
		message += "Password must contain one upppercase : "
	if not re.search(r'[a-z]', password):
		message += "Password must contain one lowercase : "

	if not re.search(r'[0-9]', password):
		message += "Password must contain one numeric : "

	if not any(c in specialCharacters for c in password):
		message += "Password must contain one special character : "

	if (len(message) > 0):
		return message
	else:
		return True


# Validing username
def validateUserName(username):
	valid = re.search(r'\w+[.|\w]\w+@\w+[.]\w+[.|\w+]\w+', username)
	# valid = re.search(r'^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$', username)
	if valid:
		return True
	return "* please enter valid email ID *"

def is_valid_uuid(uuid_to_test, version=4):
	"""
	Check if uuid_to_test is a valid UUID.

	Parameters
	----------
	uuid_to_test : str
	version : {1, 2, 3, 4}

	Returns
	-------
	`True` if uuid_to_test is a valid UUID, otherwise `False`.

	Examples
	--------
	>>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
	True
	>>> is_valid_uuid('c9bf9e58')
	False
	"""
	try:
		uuid_obj = UUID(uuid_to_test, version=version)
	except:
		return False

	return str(uuid_obj) == uuid_to_test

# --------------------------------------------------------------------------------
# Views definitions
# --------------------------------------------------------------------------------


@csrf_exempt
def registerPage(request):
	statsd.incr('api.registerPage')
	# check if method is post
	if request.method == 'POST':
		try:
			username = request.POST.get('username')
			password = request.POST.get('password')
			if (username == "" or password == "" or username == None or password == None):
				logger.debug("Username or password is empty")
				return JsonResponse({'message': 'Username or password cant be empty'})
			username_status = validateUserName(username)
			password_status = validatePassword(password)
			if (username_status == True and password_status == True):
				email = username
				if not User.objects.filter(username=username).exists():
					user = User.objects.create_user(username, email, password)
					user.is_staff = True
					user.save()
					logger.info("User created")
					return JsonResponse({"message": " : User created"})
				else:
					logger.info("User already exists")
					return JsonResponse({'Error': "User already exists"})

			else:
				if (password_status == True):
					logger.debug("Registration Error: %s",username_status)
					return JsonResponse({"message": username_status})
				elif (username_status == True):
					logger.debug("Registration Error: %s", password_status)
					return JsonResponse({"message": password_status})
				else:
					logger.debug("Registration Error: %s %s", username_status, password_status)
					return JsonResponse({'message': username_status + " " + password_status})
		except Exception as e:
			logger.error("Something Happened: %s", e)
			return JsonResponse({'Error': 'Please use a post method with parameters username and password to create user'})
	# If all the cases fail then return error message
	return JsonResponse({'Error': 'Please use a post method with parameters username and password to create user'})


@csrf_exempt
def signin(request):
	statsd.incr('api.signin')
	# statsd.incr('test2')

	# check if method is get
	if request.method == 'GET':
		if 'HTTP_AUTHORIZATION' in request.META:
			auth = request.META['HTTP_AUTHORIZATION'].split()
			if len(auth) == 2:
				if auth[0].lower() == "basic":
					authstring = base64.b64decode(auth[1]).decode("utf-8")
					username, password = authstring.split(':', 1)
					if not username and not password:
						return JsonResponse({'message': 'Error : User not logged, Please provide credentials'}, status=401)
					user = authenticate(username=username, password=password)
					if user is not None:
						current_time = time.ctime()
						return JsonResponse({"current time": current_time})
		# otherwise ask for authentification
		return JsonResponse({'message': 'Error : Incorrect user details entered'}, status=401)
	else:
		return JsonResponse({'Error': 'Please use a get method with user credentials'})

@csrf_exempt
def createOrGetNotes(request):
	statsd.incr('api.note')
	try:
		logger.debug("Request Method : %s /note", request.method)
		# Post method to create new notes for authorized user
		if request.method == 'POST':
			statsd.incr('api.note.POST')
			if (request.POST):
				try:
					title = request.POST.get('title')
					content = request.POST.get('content')
					time_now = datetime.datetime.now()
					user = validateSignin(request.META)
					if (user):
						note = NotesModel(title=title, content=content, created_on=time_now, last_updated_on=time_now,
										  user=user)
						note.save()
						#If attachment is sent as POST method while creating note
						if (request.FILES):
							logger.info("Attachments added")
							file = request.FILES['attachment']
							save_attachments(file_to_upload=file, filename= file._get_name(), note=note)
						else:
							logger.info("No Attachment added")
						message = get_note_details(note)
						logger.info("Note Saved")
						statsd.incr('api.note.POST.200')
						return JsonResponse(message, status=200)
					else:
						logger.debug("Incorrect user details")
						statsd.incr('api.note.POST.401')
						return JsonResponse({'message': 'Error : User not authorized'}, status=401)
				except:
					logger.debug("Incorrect request")
					statsd.incr('api.note.POST.400')
					return JsonResponse({'message': 'Error : provide title(req), content(req) and attachment(optional) in form-data'}, status=400)
		# Get method to retrive all notes for authorized user
		elif request.method == 'GET':
			statsd.incr('api.note.GET')
			user = validateSignin(request.META)
			if (user):
				notes = NotesModel.objects.filter(user=user)
				if (notes.exists()):
					message_list = []
					for note in notes:
						attachment_list = []
						message = get_note_details(note)
						message_list.append(message)
					logger.info("Notes displayed")
					statsd.incr('api.note.GET.200')
					return JsonResponse(message_list, status=200, safe=False)
				else:
					logger.info("Notes Empty")
					statsd.incr('api.note.GET.204')
					return JsonResponse({'message': 'Error : Note List Empty'}, status=204)
			logger.debug("Incorrect user details")
			statsd.incr('api.note.GET.401')
			return JsonResponse({'message': 'Error : Incorrect user details'}, status=401)
		logger.debug("Incorrect request")
		statsd.incr('api.note.GET.400')
		return JsonResponse({'message': 'Error : Incorrect Request'}, status=400)
	except Exception as e:
		logger.error("Something Happened: %s", e)
		statsd.incr('api.note.GET.400')
		return JsonResponse({'Error': 'Bad Request'}, status=400)

@csrf_exempt
def noteFromId(request, note_id=""):
	statsd.incr('api.note_id')
	try:
		logger.debug("Request Method : %s /note/<note_id>",request.method)
		if request.method == 'GET':
			statsd.incr('api.note_id')
			user = validateSignin(request.META)
			if (is_valid_uuid(note_id)):
				if (user):
					try:
						note = NotesModel.objects.get(pk=note_id)
						if (note.user==user):
							message = get_note_details(note)
							logger.info("Notes displayed")
							statsd.incr('api.note_id.GET.200')
							return JsonResponse(message, status=200)
						else:
							logger.debug("Notes not found")
							statsd.incr('api.note_id.GET.400')
							return JsonResponse({'message': 'Error : Note not found'}, status=404)
					except:
						logger.debug("Note not found")
						statsd.incr('api.note_id.GET.404')
						return JsonResponse({'message': 'Error : Note not found'}, status=404)
				else:
					logger.debug("Incorrect user details")
					statsd.incr('api.note_id.GET.401')
					return JsonResponse({'message': 'Error : Incorrect user details'}, status=401)
			else:
				logger.debug("Invalid Note ID")
				statsd.incr('api.note_id.GET.400')
				return JsonResponse({'message': 'Error : Invalid Note ID'}, status=400)
		#update
		elif request.method=='PUT':
			statsd.incr('api.note_id.PUT')
			user = validateSignin(request.META)
			if (is_valid_uuid(note_id)):
				if(user):
					try:
						note = NotesModel.objects.get(pk=note_id)
						if(note.user==user):
							try:
								note.title = request.PUT.get('title')
								note.content = request.PUT.get('content')
								note.last_updated_on = datetime.datetime.now()	
								statsd.incr('api.note_id.PUT.200')
								note.save()
							except:
								logger.debug("Invalid note id")
								statsd.incr('api.note_id.PUT.400')
								return JsonResponse({'message': 'Error : Invalid note id'}, status=400)		
							#If attachment is sent as PUT method while updating note
							try:
								if (request.FILES):
									file = request.FILES['attachment']
									save_attachments(file_to_upload=file, filename= file._get_name(), note=note)
								else:
									logger.info("No Attachment added")
							except:
								logger.debug("Invalid attachment")
								statsd.incr('api.note_id.PUT.400')
								return JsonResponse({'message': 'Error : Invalid attachment'}, status=400)
							logger.info("Note updated")
							message = get_note_details(note)
							statsd.incr('api.note_id.PUT.204')
							return JsonResponse(message, status=204)
						else:
							logger.debug("Invalid note id")
							statsd.incr('api.note_id.PUT.401')
							return JsonResponse({'message': 'Error : Invalid note id'}, status=401)
					except:
						logger.debug("Invalid note id")
						statsd.incr('api.note_id.PUT.401')
						return JsonResponse({'message': 'Error : Invalid note id'}, status=401)
				else:
					logger.debug("Incorrect user details")
					statsd.incr('api.note_id.PUT.400')
					return JsonResponse({'message': 'Error : Incorrect user details'}, status=400)
			else:
				logger.debug("Invalid note id")
				statsd.incr('api.note_id.PUT.400')
				return JsonResponse({'message': 'Error : Invalid note id'}, status=401)
		#delete
		elif request.method == 'DELETE':
			statsd.incr('api.note_id.DELETE')
			user = validateSignin(request.META)
			if (user):
				try:
					note = NotesModel.objects.get(pk=note_id)
				except:
					logger.debug("Invalid note id")
					statsd.incr('api.note_id.DELETE.400')
					return JsonResponse({'Error': 'Invalid note ID'}, status=400)
				if(note):
					if(user == note.user):
						##delete attachments if any
						attachments = Attachment.objects.filter(note=note)
						if (attachments):
							for attachment in attachments:
								delete_attachment(attachment)
						note.delete()
						logger.info("Note Deleted")
						statsd.incr('api.note_id.DELETE.204')
						return JsonResponse({'message':'Note Deleted!'}, status=204)
					else:
						logger.debug("Invalid note id")
						statsd.incr('api.note_id.DELETE.400')
						return JsonResponse({'message': 'Error : Invalid Note ID'}, status=400)
			else:
				logger.debug("Incorrect user details")
				statsd.incr('api.note_id.DELETE.401')
				return JsonResponse({'message': 'Error : Incorrect user details'}, status=401)
	except Exception as e:
		logger.error("Something Happened: %s", e)
		statsd.incr('api.note_id.DELETE.400')
		return JsonResponse({'Error': 'Bad Request'}, status=400)

@csrf_exempt
def addAttachmentToNotes(request,note_id=""):
	statsd.incr('api.note_attachment')
	try:
		logger.debug("Request Method : %s /note/<note_id>/attachments", request.method)
		# Post method to create new notes for authorized user
		if request.method == 'POST':
			statsd.incr('api.note_attachment.POST')
			if (request.FILES):
				user = validateSignin(request.META)
				if(user):
					if(is_valid_uuid(note_id)):
						try:
							note = NotesModel.objects.get(pk=note_id)
						except:
							logger.debug("Invalid note id")
							statsd.incr('api.note_attachment.POST.400')
							return JsonResponse({'Error': 'Invalid note ID'}, status=400)
					else:
						logger.debug("Invalid note id")
						statsd.incr('api.note_attachment.POST.400')
						return JsonResponse({'Error': 'Invalid note ID'}, status=400)
					if(note.user==user):
						file = request.FILES['attachment']
						attachment = save_attachments(file_to_upload=file, filename= file._get_name(), note=note)
						note.last_updated_on = datetime.datetime.now()	
						note.save()
						message = get_attachment_details(attachment)
						statsd.incr('api.note_attachment.POST.200')
						return JsonResponse(message, status=200)
					else:
						logger.debug("Incorrect user details")
						statsd.incr('api.note_attachment.POST.401')
						return JsonResponse({'message': 'Error : Invalid User Credentials'}, status=401)
				else:
					logger.debug("Incorrect user details")
					statsd.incr('api.note_attachment.POST.401')
					return JsonResponse({'message': 'Error : Invalid User Credentials'}, status=401)
			else:
				logger.debug("No Files Attached")
				statsd.incr('api.note_attachment.POST.400')
				return JsonResponse({'message': 'Error : Files not selected'}, status=400)

		# GET method to create new notes for authorized user
		if request.method == 'GET':
			user = validateSignin(request.META)
			if(user):
				if(is_valid_uuid(note_id)):
					try:
						note = NotesModel.objects.get(pk=note_id)
					except:
						logger.debug("Invalid note id")
						statsd.incr('api.note_attachment.GET.400')
						return JsonResponse({'Error': 'Invalid note ID'}, status=400)
				else:
					logger.debug("Invalid note id")
					statsd.incr('api.note_attachment.GET.400')
					return JsonResponse({'Error': 'Invalid note ID'}, status=400)
				if(note.user==user):
					message = {}
					attachment_list = []
					attachments = Attachment.objects.filter(note=note.id)
					if (attachments.exists()):
						for attachment in attachments:
							attachment_list.append(get_attachment_details(attachment))
						message['attachments'] = attachment_list
						logger.info("Attachments added")
						statsd.incr('api.note_attachment.GET.200')
						return JsonResponse(message, status=200)
					else:
						logger.debug("No attachments added to note")
						statsd.incr('api.note_attachment.GET.200')
						return JsonResponse({'message': 'No Attachments added to note'}, status=200)
				else:
					logger.debug("Incorrect user details")
					statsd.incr('api.note_attachment.GET.401')
					return JsonResponse({'message': 'Error : Invalid User Credentials'}, status=401)
			else:
				logger.debug("Incorrect user details")
				statsd.incr('api.note_attachment.GET.401')
				return JsonResponse({'message': 'Error : Invalid User Credentials'}, status=401)
		logger.debug("Request method should be GET or POST")
		statsd.incr('api.note_attachment.GET.400')
		return JsonResponse({'message': 'Error : Request method should be GET or POST'}, status=400)
	except Exception as e:
		logger.error("Something Happened: %s", e)
		statsd.incr('api.note_attachment.GET.400')
		return JsonResponse({'Error': 'Bad Request'}, status=400)
@csrf_exempt
def updateOrDeleteAttachments(request,note_id="",attachment_id=""):
	statsd.incr('api.note_attachment_id')
	# Update method to update attachments for authorized user
	try:
		logger.debug("Request Method : %s /note/<note_id>/attachments/<attachment_id>", request.method)
		if request.method == 'PUT':
			statsd.incr('api.note_attachment_id.PUT')
			if(request.FILES):
				user = validateSignin(request.META)
				if(user):
					if(is_valid_uuid(note_id)):                    
						try:
							note = NotesModel.objects.get(pk=note_id)
						except:
							logger.debug("Invalid note id")
							statsd.incr('api.note_attachment_id.PUT.400')
							return JsonResponse({'Error': 'Invalid note ID'}, status=400)
					else:
						logger.debug("Invalid note id")
						statsd.incr('api.note_attachment_id.PUT.400')
						return JsonResponse({'Error': 'Invalid note ID'}, status=400)
					if(is_valid_uuid(attachment_id)):
						try:
							attachment = Attachment.objects.get(pk=attachment_id)
						except:
							logger.debug("Invalid attachment id")
							statsd.incr('api.note_attachment_id.PUT.400')
							return JsonResponse({'Error': 'Invalid attachment ID'}, status=400)
					else:
						logger.debug("Invalid attachment id")
						statsd.incr('api.note_attachment_id.PUT.400')
						return JsonResponse({'Error': 'Invalid attachment ID'}, status=400)
					
					if(note.user == user):
						if(attachment.note == note):
							file = request.FILES['attachment']
							new_attachment = update_attachment(file_to_upload=file, filename= file._get_name(), note=note,attachment=attachment)
							note.last_updated_on = datetime.datetime.now()
							note.save()
							message = get_attachment_details(new_attachment)
							logger.info("Attachment updated")
							statsd.incr('api.note_attachment_id.PUT.200')
							return JsonResponse(message, status=200)
						else:
							logger.debug("Invalid attachment id")
							statsd.incr('api.note_attachment_id.PUT.400')
							return JsonResponse({'Error': 'Invalid attachment ID'}, status=400)
					else:
						logger.debug("Incorrect user details")
						statsd.incr('api.note_attachment_id.PUT.401')
						return JsonResponse({'message': 'Error : Invalid User Credentials'}, status=401)
			else:
				logger.debug("Files not selected")
				statsd.incr('api.note_attachment_id.PUT.400')
				return JsonResponse({'message': 'Error : Files not selected'}, status=400)
		# Delete method to delete attachments for authorized user
		if request.method == 'DELETE':
			statsd.incr('api.note_attachment_id.DELETE')
			user = validateSignin(request.META)
			if(user):
				if(is_valid_uuid(note_id)):
					try:
						note = NotesModel.objects.get(pk=note_id)
					except:
						logger.debug("Invalid note id")
						statsd.incr('api.note_attachment_id.DELETE.400')
						return JsonResponse({'Error': 'Invalid note ID'}, status=400)
				else:
					logger.debug("Invalid note id")
					statsd.incr('api.note_attachment_id.DELETE.400')
					return JsonResponse({'Error': 'Invalid note ID'}, status=400)
				if(is_valid_uuid(attachment_id)):
					try:
						attachment = Attachment.objects.get(pk=attachment_id)
					except:
						logger.debug("Invalid attachment id")
						statsd.incr('api.note_attachment_id.DELETE.400')
						return JsonResponse({'Error': 'Invalid attachment ID'}, status=400)
				else:
					logger.debug("Invalid attachment id")
					statsd.incr('api.note_attachment_id.DELETE.400')
					return JsonResponse({'Error': 'Invalid attachment ID'}, status=400)
				if(note.user == user):
					if(attachment.note.id == note.id):
						#Primary Logic for deleting attachments
						delete_attachment(attachment)
						note.last_updated_on = datetime.datetime.now()
						note.save()
						logger.info("Attachment Deleted")
						statsd.incr('api.note_attachment_id.DELETE.200')
						return JsonResponse({'message': 'Attachment Deleted'}, status=200)
					else:
						logger.debug("Invalid attachment id")
						statsd.incr('api.note_attachment_id.DELETE.400')
						return JsonResponse({'Error': 'Invalid attachment ID'}, status=400)
				else:
					logger.debug("Incorrect user details")
					statsd.incr('api.note_attachment_id.DELETE.401')
					return JsonResponse({'message': 'Error : Invalid User Credentials'}, status=401)
			else:
				logger.debug("Incorrect user details")
				statsd.incr('api.note_attachment_id.DELETE.401')
				return JsonResponse({'message': 'Error : Invalid User Credentials'}, status=401)
		logger.debug(" Request method should be PUT or DELETE")
		statsd.incr('api.note_attachment_id.DELETE.400')
		return JsonResponse({'message': 'Error : Request method should be PUT or DELETE'}, status=400)
	except Exception as e:
		logger.error("Something Happened: %s", e)
		statsd.incr('api.note_attachment_id.DELETE.400')
		return JsonResponse({'Error': 'Bad Request'}, status=400)

@csrf_exempt
def get404(request):
	statsd.incr('api.404')
	return JsonResponse({'Error': 'Page not found'}, status=404)

@csrf_exempt
def passwordReset(request):
	statsd.incr('api.passwordReset')
	email=request.POST.get('email')
	print(email)
	print(type(email))
	#Get email and verify if it exists in db
	if (email == ""):
		logger.debug("email is empty")
		return JsonResponse({'message': 'Email cant be empty'}, status=400)
	email_status = validateUserName(email)
	domain_name = settings.DOMAIN_NAME
	if email_status== True:
		if User.objects.filter(username=email).exists():
			logger.info("Sending notification to SNS")
			client = boto3.client('sns',region_name='us-east-1')
			response = client.publish(
				TargetArn=settings.SNSTOPICARN,
				MessageStructure='String',
				Message="Reset Email",
				MessageAttributes={
					"URL": {
							"DataType": "String",
							"StringValue": str(domain_name)
						},
					"email": {
							"DataType" : "String",
							"StringValue" : str(email)
						}
					}
				)
			statsd.incr('api.passwordReset.POST.200')
			return JsonResponse({"message": " : you will receive password reset link if the email address exists in our system"})
		else:
			statsd.incr('api.passwordReset.POST.400')
			return JsonResponse({"message": " : you will receive password reset link if the email address exists in our system"})
	else:
		statsd.incr('api.passwordReset.POST.400')
		return JsonResponse(email_status, status=400)


