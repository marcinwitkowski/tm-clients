# Python implementation of Dictation ASR gRPC client.



## How to prepare virtual environment and run Dictation Client on Windows 10


### Prerequisites

If Python is not installed on your system, download the Python 3.10 installer from: https://www.python.org/downloads/windows/ and install.
Remember to mark checkbox:
```
Add Python 3.10 to PATH
```


Start the PowerShell with `Run as Administrator`.

Temporarily change the PowerShell's execution policy to allow scripting:

```
Set-ExecutionPolicy RemoteSigned
```
then confirm your choice.

Navigate into the project root directory, eg.:

```
cd C:\Users\Jan_Kowalski\Desktop\techmo-dictation-client-python\
```

Create virtual environment for project:and install required packages:

```
python -m venv .venv
```

Activane newly created virtual environment:
```
.\.venv\Scripts\activate
```

Install required packages:
```
pip install -r requirements.txt
```


To switch back PowerShell's execution policy to the default, use command:

```
Set-ExecutionPolicy Restricted
```



## Usage

Basic request:

```
python dictation_client.py --service-address ADDRESS --audio-path AUDIO_FILE_NAME
```


For example:

```
python dictation_client.py --service-address "demo.devtechmo.pl:25510" --audio-path test.wav
```
Each request must be provided with the address of the service and the audio source (wav/ogg/mp3 file or microphone).



To get list of all available options, use:
```
python dictation_client.py --help
```