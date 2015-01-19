# quick and dirty CLI for downloading courses from teamtreehouse.com.
# Usage: python app.py
# By default videos are downloaded into a 'videos' folder in the current working directory 
# If you'd like to put them somewhere else, look at modifying downloader.py


from spider.treehouse import CourseBrowser
import os

clear = lambda : os.system('tput reset')
clear()

# some nice terminal colours if we're not on windows 
if os.name != 'nt':
	ANSI_RED = "\033[5;40;31m"
	heading = "\033[1;40;33m"
	ANSI_RESET = "\033[0m"
else:
	ANSI_RED = ""
	heading = ""
	ANSI_RESET = ""

def authenticate_user():
	""" Gets user input and attempts to authenticate them with teamtreehouse.com """
	is_authenticated = False
	try_again = 'y'
	clear()
	print heading + "------------Sign In------------" + ANSI_RESET
	while is_authenticated == False and try_again == 'y':

		email = raw_input("Please enter your email: ")
		password = raw_input("Please enter your password: ")
		session = CourseBrowser(email, password)

		if session.authenticate() == True:
			is_authenticated = True
			print "Successfully Logged in!"
			print "Sorting all of the courses..."
			session.categorise()
			return session

		try_again = raw_input("Log in unsuccessful, would you like to try again? (y/n): ")
	return


def choose_language():
	""" display a list of programming languages treehouse has courses for and ask the user to pick one """
	clear()
	# get a lit of languages
	language_list = session.get_languages()

	# print all programming languages treehouse has courses for
	print heading + "------------Topics-------------" + ANSI_RESET
	i = 0
	for language in language_list:
		i +=1
		print "[{0}]: {1} ".format(i, language)
	print "[0]: To go back"

	# input loop
	valid_choices = set([x for x in range(0,i+2)])
	choice = -1
	while choice  not in valid_choices:
		try:
			choice = int(raw_input("Option: "))
		except ValueError:
			print "Please enter a number.",
		if choice not in valid_choices:
			print "Invalid option."

	# return user's choice
	if choice == 0:
		return
	return language_list[int(choice)-1]


def choose_course(choice):
	""" display a list of courses available for a languages and ask the user to pick one """
	clear()
	# print the menu
	print heading + "------ Courses for: {0} -------".format(choice) + ANSI_RESET
	i = 0
	print "['a']: To download all courses"
	for course in session.get_courses(choice):
		i+=1
		if course.membership == 'pro':
			print "[{0}]: {1} - {2} ({3})".format(i, course, course.category, course.membership)
		else:
			print "[{0}]: {1} - {2}".format(i, course, course.category) 
	print "[0]: To go back"
	
	# input loop
	valid_choices = set([x for x in range(0,i+2)])
	choice = -1
	while choice  not in valid_choices:
		try:
			choice = raw_input("Option: ")
			if choice == 'a' or choice == "'a'":
				return 'a'
			else:
				choice = int(choice)
		except ValueError:
			print "Please enter a number.",
		if choice not in valid_choices:
			print "Invalid option."

	# return user's choice
	if choice == 0:
		return
	return choice


def main_menu():
	""" main menu that takes user's to sub menus"""
	clear()
	# print the menu
	print heading + "-----------Main Menu-----------" + ANSI_RESET
	print "[1]: View Programming Languages"
	print "[2]: Re-Authenticate"
	print "[3]: Exit "

	# input loop
	valid_choices = set([1,2,3])
	choice = 0
	while choice not in valid_choices:
		try:
			choice = int(raw_input("Option: "))
		except ValueError:
			print "Please enter a number.",
		if choice not in valid_choices:
			print "Invalid option."

	# return user's choice
	return choice


# terminal loop
session = None
while True:
	# authenticate the user 
	if not session:
		session = authenticate_user()

	# main menu
	choice = main_menu()

	# show available languages
	if choice == 1:
		while True:
			lang_choice = choose_language()
			# if they picked a language they want courses for
			# display available courses
			if lang_choice:
				while True:
					course_choice = choose_course(lang_choice)
					if course_choice:
						# if choice is 'a' download all courses
						# for that language
						if course_choice == 'a':
							format = raw_input("Select a format (webm/mp4): ")
							clear()
							session.download_all_videos(lang_choice, format)
						# otherwise download only that course
						else:
							format = raw_input("Select a format (webm/mp4): ")
							course = session.tracks[lang_choice][course_choice-1]
							clear()
							session.download_course_videos(course, format)
					else:
						break
			else:
				break
	# re-authenticate the user and update the course catalogue
	elif choice == 2:
		session = authenticate_user()
	# quit
	elif choice == 3:
		break