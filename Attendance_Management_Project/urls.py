"""Attendance_Management_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('home', views.home, name="home"),
    path('wrongCredentials', views.wrongCredentials, name="wrongCredentials"),
    path('logOut', views.logOut, name="logOut"),
    path('ajaxQR', views.ajaxQR, name="ajaxQR"),
    path('ajaxCanvas', views.ajaxCanvas, name="ajaxCanvas"),
    path('ajaxCheckImage', views.ajaxCheckImage, name="ajaxCheckImage"),
    path('ajaxCheckEmail', views.ajaxCheckEmail, name="ajaxCheckEmail"),
    path('ajaxStatusCheck', views.ajaxStatusCheck, name="ajaxStatusCheck"),
    path('ajaxAttendanceUpdate', views.ajaxAttendanceUpdate, name="ajaxAttendanceUpdate"),
    path('studentRegister', views.studentRegister, name="studentRegister"),
    path('postRegistration', views.postRegistration, name="postRegistration"),
    path('dupHome', views.dupHome, name="dupHome"),
    path('attendanceClosed', views.attendanceClosed, name="attendanceClosed"),
    path('attendanceRecorded', views.attendanceRecorded, name="attendanceRecorded"),
    path('facultyAttendance', views.facultyAttendance, name="facultyAttendance"),
    path('allStudents', views.allStudents, name="allStudents"),
    path('getAttendance', views.getAttendance, name="getAttendance"),
    path('markAttendance', views.markAttendance, name="markAttendance"),
    path('attendanceMarked', views.attendanceMarked, name="attendanceMarked"),
    path('showAttendance', views.showAttendance, name="showAttendance")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
