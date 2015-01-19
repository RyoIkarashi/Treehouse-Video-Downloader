import requests
import os
from sys import stdout


def download_Video(url, name, current_video=1, total_videos=1, verbose=True):
	""" downloads a video from a url """
	# defer downloading of the body
	response = requests.get(url, stream=True)

	# if there's not a response, exit. Should probably add some error handling here
	if not response:
		return

	# work out file size in Mbytes. Extension of file is retrieved from content-type
	file_size = round(float(response.headers['content-length']),2) / 1000000
	downloaded = 0
	file_name = name
	file_name = file_name + '.' + response.headers['content-type'].split('/')[1]
	
	# download the body of the response (the video) in chunks of 8192 bytes and write to file
	if verbose:
		with open(file_name, 'wb') as fd:
			for chunk in response.iter_content(8192):
				fd.write(chunk)
				downloaded += len(chunk)
				print_progress(current_video, total_videos, downloaded, file_size)
	else:
		with open(file_name, 'wb') as fd:
			for chunk in response.iter_content(8192):
				fd.write(chunk)

	# close the file and release the connection
	fd.close()
	response.close


def print_progress(current_video, total_videos, downloaded, file_size):
	""" some visual feedback if the user so desires """
	status = ("\rVideo: [{0}/{1}]".format(current_video, total_videos) +
			 " {0:.2f} MB of {1:.2f} MB \t[{2:.2f}%] ".format( 
			 float(downloaded) / 1000000, 
			 file_size, 
			 (float(downloaded) / 1000000 * 100) / file_size ) +
			 "       "
			 )

	stdout.write(status)
	stdout.flush()


def download_course(course):
	""" downloads each of the videos for a course and puts them in the correct directory. """
	print "Downloading all videos for: ", course.title
	
	# make a folder with with the title of the programming language
	if not os.path.exists("videos/" + course.language):
		os.makedirs("videos/" + course.language)

	# make a sub folder with the title of the course
	if not os.path.exists("videos/" + course.language + "/" + course.title):
		os.makedirs("videos/" + course.language + "/" + course.title)

	# change dir to the current course being downloaded
	os.chdir("videos/" + course.language + "/" + course.title)

	# download the videos
	total = len(course.videos.items())
	i = 0
	for title, url in course.videos.items():
		i +=1
		download_Video(url, title, current_video=i, total_videos=total)

	# move back up to videos
	os.chdir("../../..")