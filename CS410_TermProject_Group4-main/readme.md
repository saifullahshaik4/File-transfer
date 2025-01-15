# Term Project - SFTP Application

**Group 4**

_CS410/510_

**Portland State University**

_Summer 2024_

## Development Notes:

- before working please start the virtual environment from visual studio code, enter venv\Scripts\activate into the terminal (from the base directory)
- The kanban board can be found under the projects tab of this repo.
- to run unit tests: first be in the base directory, ensure the venv is active, then run pytest tests/unit_tests.py ![image](https://github.com/shortstring/CS410_TermProject_Group4/assets/77479441/cb16e7e9-e691-49a4-9265-eeeea82f0b9e)

## Virtual Environment Setup

- Create the venv using "python -m venv venv" (The second venv is the directory name and can be changed, for consistency we have chosen the default name venv)
- Activate the venv using ".\venv\Scripts\activate
- If you are on mac the activate command is "source venv/bin/activate"
- Install requirements "pip install -r requirements.txt"


## SFTP Library Notes

- Many choices, most of which are built on top of paramiko which seems to be the most popular library by far. Paramiko is our chosen library for this reason and its ease of use.
- Documentation can be found here: https://docs.paramiko.org/en/latest/


## Create an Executable

- With the venv active, create a .exe with no console run the command: python .\venv\Scripts\pyinstaller.exe --onefile --noconsole -p ./ gui.py
- To create a .exe that runs with a console: python .\venv\Scripts\pyinstaller.exe --onefile -p ./ gui.py (The console will show stuff you printed to the console.)
- If you want to make the console appluication into an .exe run python .\venv\Scripts\pyinstaller.exe --onefile -p ./ main.py
- After running the command dist/gui.exe should be created .. open from file explorer.