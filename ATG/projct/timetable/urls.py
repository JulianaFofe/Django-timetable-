from django.urls import  path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),
    path('guide', views.guide, name='guide'),

    path('add_lecturers', views.addLecturer, name='addLecturers'),
    path('lecturers_list/', views.lect_list_view , name='editlecturer'),
    path('delete_lecturer/<int:pk>/', views.delete_lecturer, name='deletelecturer'),

    path('add_halls', views.addHalls, name='addHalls'),
    path('halls_list/', views.hall_list, name='edithalls'),
    path('delete_hall/<int:pk>/', views.delete_hall, name='deletehall'),

    path('add_timings', views.addTimings, name='addTimings'),
    path('timings_list/', views.meeting_list_view, name='editmeetingtime'),
    path('delete_meetingtime/<str:pk>/', views.delete_meeting_time, name='deletemeetingtime'),

    path('add_courses', views.addCourses, name='addCourses'),
    path('courses_list/', views.course_list_view, name='editcourse'),
    path('delete_course/<str:pk>/', views.delete_course, name='deletecourse'),

    path('add_departments', views.addDepts, name='addDepts'),
    path('departments_list/', views.department_list, name='editdepartment'),
    path('delete_department/<int:pk>/', views.delete_department, name='deletedepartment'),

    path('add_sections', views.addSections, name='addSections'),
    path('sections_list/', views.section_list, name='editsection'),
    path('delete_section/<str:pk>/', views.delete_section, name='deletesection'),

    path('generate_timetable', views.generate, name='generate'),

    path('timetable_generation/', views.timetable, name='timetable'),
    path('timetable_generation/render/pdf', views.Pdf.as_view(), name='pdf'),
]