from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import auth
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

import numpy as np
from PIL import Image
import base64
import re
from io import StringIO, BytesIO
import face_recognition
import datetime
from . import utils
import pyrebase
import qrcode
import random
import os
from pyzbar.pyzbar import decode
import pytz

firebaseConfig = {
    'apiKey': "AIzaSyCt_ES04VDH6IyBOx810tj0eG6a17-uzTA",
    'authDomain': "face-recog-2aeb4.firebaseapp.com",
    'databaseURL': "https://face-recog-2aeb4.firebaseio.com",
    'projectId': "face-recog-2aeb4",
    'storageBucket': "face-recog-2aeb4.appspot.com",
    'messagingSenderId': "218928360961",
    'appId': "1:218928360961:web:b2d67d596e1082e97b5a00",
    'measurementId': "G-LM4YT1REVF"
  }
 
fire = pyrebase.initialize_app(firebaseConfig)

authe = fire.auth()
database = fire.database()

QR_random = 0

def login(request):
    
    return render(request, 'login.html',{'error':'0'})

def dupHome(request):
    user = []
    email = ""
    try:
        idToken = request.session['uid']
        user = authe.get_account_info(idToken)["users"][0]
        email = user["email"]
    except KeyError:
        return redirect('logOut')
    if(len(email.split("@")[0]) != 6):
        localId = user["localId"]
        name = database.child("Users").child(localId).child("details").child("firstName").get().val()
        return render(request, 'StudentHome.html', {'i':name})
    else:
        database.child("publicData").update({"AttendanceStatus":False})
        return render(request, 'FacultyHome.html', {'i':"Faculty"})
    
def attendanceClosed(request):
    name = ""
    try:
        idToken = request.session['uid']
        user = authe.get_account_info(idToken)["users"][0]
        localId = user["localId"]
        name = database.child("Users").child(localId).child("details").child("firstName").get().val()
    except KeyError:
        return redirect('logOut')
    return render(request, 'StudentHome.html', {'i':name, 'Closed':"0"})
    
def attendanceRecorded(request):
    name = ""
    try:
        idToken = request.session['uid']
        user = authe.get_account_info(idToken)["users"][0]
        localId = user["localId"]
        name = database.child("Users").child(localId).child("details").child("firstName").get().val()
    except KeyError:
        return redirect('logOut')
    return render(request, 'StudentHome.html', {'i':name, 'Recorded':"0"})
    
def home(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    user = []
    try:
        user = authe.sign_in_with_email_and_password(email, password)
        #print(user['idToken'])
    except:
        return redirect('wrongCredentials')
    sessionId = user['idToken']
    request.session['uid'] = str(sessionId)
    if(len(email.split("@")[0]) != 6):
        localId = user["localId"]
        name = database.child("Users").child(localId).child("details").child("firstName").get().val()
        return render(request, 'StudentHome.html', {'i':name})
    else:
        database.child("publicData").update({"AttendanceStatus":False})
        return render(request, 'FacultyHome.html', {'i':"Faculty"})

def wrongCredentials(request):
    return render(request, 'login.html',{'error':'1'})

def logOut(request):
    email = ""
    try:
        idToken = request.session['uid']
        user = authe.get_account_info(idToken)["users"][0]
        email = user["email"]
        del request.session['uid']
    except:
        return render(request, 'login.html',{'error':'2'})
    if(len(email.split("@")[0]) == 6):
        database.child("publicData").update({"AttendanceStatus":False})
    return render(request, 'login.html',{'error':'2'})

def showAttendance(request):
    localId = ""
    try:
        idToken = request.session['uid']
        user = authe.get_account_info(idToken)["users"][0]
        localId = user["localId"]
    except KeyError:
        return redirect('logOut')
    data = []
    allClasses,attendedClasses = database.child("Users").child(localId).child("AttendanceLastCount").get().val(), 0;
    regId = database.child("Users").child(localId).child("details").child("regNumber").get().val()
    name = database.child("Users").child(localId).child("details").child("firstName").get().val() + " " + database.child("Users").child(localId).child("details").child("lastName").get().val()

    for i in range(database.child("Users").child(localId).child("AttendanceLastCount").get().val()):
        Attendance = []
        dateTime = database.child("Users").child(localId).child("DateTime").child(i).get().val()
        Attendance.append(dateTime.split(" ")[0])
        Attendance.append(dateTime.split(" ")[1])
        Attendance.append(database.child("Users").child(localId).child("AttendanceMarked").child(i).get().val())
        if(database.child("Users").child(localId).child("AttendanceMarked").child(i).get().val() == "Present"):
            attendedClasses+=1
        data.append(Attendance)
    return render(request, 'showAttendance.html',{"data": data, "percentage": format((attendedClasses/allClasses)*100, '.2f'), "Name": name,"RegId": regId})

def ajaxQR(request):
    try:
        if(database.child("publicData").child("AttendanceStatus").get().val()):
            image_b64 = request.POST.get('imageBase64')
            image_data = re.sub('^data:image/.+;base64,', '', image_b64)
            image_PIL = Image.open(BytesIO(base64.b64decode(image_data)))
            image_np = np.array(image_PIL) 
            #Shape Difference
            idToken = request.session['uid']
            user = authe.get_account_info(idToken)["users"][0]
            
            global QR_random
            Status = "False"
            QR_List = decode(image_PIL)
            if(len(QR_List)!=0 and int(QR_List[0].data.decode("utf-8")) == QR_random):
                Status = "True"
            return HttpResponse(json.dumps({'Status': Status}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'Status': "Closed"}), content_type="application/json")
    except KeyError:
        return redirect('logOut')
    except Exception as e:
        print("error: "+str(e))
    return HttpResponse("Success!")

def ajaxCanvas(request):
    try:
        if(database.child("publicData").child("AttendanceStatus").get().val()):
            image_b64 = request.POST.get('imageBase64')
            image_data = re.sub('^data:image/.+;base64,', '', image_b64)
            image_PIL = Image.open(BytesIO(base64.b64decode(image_data)))
            image_np = np.array(image_PIL) 
            #Shape Difference
            idToken = request.session['uid']
            user = authe.get_account_info(idToken)["users"][0]
            Known_Face_Encoding = database.child("Users").child(user["localId"]).child("details").child("faceDetails").get().val().split()
            Known_Face_Encoding = [float(x) for x in Known_Face_Encoding]
            #print(Known_Face_Encoding)
            Status = utils.faceRecog(Known_Face_Encoding ,image_np)
            if(Status == "True"):
                database.child("Users").child(user["localId"]).update({"PresentAttendance": "Present"})
            return HttpResponse(json.dumps({'Status': Status}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'Status': "Closed"}), content_type="application/json")
    except KeyError:
        return redirect('logOut')
    except Exception as e:
        print("error: "+str(e))
    return HttpResponse("Success!")
               
def ajaxStatusCheck(request):
    idToken = request.session['uid']
    user = authe.get_account_info(idToken)["users"][0]
    localId = user["localId"]
    presentAttendance = database.child("Users").child(localId).child("PresentAttendance").get().val()
    attendanceStatus = database.child("publicData").child("AttendanceStatus").get().val()
    if(presentAttendance == "Present" and attendanceStatus):
        return HttpResponse(json.dumps({'Status': "Present"}), content_type="application/json")
    elif(attendanceStatus):
        return HttpResponse(json.dumps({'Status': "Open"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'Status': "Closed"}), content_type="application/json")

def ajaxAttendanceUpdate(request):
    data = {}
    try:
        idToken = request.session['uid']
        length = database.child("publicData").child("LastCount").get().val()
        data["length"] = length
        for i in range(length):
            localId = database.child("publicData").child("studentLocalId").child(i).get().val()
            val = database.child("Users").child(localId).child("PresentAttendance").get().val()
            data[i] = val
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        global QR_random 
        QR_random = random.randint(0,99999999)
        qr.add_data(QR_random)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        contents = base64.b64encode(img_io.getvalue())
        data["contents"] = contents.decode('UTF-8')
        img_io.close()
    except KeyError:
        return redirect('logOut')
    return HttpResponse(json.dumps(data), content_type="application/json")
    
@csrf_exempt
def ajaxCheckImage(request):
    try:
        print(request.FILES['ImageData'])
    except:
        print("Error")
    return HttpResponse(json.dumps({}), content_type="application/json")    
    
def ajaxCheckEmail(request):
    PregId = request.GET.get('Email', None)
    PregId = PregId.split("@")[0]
    for i in range(database.child("publicData").child("LastCount").get().val()):
        localId = database.child("publicData").child("studentLocalId").child(i).get().val()
        regId = database.child("Users").child(localId).child("details").child("regNumber").get().val()
        if(PregId == regId):
            return HttpResponse(json.dumps({"Exist": "True"}), content_type="application/json")
    return HttpResponse(json.dumps({"Exist": "False"}), content_type="application/json")
    
def studentRegister(request):
    try:
        idToken = request.session['uid']
        database.child("publicData").update({"AttendanceStatus":False})
    except KeyError:
        return redirect('logOut')
    
    return render(request, 'studentRegister.html', {})

def postRegistration(request):
    database.child("publicData").update({"AttendanceStatus":False})
    emai = ""
    try:
        idToken = request.session['uid']
        user = authe.get_account_info(idToken)["users"][0]
        emai = user["email"]
    except KeyError:
        return redirect('logOut')
    firstName = email = request.POST.get("firstName")
    lastName = email = request.POST.get("lastName")
    email = request.POST.get("email")
    password = request.POST.get("password")
    faceImage = request.FILES['myFile']
    
    image_PIL = Image.open(faceImage)
    image_np = np.array(image_PIL)
    
    #print(image_np.shape)
    row,col,plane = image_np.shape
    x, y = 4, 4

    blue_plane = image_np[:,:,0]
    green_plane = image_np[:,:,1]
    red_plane = image_np[:,:,2]

    resize_blue_plane = blue_plane[0::x,0::x]
    resize_green_plane = green_plane[0::x,0::x]
    resize_red_plane = red_plane[0::x,0::x]
    
    newRow, newCol = resize_blue_plane.shape
    small_frame = np.zeros((newRow, newCol, 3),np.uint8)

    small_frame[:,:,0] = resize_blue_plane
    small_frame[:,:,1] = resize_green_plane
    small_frame[:,:,2] = resize_red_plane
    

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)
    
    if(len(face_encodings) != 1):
        return render(request, 'studentRegister.html', {"error" : True})
    faceDetails = ""
    for value in face_encodings[0]:
        faceDetails+=str(value)+" "
    
    user = authe.create_user_with_email_and_password(email, password);
    uid = user['localId']
    
    attendanceData = {"AttendanceLastCount" : 0, "PresentAttendance" : "Absent"}
    database.child("Users").child(uid).set(attendanceData)
    
    data = {"firstName":firstName, "lastName":lastName, "faceDetails":faceDetails, "regNumber":email.split("@")[0]}
    database.child("Users").child(uid).child("details").set(data)
    
    
    val =database.child("publicData").child("LastCount").get().val()
    database.child("publicData").child("studentLocalId").child(val).set(user['localId'])
    val+=1;
    
    database.child("publicData").update({"LastCount":val})
    return render(request, 'FacultyHome.html', {'i':"Faculty", 'Registered':firstName+" "+lastName})

def allStudents(request):
    try:
        idToken = request.session['uid']
    except KeyError:
        return redirect('logOut')
    data = []
    for i in range(database.child("publicData").child("LastCount").get().val()):
        student = []
        localId = database.child("publicData").child("studentLocalId").child(i).get().val()
        regId = database.child("Users").child(localId).child("details").child("regNumber").get().val()
        name = database.child("Users").child(localId).child("details").child("firstName").get().val() + " " + database.child("Users").child(localId).child("details").child("lastName").get().val()
        student.append(regId)
        student.append(name)
        data.append(student)
    return render(request, 'allStudents.html', {"data": data})

def getAttendance(request):
    try:
        idToken = request.session['uid']
    except KeyError:
        return redirect('logOut')
    
    localId = database.child("publicData").child("studentLocalId").child(request.POST.get('userId')).get().val()
    data = []
    regId = database.child("Users").child(localId).child("details").child("regNumber").get().val()
    name = database.child("Users").child(localId).child("details").child("firstName").get().val() + " " + database.child("Users").child(localId).child("details").child("lastName").get().val()
    
    allClasses,attendedClasses = database.child("Users").child(localId).child("AttendanceLastCount").get().val(), 0;
    
    for i in range(database.child("Users").child(localId).child("AttendanceLastCount").get().val()):
        Attendance = []
        dateTime = database.child("Users").child(localId).child("DateTime").child(i).get().val()
        Attendance.append(dateTime.split(" ")[0])
        Attendance.append(dateTime.split(" ")[1])
        Attendance.append(database.child("Users").child(localId).child("AttendanceMarked").child(i).get().val())
        if(database.child("Users").child(localId).child("AttendanceMarked").child(i).get().val() == "Present"):
            attendedClasses+=1
        data.append(Attendance)
    return render(request, 'showAttendance.html',{"data": data, "percentage": format((attendedClasses/allClasses)*100, '.2f'), "Name": name,"RegId": regId})

def markAttendance(request):
    name = ""
    try:
        idToken = request.session['uid']
        user = authe.get_account_info(idToken)["users"][0]
        name = database.child("Users").child(user["localId"]).child("details").child("firstName").get().val()
    except KeyError:
        return redirect('logOut')
    return render(request, 'markAttendance.html', {"i":name})

def facultyAttendance(request):
    data = []
    try:
        idToken = request.session['uid']
        database.child("publicData").update({"AttendanceStatus":True})
        for i in range(database.child("publicData").child("LastCount").get().val()):
            student = []
            localId = database.child("publicData").child("studentLocalId").child(i).get().val()
            student.append(database.child("Users").child(localId).child("details").child("firstName").get().val())
            student.append(database.child("Users").child(localId).child("details").child("lastName").get().val())
            student.append(database.child("Users").child(localId).child("details").child("regNumber").get().val())
            database.child("Users").child(localId).update({"PresentAttendance": "Absent"})
            data.append(student)
        #data = [[FirstName, SecondName, Email],[],[]]
    except KeyError:
        return redirect('logOut')
    return render(request, 'facultyAttendance.html', {"data":data})

def attendanceMarked(request):
    try:
        idToken = request.session['uid']
        user = authe.get_account_info(idToken)["users"][0]
        email = user["email"]
    except KeyError:
        return redirect('logOut')
    utcmoment_naive = datetime.datetime.utcnow()
    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
    localDatetime = utcmoment.astimezone(pytz.timezone('Asia/Calcutta'))
    print()
    print()
    Date = localDatetime.strftime("%m/%d/%Y")
    Hour = int(localDatetime.strftime("%H"))
    for i in range(database.child("publicData").child("LastCount").get().val()):
        localId = database.child("publicData").child("studentLocalId").child(i).get().val()
        val = database.child("Users").child(localId).child("AttendanceLastCount").get().val()
        database.child("Users").child(localId).child("AttendanceMarked").child(val).set(request.POST.get("sel"+str(i)))
        database.child("Users").child(localId).child("DateTime").child(val).set(Date+" "+(format(Hour if(Hour <= 12) else Hour%12, '02'))+("AM-" if(Hour%24 < 12) else "PM-")+(format((Hour+1)%24 if((Hour+1)%24 <= 12) else (Hour+1)%12, '02')) + ("AM" if((Hour+1)%24 < 12) else "PM"))
        database.child("Users").child(localId).update({"AttendanceLastCount": val+1})
        database.child("Users").child(localId).update({"PresentAttendance": "Absent"})
    database.child("publicData").update({"AttendanceStatus":False})
    return render(request, 'FacultyHome.html', {'i':"Faculty", 'Status':"Marked"})
