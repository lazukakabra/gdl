#!/usr/bin/env python
'''
requirements and made with versions:
[exe] python 3.14.6
[exe] gallery-dl-1.32.9, installed with pip
'''
import os
import subprocess
from shutil import move
import tempfile
import gdl_req_check as grc

# foreground color codes
os.system('color') # needed for ANSI color codes to work (win10)
GREEN, YELLOW, DARK_CYAN, RED_BG = '\033[92m', '\033[93m', '\033[36m', '\033[41m'
RESET = '\033[0m'  # This resets the color back to default

# color wrapping
def color(color, arg:str)->str:
	return color+arg+RESET

# \t, indented print
def print2(*arg):
	for element in arg:
		print(f'\t{element}')

# if directory doesnt exist, create directory and print location
def create_dir(path:str):
	if not os.path.exists(path):
		os.mkdir(path)
		print2(color(DARK_CYAN, 'folder created at: ')+f'{path}')

# finds folder containing files, can differ depending on
# download settings set for different sites in config file
def tree(path:str, folder='')->str:
	if not os.path.isfile(path):
		folder = tree(os.path.join(path, os.listdir(path)[0]), path)
	return folder

# check if filename exists in destination directory, assumes 3 letter extension file
def check_duplicate(name:str, og_name:str, dest_dir:str, dl_dir_tree:str, n=0)->(str, int):
	fname, fext = os.path.splitext(os.path.join(dl_dir_tree, og_name))
	lext = len(fext)+1 
	path_duplicate = os.path.join(dest_dir, dl_dir_tree, name)
	if os.path.exists(path_duplicate):
		name = fname + f' ({n+1})' + fext
		name, n = check_duplicate(name, og_name, dest_dir, dl_dir_tree, n+1)
	return name, n

# download func, needs gallery-dl options and url,
def download(options:dict, url:str):
	flags = ''
	for option in options:
		flags += ' '+option
	subprocess.check_output(f'gallery-dl{flags} {url}')

# get size and return with proper unit
def fsize(fname:str, fopath:str)->str:
	size = os.path.getsize(os.path.join(fopath, fname))
	units = ['B', 'kB', 'MB', 'GB']
	unit_index = 0
	for _ in units[:-1]:
		if size > 1024:
			unit_index += 1
			size = size / 1024.0
	size = str(size)[:5] # return 3 decimals max, ignore rounding
	return f'{size} {units[unit_index]}'

# needs downloaded folder path
def rename_and_move(dir_path:str, download_dir:str):
	# change folders to tmp_dir
	prev_dir = os.getcwd()
	os.chdir(dir_path)

	# find folder structure
	folderpath = tree(os.listdir()[0])
	filenames = os.listdir(folderpath)
	old_filenames = filenames

	print2(color(GREEN, 'downloaded:'), '    folder: '+folderpath)
	for filename in filenames:
		print2(
			'      file: '+filename,
			'      size: '+fsize(filename, folderpath))

	# checking for duplicates in dl_dir and adjusting filenames if found
	duplicates = 0
	fname_duplicates = []
	for i, fn in enumerate(filenames):
		filenames[i], n_duplicate = check_duplicate(fn, fn, download_dir, folderpath)
		if n_duplicate:
			fname_duplicates.append((fn, n_duplicate))
			duplicates += 1

	# if duplicate found, ask to continue, if yes then >>
	# rename and print msg with new name
	if duplicates:
		print2('found '+color(YELLOW, f'{duplicates}')+
			f' out of '+color(DARK_CYAN, f'{len(filenames)}')+' duplicates')
		for fn in fname_duplicates:
			print2(f'found '+color(YELLOW, f'{fn[1]}')+
				' duplicates in destination folder for: ', '  '+fn[0])
		cont = input(color(YELLOW, '  duplicate found, continue? [Y/n] '))
		if cont and cont.lower() not in['y', 'ye', 'yes']:
			print2(color(YELLOW, 'process terminated >> deleting downloaded files...'))
			os.chdir(prev_dir)
			return
		for ofn, fn in zip(old_filenames, filenames):
			os.rename(os.path.join(folderpath, ofn), os.path.join(folderpath, fn))
			print2(color(GREEN,'renamed >> ')+fn)
	else:
		print2('found '+color(YELLOW, '0')+' duplicates in destination folder')

	# ensuring directory exists in destination folder
	create_dir(os.path.join(download_dir, folderpath))

	# moving file(s)
	old_folder_path = os.path.join(dir_path, folderpath)
	new_folder_path = os.path.join(download_dir, folderpath)
	for ofn, fn in zip(old_filenames, filenames):
		ofp = os.path.join(old_folder_path, ofn)
		nfp = os.path.join(new_folder_path, fn)
		move(ofp, nfp)
		print2('', color(GREEN, f'moved >> {fn}'),
		'  from: '+old_folder_path,
		'    to: '+new_folder_path)

	# if log not empty, move from download_dir\logs\ to
	# new_folder_path\logs\filename.log, if multiple files downloaded
	# simply use the 0th index from filenames to name the log
	if os.path.getsize(LOG_FILE_PATH):
		new_log_folder = os.path.join(new_folder_path, LOG_FOLDER)
		create_dir(new_log_folder)
		new_log_path = os.path.join(new_log_path, filenames[0]+'.log')
		move(LOG_FILE_PATH, new_log_path)
		print2(color(RED_BG, 'non-empty log file, saved:'), new_log_path,'')
	else:
		print2(color(GREEN, 'empty log file, deleting...'))
		os.remove(LOG_FILE_PATH)
	os.rmdir(LOG_FOLDER_PATH)

	# move back to prev dir to safely delete temporary directory
	os.chdir(prev_dir)

# gets download folder paths from file if it exists, creates file if it does not
def check_file_for_paths(filename:str)->dict:
	# if file doesnt exist, create it and add file save locations
	script_dir = os.path.dirname(os.path.realpath(__file__))
	prv_dir = os.getcwd()
	os.chdir(script_dir)
	if not os.path.exists(filename):
		print2('[ATTN] >> file containing save locations '+color(RED_BG, 'not')+' found, creating...')
		locations = {}
		while True:
			locations['download'] = input('\t[INPUT] >> enter location to save videos, full path: ')
			for k,v in locations.items():
				print2('\t  '+k+': '+v)
			q = input('\t[INPUT] >> is the above folder correct? [Y/n] ')
			if q and str(q).lower() not in ['y', 'ye', 'yes']:
				continue
			break

		# write to file the entered locations
		with open(filename, 'x') as f:
			for k, v in locations.items():
				f.write(k+' = '+v + '\n')
		print2(color(GREEN, 'created file >> ')+filename)

	# get file paths from filename
	locs = {}
	with open(filename) as f:
		contents = f.read()
	for line in contents.split('\n'):
		if not line: continue
		k, v = line.split(' = ')
		locs[k] = v

	# print locations and return dict
	print2(color(GREEN, 'found ')+f'{filename}, '
		+color(DARK_CYAN, 'download folder set to:'),
		color(DARK_CYAN, '  >> ')+locs['download'],
		f'  to change, edit {filename} or delete it and rerun script.')
	os.chdir(prv_dir)
	return locs

''' FLAGS for gallery-dl, explanations
-d <path>:	exact location for file downloads, leave alone below if its not needed to change
			files will be downloaded to temporary directory first. this is to primarily 
			avoid overwrites and to facilitate easier renaming.
--windows-filenames: force filenames to be Windows-compatible,
					 comment out only if not on windows.
-c <path>: exact location of config file.
-w:	print only warnings and errors.
-q:	activate quiet mode.
'''

## static filenames and paths
# set filename containing save-folder paths
paths_file = 'gdl_paths.txt'

# download
locations = check_file_for_paths(paths_file)
DOWNLOAD_DIR = Rf'{locations['download']}'

# config
CONFIG_NAME = 'gallery-dl.conf'
LOC_THIS_SCRIPT = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(LOC_THIS_SCRIPT, CONFIG_NAME)

# name of log set in config file, set to save at: cwd/logs/log.log
LOG_FILE = R'log.log'
LOG_FOLDER = 'logs'
LOG_FOLDER_PATH = os.path.join(DOWNLOAD_DIR, LOG_FOLDER)
LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, LOG_FILE)

# if -d and/or -c is used below, then remove from main(),
# -d currently set to use temporary directory to avoid
# overwriting potential duplicates
gdl_opts = [
			#f'-d {DL_DIR}',
			f'-c {CONFIG_PATH}',
			'--windows-filenames',
			'-w',
			#'-q ',
			]

def main():
	# checking for requirements with helper script ytdlp_req_check.py
	if not grc.report():
		print2(color(GREEN, 'found')+' all dependencies')
	else:
		grc.main()
		input('press enter to quit')
		quit()

	# to make logs spawn at expected location
	# regardless of where you execute script from
	prv_dir = os.getcwd()
	os.chdir(DOWNLOAD_DIR)

	while True:
		get_url = input(color(DARK_CYAN, '  [gdl] >> enter url or leave empty to exit. '))
		if not get_url:
			os.chdir(prv_dir)
			quit()
		with tempfile.TemporaryDirectory() as tmp_dir:
			gdl_opts.append(f'-d {tmp_dir}')
			download(gdl_opts, get_url)
			rename_and_move(tmp_dir, DOWNLOAD_DIR)
			
if __name__ == '__main__':
	main()