from django.http import request
from django.shortcuts import render, redirect
from . forms import *
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .render import Render
import random    
from django.views.generic import View

POPULATION_SIZE = 9
NUMB_OF_ELITE_SCHEDULES = 1
TOURNAMENT_SELECTION_SIZE = 3
MUTATION_RATE = 0.05

class Data:
    def __init__(self):
        self._halls = Hall.objects.all()
        self._meetingTimes = MeetingTime.objects.all()
        self._lecturers = Lecturer.objects.all()
        self._courses = Course.objects.all()
        self._depts = Department.objects.all()

    def get_halls(self): return self._halls

    def get_lecturer(self): return self._lecturers

    def get_courses(self): return self._courses

    def get_depts(self): return self._depts

    def get_meetingTimes(self): return self._meetingTimes

data = Data()

class Schedule:
    def __init__(self):
        self._data = data
        self._classes = []
        self._numberOfConflicts = 0
        self._fitness = -1
        self._classNumb = 0
        self._isFitnessChanged = True

    def get_classes(self):
        self._isFitnessChanged = True
        return self._classes

    def get_numbOfConflicts(self): return self._numberOfConflicts

    def get_fitness(self):
        if self._isFitnessChanged:
            self._fitness = self.calculate_fitness()
            self._isFitnessChanged = False
        return self._fitness

    def initialize(self):
        sections = Section.objects.all()
        for section in sections:
            dept = section.department
            n = section.num_class_in_week
            if n <= len(MeetingTime.objects.all()):
                courses = dept.courses.all()
                for course in courses:
                    for i in range(n // len(courses)):
                        crs_lect = course.lecturers.all()
                        newClass = Class(self._classNumb, dept, section.section_id, course)
                        self._classNumb += 1
                        newClass.set_meetingTime(data.get_meetingTimes()[rnd.randrange(0, len(MeetingTime.objects.all()))])
                        newClass.set_hall(data.get_halls()[rnd.randrange(0, len(data.get_halls()))])
                        if crs_lect:
                            newClass.set_lecturer(crs_lect[rnd.randrange(0, len(crs_lect))])
                        else:
                            print("Error: crs_lect list is empty. Cannot set lecturer.")
                        self._classes.append(newClass)
            else:
                n = len(MeetingTime.objects.all())
                courses = dept.courses.all()
                for course in courses:
                    for i in range(n // len(courses)):
                        crs_lect = course.lecturers.all()
                        newClass = Class(self._classNumb, dept, section.section_id, course)
                        self._classNumb += 1
                        newClass.set_meetingTime(data.get_meetingTimes()[rnd.randrange(0, len(MeetingTime.objects.all()))])
                        newClass.set_hall(data.get_halls()[rnd.randrange(0, len(data.get_halls()))])
                        newClass.set_lecturer(crs_lect[rnd.randrange(0, len(crs_lect))])
                        self._classes.append(newClass)

        return self


    def calculate_fitness(self):
            self._numberOfConflicts = 0
            classes = self.get_classes()
            for i in range(len(classes)):
                if classes[i].hall.seating_capacity < int(classes[i].course.max_numb_students):
                    self._numberOfConflicts += 1
                for j in range(len(classes)):
                    if j >= i:
                        if (classes[i].meeting_time == classes[j].meeting_time) and \
                                (classes[i].section_id != classes[j].section_id) and (classes[i].section == classes[j].section):
                            if classes[i].hall == classes[j].hall:
                                self._numberOfConflicts += 1
                            if classes[i].lecturer == classes[j].lecturer:
                                self._numberOfConflicts += 1
            return 1 / (1.0 * self._numberOfConflicts + 1)
    
class Population:
    def __init__(self, size):
        self._size = size
        self._data = data
        schedules = [Schedule() for i in range(size)]
        for schedule in schedules:
            schedule.initialize()
        self._schedules = schedules

    def get_schedules(self):
        return self._schedules
    
class GeneticAlgorithm:
    def evolve(self, population):
        return self._mutate_population(self._crossover_population(population))

    def _crossover_population(self, pop):
        crossover_pop = Population(0)
        for i in range(NUMB_OF_ELITE_SCHEDULES):
            crossover_pop.get_schedules().append(pop.get_schedules()[i])
        i = NUMB_OF_ELITE_SCHEDULES
        while i < POPULATION_SIZE:
            schedule1 = self._select_tournament_population(pop).get_schedules()[0]
            schedule2 = self._select_tournament_population(pop).get_schedules()[0]
            crossover_pop.get_schedules().append(self._crossover_schedule(schedule1, schedule2))
            i += 1
        return crossover_pop

    def _mutate_population(self, population):
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            self._mutate_schedule(population.get_schedules()[i])
        return population

    def _crossover_schedule(self, schedule1, schedule2):
        crossoverSchedule = Schedule().initialize()
        for i in range(0, len(crossoverSchedule.get_classes())):
            if rnd.random() > 0.5:
                crossoverSchedule.get_classes()[i] = schedule1.get_classes()[i]
            else:
                crossoverSchedule.get_classes()[i] = schedule2.get_classes()[i]
        return crossoverSchedule

    def _mutate_schedule(self, mutateSchedule):
        schedule = Schedule().initialize()
        for i in range(len(mutateSchedule.get_classes())):
            if MUTATION_RATE > rnd.random():
                mutateSchedule.get_classes()[i] = schedule.get_classes()[i]
        return mutateSchedule

    def _select_tournament_population(self, pop):
        tournament_pop = Population(0)
        i = 0
        while i < TOURNAMENT_SELECTION_SIZE:
            tournament_pop.get_schedules().append(pop.get_schedules()[rnd.randrange(0, POPULATION_SIZE)])
            i += 1
        tournament_pop.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        return tournament_pop
    
class Class:
    def __init__(self, id, dept, section, course):
        self.section_id = id
        self.department = dept
        self.course = course
        self.lecturer = None
        self.meeting_time = None
        self.hall = None
        self.section = section

    def get_id(self): return self.section_id

    def get_dept(self): return self.department

    def get_course(self): return self.course

    def get_lecturer(self): return self.lecturer

    def get_meetingTime(self): return self.meeting_time

    def get_hall(self): return self.hall

    def set_lecturer(self, lecturer): self.lecturer = lecturer

    def set_meetingTime(self, meetingTime): self.meeting_time = meetingTime

    def set_hall(self, hall): self.hall = hall

def context_manager(schedule):
    classes = schedule.get_classes()
    context = []
    cls = {}
    for i in range(len(classes)):
        cls["section"] = classes[i].section_id
        cls['dept'] = classes[i].department.dept_name
        cls['course'] = f'{classes[i].course.course_name} ({classes[i].course.course_number}, ' \
                        f'{classes[i].course.max_numb_students}'
        cls['hall'] = f'{classes[i].hall.h_name} ({classes[i].hall.seating_capacity})'
        cls['lecturer'] = f'{classes[i].lecturer.name} ({classes[i].lecturer.uid})'
        cls['meeting_time'] = [classes[i].meeting_time.pid, classes[i].meeting_time.day, classes[i].meeting_time.time]
        context.append(cls)
    return context

def timetable(request):
    schedule = []
    population = Population(POPULATION_SIZE)
    generation_num = 0
    population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
    geneticAlgorithm = GeneticAlgorithm()
    while population.get_schedules()[0].get_fitness() != 1.0:
        generation_num += 1
        print('\n> Generation #' + str(generation_num))
        population = geneticAlgorithm.evolve(population)
        population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        schedule = population.get_schedules()[0].get_classes()

    return render(request, 'gentimetable.html', {'schedule': schedule, 'sections': Section.objects.all(),
                                                'times': MeetingTime.objects.all()})

###########################################################################################################################################
def home(request):
    return render(request, 'home.html', {})

@login_required
def guide(request):
    return render(request, 'guide.html', {})
###########################################################################################################################################
@login_required
def addCourses(request):
    form = CourseForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addCourses')
        else:
            print('Invalid')
    context = {
        'form': form
    }
    return render(request, 'addCourses.html', context)

@login_required
def course_list_view(request):
    context = {
        'courses': Course.objects.all()
    }
    return render(request, 'courseslist.html', context)

@login_required
def delete_course(request, pk):
    crs = Course.objects.filter(pk=pk)
    if request.method == 'POST':
        crs.delete()
        return redirect('editcourse')

###########################################################################################################################################
@login_required
def addLecturer(request):
    form = LecturerForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addLecturers')
    context = {
        'form': form
    }
    return render(request, 'addLecturers.html', context)

@login_required
def lect_list_view(request):
    context = {
        'lecturers': Lecturer.objects.all()
    }
    return render(request, 'leclist.html', context)
    
@login_required
def delete_lecturer(request, pk):
    lect = Lecturer.objects.filter(pk=pk)
    if request.method == 'POST':
        lect.delete()
        return redirect('editlecturer')

########################################################################################################################################### 
@login_required
def addHalls(request):
    form = HallForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addHalls')
    context = {
        'form': form
    }
    return render(request, 'addHalls.html', context)

@login_required
def hall_list(request):
    context = {
        'halls': Hall.objects.all()
    }
    return render(request, 'hallslist.html', context)

@login_required
def delete_hall(request, pk):
    hl = Hall.objects.filter(pk=pk)
    if request.method == 'POST':
        hl.delete()
        return redirect('edithalls')

###########################################################################################################################################   
@login_required
def addTimings(request):
    form = MeetingTimeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addTimings')
        else:
            print('Invalid')
    context = {
        'form': form
    }
    return render(request, 'addTimings.html', context)

@login_required
def meeting_list_view(request):
    context = {
        'meeting_times': MeetingTime.objects.all()
    }
    return render(request, 'mtlist.html', context)

@login_required
def delete_meeting_time(request, pk):
    mt = MeetingTime.objects.filter(pk=pk)
    if request.method == 'POST':
        mt.delete()
        return redirect('editmeetingtime')

###########################################################################################################################################   
@login_required
def addDepts(request):
    form = DepartmentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addDepts')
    context = {
        'form': form
    }
    return render(request, 'addDepts.html', context)

@login_required
def department_list(request):
    context = {
        'departments': Department.objects.all()
    }
    return render(request, 'deptlist.html', context)

@login_required
def delete_department(request, pk):
    dept = Department.objects.filter(pk=pk)
    if request.method == 'POST':
        dept.delete()
        return redirect('editdepartment')
    
###########################################################################################################################################
@login_required
def addSections(request):
    form = SectionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('addSections')
    context = {
        'form': form
    }
    return render(request, 'addSections.html', context)

@login_required
def section_list(request):
    context = {
        'sections': Section.objects.all()
    }
    return render(request, 'seclist.html', context)

@login_required
def delete_section(request, pk):
    sec = Section.objects.filter(pk=pk)
    if request.method == 'POST':
        sec.delete()
        return redirect('editsection')

###########################################################################################################################################
@login_required
def generate(request):
    return render(request, 'generate.html', {})

###########################################################################################################################################
class Pdf(View):
    def get(self, request):
        params = {
            'request': request
        }
        return Render.render('gentimetable.html', params)