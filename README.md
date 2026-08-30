# gallery-dl wrapper

### works on:
- win10 Version 22h2 (19045.6466)

### with:
- python 3.14 -> https://www.python.org/downloads/
- gallery-dl 1.32.9 -> https://github.com/mikf/gallery-dl#installation
- optional (yt-dlp), if videos are wanted aswell -> 

### install:
- python -> https://www.python.org/downloads/
- gallery-dl -> https://github.com/mikf/gallery-dl#installation
- do: ```git clone https://codeberg.org/lazukakabra/gdl.git``` where you wish the files to be or ```download as zip``` and extract where you wish the files to be.
- if yt-dlp needed aswell, see: https://codeberg.org/lazukakabra/ytdlp#install

when the script is run for the first time it will ask for locations to save files which is stored in a file it creates in the same directory as the script. to change the paths, edit the file gdl_paths.txt or delete it and rerun script.

## gallery-dl.conf
keep this file alongside ```gallery-dl.py```.  
config file for gallery-dl itself, provided is the one I use which has a save file setup for instagram and pinterest.  
for edit options etc. see https://github.com/mikf/gallery-dl#configuration

## gdl.bat - calling script with specific user set command/alias
### for win10
point of the file ```gdl.bat``` is to facilitate calling, in this case ```gdl```, in cmd from anywhere which will execute ```gallery-dl.py```.
to do so however the file location have to be added to environment variables and the file has to be edited to point to ```gallery-dl.py``` location.
1. place ```gdl.bat``` in eg. ```C:\tools``` or another created-by-you folder or alternatively, leave it in the same folder as the script above.
2. edit file (with text editor) and replace ```path\to\gallery-dl.py``` with ```your path\gallery-dl.py```.
3. add the folder to ```path environment variables```
   - environment variables -> mark PATH in user if only for that user or system for everybody and hit edit -> hit New and enter the path to the bat file, eg. ```C:\tools```.

### for linux
the file ```gdl.bat``` is not needed for linux.  
instead, simply add the following to your bash profile, or whatever else shell, terminal whatever you run. if you run something else you can probably figure this out on your own np. if you did not need/want venv when installing with pip then:  
  ```echo "alias ytdlp='python3 /full/path/to/gallery-dl.py'" >> ~/.bashrc```  
else do for venv:  
  ```echo "alias ytdlp='cd path/to/gallery-dl.py && source venv/bin/activate && python3 gallery-dl.py && deactivate && cd $OLDPWD'```  
which adds a new line in .bashrc with the alias which when you call ytdlp will:  
- move terminal directory to your file
- activate an already created virtual environment named venv
- execute the script
- deactivate the venv when you quit the script
- lastly it returns the terminal to the previous working directory, wherever your terminal was before

then restart your terminal or do:  
  ```source ~/.bashrc```  
which should refresh the terminal with the new settings set in the file.  
you should now be able to call ```gdl``` (or whatever command you set instead) from your terminal and it will start the script.  

### other OS
not a damn clue