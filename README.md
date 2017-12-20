# tm-clients

Project includes Python clients to services used in TM labs . 

## Requirements:
 - VPN connection with AGH network (http://panel.agh.edu.pl/docs/openvpn/) when using outside the network.
 - Installed packages listed in requirements.txt. To install requirements run:
 
 Linux:
 ```bash
 pip install -r requirements.txt
 ```
 
 Windows:
 1. Move to the directory with the used interpreter python.exe.
 2. Run:
 ```bash
 python.exe -m pip install -r path_to_requirements.txt
 ```

 ## Clients

 This package provides API in Python to 4 systems:
 *   **Dictation** - Continuous speech recognition
 *   **Pathfinder** - Key word spotting
 *   **Sarmata** - Speech recognition based on [SRGS](https://www.w3.org/TR/speech-grammar/) grammar
 *   **Trybun** - Text to speech synthesis

Addresses and ports to the systems are stored in the json defined in address_provider.py.

 Contact: witkow@agh.edu.pl
