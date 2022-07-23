# Overview
This is a PyQt Designer series to create Utility projects using below technologies.
1. python 3.7
2. PyQt Designer

Tutorial : [PyQt Designer Tutorial](https://www.pythonguis.com/pyqt5-tutorial/)

## Setup
- Execute below command to install required modules.
    `pip install -r requirements.txt`

## Commands
- Convert <filename>.ui file to <filename>.py
    `pyuic5 -x <filename>.ui -o <filename>.py`
- Command to create executable file.
	`pyinstaller -n "<filname>" --noconsole --onefile <filename>.py`
    > where 
	> -n : name of executable file
	> --noconsole : hide black cmd which comes during execution of program
	> --onefile : will create only single execution file 

### Project Details
1. **Project** : `timezone-clock`
    - This project shows the live current datetime of each and every timezone. 
 