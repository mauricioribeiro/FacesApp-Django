from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

import cv2, os, re, base64, numpy

context = {}
temp_path = 'faces/temp/'

def resetContext():
	global context
	context = {
		'title_tag': 'Home',
		'cv_tag' : cv2.__version__,
		'dir_tag' : os.getcwd(),
		'faceapp_data' : []
	}

def createFaceData(faceX, faceY, faceWidth, faceHeight):
	return {
		'id' : 'Undefined',
		'faceCoords' : { 'x1': faceX, 'x2': faceX + faceWidth, 'y1' : faceY, 'y2' : faceY + faceHeight },
	}

def notfound(request):
	return HttpResponse("Make sure the requested page exists..")

def login(request):
	resetContext()
	if request.method == 'POST':
		logged = createFacesImagebyHaarAndShi(request.POST['loginUsingFacesApp_frame'])
		if logged:
			context['success_msg'] = 'FacesApp detected a face!'
			#return HttpResponse("Logged!")
		else:
			context['error_msg'] = 'FaceApp didn\'t detect any faces'
	else:
		context['error_msg'] = 'You have no permission to access the requested page'

	return render(request, 'faces/index.html', context)

def index(request):
	resetContext()
	return render(request, 'faces/index.html', context)

def uri2file(uri_str, file_name):
	frame_str = re.search(r'base64,(.*)', uri_str).group(1)

	frame_file = open(file_name, 'wb')
	frame_file.write(base64.b64decode(frame_str))
	frame_file.close()

def createFacesImagebyHaar(post_uri):
	global temp_path
	print('<<< using Haar method >>')

	try:	
		uri2file(post_uri, temp_path + 'frame.jpg')

		cascPath = os.getcwd() + '/faces/haarcascade-source/haarcascade/'
		faceCascade = cv2.CascadeClassifier(cascPath + 'haarcascade_frontalface_default.xml')
		eyeCascade = cv2.CascadeClassifier(cascPath + 'haarcascade_eye.xml')

		frame = cv2.imread(temp_path + 'frame.jpg')
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		scaleFactor, minNeighbors, thickness = 1.3, 5, 2
		faceColor, eyeColor = (0, 255, 0), (255, 0, 0)

		faces = faceCascade.detectMultiScale(gray, scaleFactor, minNeighbors)
		for (fx, fy, fwidth, fheight) in faces:
			cv2.rectangle(frame, (fx, fy), (fx + fwidth, fy + fheight), faceColor, thickness)

			faceGray = gray[fy:fy + fheight, fx:fx + fwidth]
			eyes = eyeCascade.detectMultiScale(faceGray)

			if len(eyes) <= 2:
				for (ex, ey, ewidth, eheight) in eyes:
					cv2.rectangle(frame[fy:fy + fheight, fx:fx + fwidth], (ex, ey), (ex + ewidth, ey + eheight), eyeColor, thickness)
				context['faceapp_data'].append(createFaceData(fx, fy, fwidth, fheight))

		cv2.imwrite(temp_path + 'faces.jpg', frame)
		return True if len(faces) else False
	except:
		return False

def createFacesImagebyShi(post_uri):
	global temp_path
	print('<<< using Shi method >>')

	try:
		uri2file(post_uri, temp_path + 'frame.jpg')

		frame = cv2.imread(temp_path + 'frame.jpg')
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		maxCorners, qualityLevel, minDistance = 50, 0.01, 10
		corners = numpy.int0(cv2.goodFeaturesToTrack(gray, maxCorners, qualityLevel, minDistance))

		radius, color, thickness = 3, (0,0,255), -1
		for corner in corners:
			x,y = corner.ravel()
			cv2.circle(frame, (x,y), radius, color, thickness)

		cv2.imwrite(temp_path + 'faces.jpg', frame)
		return True
	except:
		return False

def createFacesImagebyHaarAndShi(post_uri):
	global temp_path
	print('<<< using Haar + Shi method >>')

	uri2file(post_uri, temp_path + 'frame.jpg')

	cascPath = os.getcwd() + '/faces/haarcascade-source/haarcascade/'
	faceCascade = cv2.CascadeClassifier(cascPath + 'haarcascade_frontalface_default.xml')

	frame = cv2.imread(temp_path + 'frame.jpg')
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	scaleFactor, minNeighbors, countFaces = 1.3, 5, 0
	for (fx, fy, fw, fh) in faceCascade.detectMultiScale(gray, scaleFactor, minNeighbors):
		countFaces += 1
		face, faceGray = frame[fy:fy + fh, fx:fx + fw], gray[fy:fy + fh, fx:fx + fw]

		maxCorners, qualityLevel, minDistance = 10, 0.01, 10
		corners = numpy.int0(cv2.goodFeaturesToTrack(faceGray, maxCorners, qualityLevel, minDistance))

		radius, color, thickness = 3, (0,0,255), -1
		for corner in corners:
			x,y = corner.ravel()
			cv2.circle(face, (x,y), radius, color, thickness)

		cv2.imwrite(temp_path + 'face_%d.jpg' %countFaces, face)

	return True if countFaces > 0 else False