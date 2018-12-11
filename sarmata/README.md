Techmo Sarmata ASR - python client.

Stream audio from wave or microphone to the ASR engine and prints all reponses:
 - status, 
 - transcription, 
 - semantic interpretation, 
 - confidence,
(when applicable).

Dependencies (listed in requirements.txt):
 - grpcio
 - grpcio-tools
 - protobuf
 - pydub
 - pyaudio

`pyaudio` requires development packages of Python and PortAudio:
```
sudo apt-get install python3.5-dev portaudio19-dev
```

To regenerate sources from `.proto`, run (virtualenv must be enabled before):
```
./make_proto.sh
```
This might be required when using other gRPC or Protocol Buffers version.

To run:
 - Use python 3.5 with virtual environment and install required packages.
```
virtualenv -p python3.5 venv
source venv/bin/activate
pip install -r requirements.txt
```


**Run (wave):**
```
python sarmata_client.py --service-address ip:port --grammar grammar_file.xml --wave-path audio.wav
```
 
**Run (microphone):**
```
python sarmata_client.py --service-address ip:port --grammar grammar_file.xml --mic
```
 
There is a possibility to define grammar before recognitions:
```
python sarmata_client.py --service-address ip:port --define-grammar --grammar grammar_file.xml --grammar-name simple_grammar
```
and then run recognition:
```
python sarmata_client.py --service-address ip:port --grammar-name simple_grammar --wave-path audio.wav
```
or
```
python sarmata_client.py --service-address ip:port --grammar-name simple_grammar --mic
```

To delete a cached grammar, run with `--define-grammar` and `--grammar-name` options only (no `--grammar` option):
```
python sarmata_client.py --service-address ip:port --define-grammar --grammar-name grammar_to_delete
```

Usage:
```
usage: sarmata_client.py [-h] --service-address ADDRESS [--define-grammar]
                         [--grammar-name GRAMMAR_NAME] [--grammar GRAMMAR]
                         [--wave-path WAVE] [--mic]
                         [--service-settings SERVICE_SETTINGS]
                         [--max-alternatives MAX_ALTERNATIVES]
                         [--no-match-threshold NO_MATCH_THRESHOLD]
                         [--speech-complete-timeout SPEECH_COMPLETE_TIMEOUT]
                         [--speech-incomplete-timeout SPEECH_INCOMPLETE_TIMEOUT]
                         [--no-input-timeout NO_INPUT_TIMEOUT]
                         [--recognition-timeout RECOGNITION_TIMEOUT]

optional arguments:
  -h, --help            show this help message and exit
  --service-address ADDRESS
                        IP address and port (address:port) of a service the
                        client will connect to.
  --define-grammar      Defines a new grammar to be cached by the service
                        under ID given by `--grammar-name` option from data
                        given by `--grammar` option.
  --grammar-name GRAMMAR_NAME
                        Name (ID) of the grammar in the service's grammar
                        cache.
  --grammar GRAMMAR     SRGS grammar file (ABNF or XML format accepted).
  --wave-path WAVE      Path to wave file with speech to be recognized. Should
                        be mono, 8kHz or 16kHz.
  --mic                 Use microphone as an audio source (instead of wave
                        file).
  --service-settings SERVICE_SETTINGS
                        Semicolon-separated list of key=value pairs defining
                        settings to be sent to service via gRPC request.
  --max-alternatives MAX_ALTERNATIVES
                        Maximum number of recognition hypotheses to be
                        returned.
  --no-match-threshold NO_MATCH_THRESHOLD
                        Confidence acceptance threshold.
  --speech-complete-timeout SPEECH_COMPLETE_TIMEOUT
                        MRCPv2 Speech-Complete-Timeout in milliseconds.
  --speech-incomplete-timeout SPEECH_INCOMPLETE_TIMEOUT
                        MRCPv2 Speech-Incomplete-Timeout in milliseconds.
  --no-input-timeout NO_INPUT_TIMEOUT
                        MRCPv2 No-Input-Timeout in milliseconds.
  --recognition-timeout RECOGNITION_TIMEOUT
                        MRCPv2 Recognition-Timeout in milliseconds.
```
