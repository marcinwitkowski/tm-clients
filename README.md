# tm-clients

Project includes Python clients to services provided by [Techmo](http://techmo.pl/) exclusively for TM labs. 

## Setup
 Install packages listed in requirements.txt to run both `run_tts.py` and `run_dictation.py`.  
 ### Linux:
 ```bash
 pip install -r requirements.txt
 ```
 
 ### Windows (with virtualenv):
 1. Change the directory with the used interpreter (`python.exe`).
 2. Run:
 ```bash
 python.exe -m pip install -r path_to_requirements.txt
 ```
 or use Linux command in Anaconda Shell
 or use the Terminal in Pycharm to install as in Linux using the virtualenvironment created in this IDE.
### Final Remarks

* Client scripts has been tested with Python 3.10 using PyCharm on Windows. It is recommended to create [virtual environment](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html) for the project.
* When using PyCharm remember to mark directories *dictation* and *tts* as "Sources Root".  

 ## Clients

 This package provides API in Python to 3 systems:
 *   **Dictation** - Continuous speech recognition
 *   **TTS** - Text to speech synthesis
 
Original command line clients are provided with [Techmo GitHub](https://github.com/techmo-pl). 
Addresses and ports to the systems are stored in the json defined in address_provider.py and should not be included in any public repository.


 Contact: witkow at agh.edu.pl
