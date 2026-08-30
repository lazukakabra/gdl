#!/usr/bin/env python
''' use the script to check if dependencies for gallery-dl.py
exists on system'''

import os
from importlib.util import find_spec
from importlib.metadata import version
from shutil import which
from subprocess import run
from platform import uname

# set requirements to check here
libs = ['requests', 'gallery_dl']

# optional dependencies. needed if gallery-dl is requested to download video
# which relies on yt-dlp which in turn needs the rest for some, not all, formats
# there are more optional dependencies, add them if needed, see:
# https://github.com/mikf/gallery-dl#dependencies
opt_libs = ['yt_dlp', 'yt_dlp_ejs', 'mutagen']	# python libs
opt_exe_fftools = ['ffmpeg', 'ffprobe']	# fftools gives alot of version info, separated
opt_exe = ['deno']	# installed on system

# status dict will be key=name and value=[requirement yes or no, lib or exe, version]
# if no version, eg. "name" wasnt found. then save '' (empty str)
status = {}

# used as true/false with report() when called by other scripts.
# also used as giving a total in table print
not_found_req = 0
not_found_opt = 0

# prefix for printing, added to status dict when making entry to dict
l, e, r, o = '[LIB]', '[EXE]', '[REQUIRED]', '[OPTIONAL]'

# checks for python libs
def check_lib(status_dict, list_of_libs, dependency, typ, missing=0):
	for lib in list_of_libs:
		status_dict[lib] = [dependency, typ, '']
		if find_spec(lib) is None:
			missing += 1
		else:
			status_dict[lib][-1] = version(lib)
	return status_dict, missing

# for fftools, no direct way to get only version
# so it has to be dug out of a small wall of text
def check_fftools(status_dict, list_of_exes, dependency, typ, missing=0):
	for exe in list_of_exes:
		status_dict[exe] = [dependency, typ, '']
		if bool(which(exe)):
			exe_version = run([exe, '-version'], capture_output=True, text=True).stdout
			vers = ''.join(char for char in exe_version)
			vers = vers.split(' Copyright')[0].split('version ')[1]
			status_dict[exe][-1] = vers
		else:
			missing += 1
	return status_dict, missing

# checks for executeables which prints with "name -version" as "<name> <version>"
def check_exe(status_dict, list_of_exes, dependency, typ, missing=0):
	for exe in list_of_exes:
		status_dict[exe] = [dependency, typ, '']
		if bool(which(exe)):
			exe_version = run([exe, '-version'], capture_output=True, text=True).stdout
			vers = ''.join(char for char in exe_version)
			vers = vers.strip('\n').split('deno ')[1]
			status[exe][-1] = vers
		else:
			missing += 1
	return status_dict, missing

status, n1 = check_lib(status, libs, r, l)
status, n2 = check_lib(status, opt_libs, o, l)
status, n3 = check_fftools(status, opt_exe_fftools, o, e)
status, n4 = check_exe(status, opt_exe, o, e)

not_found_req += n1
not_found_opt += n2+n3+n4

# report func to be called from ytdlp.py, will not work if called from py console
# returns true if any requirements are not found
def report():
	return bool(not_found_req)

def main():
	# foreground color codes
	os.system('color') # needed for ANSI color codes to work (win10)
	GREEN, YELLOW, DARK_CYAN, RED_BG = '\033[92m', '\033[93m', '\033[36m', '\033[41m'
	RESET = '\033[0m'  # This resets the color back to default

	# color input and reset cmd style to default
	def color(color:str, arg:str) -> str:
		return color+arg+RESET

	# \t, indented print
	def print2(*arg):
		for element in arg:
			print(f'\t{element}')

	# printing status msgs
	print2('', color(DARK_CYAN, 'requirements table for gallery-dl.py'))

	header = color(YELLOW, f'{"[status]":<11}{"[dependency]":<14}{"[type]":<7}{"name":14}version')
	separater_row = '-'*len(header)
	print2(separater_row, header, separater_row)

	for pkg, values in status.items():
		dep, typ, ver = values
		if not ver:
			print2(color(RED_BG, f'{"[- FOUND]":<11}{dep:<14}{typ:<7}{pkg:14}{ver}'))

		else:
			print2(color(GREEN, f'{"[+ FOUND]":<11}{dep:<14}{typ:<7}{pkg:14}{ver}'))

	print2(separater_row)
	print2(color(YELLOW, f'missing {not_found_req} required dependencies'),
		color(YELLOW, f'missing {not_found_opt} required dependencies'))
	print2(color(DARK_CYAN, f'your system >> ')+uname()[0])

if __name__ == '__main__':
	main()