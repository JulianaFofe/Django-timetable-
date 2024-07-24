from django.forms import ModelForm
from. models import *
from django import forms

class HallForm(ModelForm):
    class Meta:
        model = Hall
        labels = {
            "h_name": "Hall name",
            "seating_capacity": "Capacity"
        }
        fields = [
            'h_name',
            'seating_capacity'
        ]

class LecturerForm(ModelForm):
    class Meta:
        model = Lecturer
        labels = {
            "uid": "Teacher UID",
            "name": "Full Name"
        }
        fields = [
            'uid',
            'name',
        ]

class MeetingTimeForm(ModelForm):
    class Meta:
        model = MeetingTime
        fields = [
            'pid',
            'time',
            'day'
        ]
        widgets = {
            'pid': forms.TextInput(),
            'time': forms.Select(),
            'day': forms.Select(),
        }
        labels = {
            "pid": "Meeting ID",
            "time": "Time",
            "day": "Day of the Week"
        }

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'max_numb_students', 'lecturers']
        labels = {
            "course_code": "Course code",
            "course_name": "Course Name",
            "max_numb_students": "Course Capacity",
            "lecturers": "Course Lecturer"
        }

class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = ['dept_name', 'courses']
        labels = {
            "dept_name": "Department Name",
            "courses": "Corresponding Courses"
        }


class SectionForm(ModelForm):
    class Meta:
        model = Section
        fields = ['section_id', 'department', 'num_class_in_week']
        labels = {
            "section_id": "Section ID",
            "department": "Corresponding Department",
            "num_class_in_week": "Classes Per Week"
        }