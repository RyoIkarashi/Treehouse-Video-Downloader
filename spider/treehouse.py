from auth import AuthSession
from lxml import html
import os
from sys import stdout
import downloader as d


class Course:
	"""simple class for holding all the course information"""
	def __init__(self, category, language, title, duration, difficulty, url, description, membership):
		self.category = category
		self.language = language
		self.title = title
		self.duration = duration
		self.difficulty = difficulty
		self.url = url
		self.description = description
		self.membership = membership
		self.videos = {}

	def __str__(self):
		return self.title


class CourseBrowser(AuthSession):
	"""Fetches all off the available courses offered by treehouse,
	   finds all available videos for a course and their source urls."""
	def __init__(self, user_name, password):
		super(CourseBrowser, self).__init__(user_name, password)
		# holds all of the courses, categorised by language.
		# structure --> {language: [course_1, course_2], language:[course_1]}
		self.tracks = {}

	def categorise(self):
		"""Sort all of the courses in the library by programming language."""
		response = self.get("https://teamtreehouse.com/library")

		# if there's no response from requesting /library, exit
		if not response:
			return

		tree = html.fromstring(response.text)
		# list with all the course cards
		library = tree.xpath("//ul[@class='card-list']")[0]

		for card in library:
			card_info = card.xpath("@class")[0]
			card_category = card_info.split()[1]
			card_language = card_info.split()[2]
			card_title = card.xpath("a/h3/text()")[0]
			card_url = "http://teamtreehouse.com" + card.xpath("a/@href")[0]
			card_description = card.xpath("a/p[@class='description']/text()")[0].replace("\n", "").strip()
			# not all cards have a duration, difficult and membership so
			# we need to do a bit of error handling
			try:
				card_duration = card.xpath("a/div/span[@class='estimate']/text()")[0]
			except IndexError:
				card_duration = None

			try:
				card_difficulty = card.xpath("ul[@class='tags']/li[@class='difficulty']/span/text()")[0]
			except IndexError:
				card_difficulty = None

			if card.xpath("ul[@class='tags']/li[@class='pro-content']"):
				card_membership = 'pro'
			else:
				card_membership = 'premium'

			# put all cards into a dictionary, categorised by programming language
			if card_language in self.tracks:
				self.tracks[card_language].append(Course(
					category=card_category,
			  		language=card_language,
			  		title=card_title,
			  		duration=card_duration,
			  		difficulty=card_difficulty,
			  		url=card_url,
			  		description=card_description,
			  		membership=card_membership))
			else:
				self.tracks[card_language] = [Course(
					category=card_category,
			  		language=card_language,
			  		title=card_title,
			  		duration=card_duration,
			  		difficulty=card_difficulty,
			  		url=card_url,
			  		description=card_description,
			  		membership=card_membership)]


	def get_languages(self):
		"""View a list of all programming languages treehouse has courses for"""
		return [language for language in self.tracks.keys()]


	def get_courses(self, language):
		"""View a list of all courses for a programming language"""
		language = language.lower()

		if language in self.tracks:
			return [course for course in self.tracks[language]]
		return None


	def get_course_videos(self, course):
		"""gets all the videos and their titles from a course page
		   and adds them to that course's videos dict"""
		response = self.get(course.url)

		if not response:
			return

		tree = html.fromstring(response.text)
		base_url = "http://teamtreehouse.com"
		link_pool = tree.xpath("//div[@class='achievement-steps']/ul/li/a")

		i = 1
		# go through each one of the links on the course home page, if it's a video add to the videos dict
		for video in link_pool:
			try:
				if "video" in video.xpath("span/@class")[0]:
					course.videos[str(i) + " - " + video.xpath("strong/text()")[0].replace("/", " ")] = base_url + video.xpath("@href")[0]
					i += 1
			except IndexError:
				print "Index Error when finding videos for", course.title
		return course.videos


	def get_video_source(self, course, format):
		"""gets the source of every video for a given course and puts the url
		   back into that course's video dict"""
		format = 1 if format != 'webm' else 0

		no_vids = len(course.videos)
		i = 0
		for video, url in course.videos.items():
			response = self.get(url)

			if response:
				i +=1
				status = "\rGetting Source URLs for: {0}\t [{1}/{2}]".format(course.title, i, no_vids)
				stdout.write(status)
				stdout.flush()
				tree = html.fromstring(response.text)
				course.videos[video] = tree.xpath("//video/source")[format].attrib['src']
		print ""
		return course.videos


	def download_all_videos(self, language, format):
		"""downloads videos for every course a programming language has"""
		# for each course find all the videos in that course
		for course in self.tracks[language]:
			print "Finding videos for: {0}".format(course)
			if course.category == 'workshop':
				course.videos[course.title] = course.url
			else:
				self.get_course_videos(course)

		# for each video in a course, find it's source url
		for course in self.tracks[language]:
			self.get_video_source(course, format)

		# for each course for a given programming language, download all the videos
		for course in self.tracks[language]:
			d.download_course(course)


	def download_course_videos(self, course, format):
		""" downloads all the videos for one course"""
		# workshops only have 1 video, so we can skip the call to
		# get_course_videos()
		if course.category == 'workshop':
			course.videos[course.title.replace("/", " ")] = course.url
			self.get_video_source(course, format)
			d.download_course(course)
			return

		# get video links from course page
		print "Finding videos for: {0}".format(course)
		self.get_course_videos(course)
		# get the source for each video
		self.get_video_source(course, format)
		# download it
		d.download_course(course)