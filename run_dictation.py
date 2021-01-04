#!/usr/bin/env python3
# coding=utf-8
from dictation.dictation_client import create_audio_stream, print_results
from dictation.service.dictation_settings import DictationSettings
from dictation.service.streaming_recognizer import StreamingRecognizer
from address_provider import AddressProvider
from dictation.VERSION import DICTATION_CLIENT_VERSION
import os.path as op


class DictationArgs:

    def __init__(self, wav_filepath=None, ssldir=None):
        if wav_filepath:
            self.wave = op.join(wav_filepath) # Path to wave file with speech to be recognized. Should be mono, 8kHz or 16kHz.
        else:
            self.wave = None
        if ssldir:
            assert op.isdir(ssldir) & \
                   op.isfile(op.join(ssldir, "client.crt")) & \
                   op.isfile(op.join(ssldir, "client.key")) & \
                   op.isfile(op.join(ssldir, "ca.crt"))
        self.ssl_directory = ssldir
        ap = AddressProvider()
        self.address = ap.get("dictation")
        self.grpc_timeout = 0 #Timeout in milliseconds used to set gRPC deadline - how long the client is willing to wait for a reply from the server.
                              # If not specified, the service will set the deadline to a very large number.
        self.interim_results = False  # If set - messages with temporal results will be shown.
        self.mic = False  # Use microphone as an audio source (instead of wave file).
        self.no_input_timeout = 5000  # MRCP v2 no input timeout [ms].
        self.recognition_timeout = 15000  # MRCP v2 recognition timeout [ms].
        self.session_id = None  # Session ID to be passed to the service. If not specified, the service will generate a default session ID itself.
        self.single_utterance = False  # If set - the recognizer will detect a single spoken utterance.
        self.speech_complete_timeout = 5000  # MRCP v2 speech complete timeout [ms].
        self.speech_incomplete_timeout = 6000  # MRCP v2 speech incomplete timeout [ms].
        self.time_offsets = False  # If set - the recognizer will return also word time offsets.
        self.context_phrase = "" # Specifies which context model to use.


if __name__ == '__main__':
    print("Dictation ASR gRPC client " + DICTATION_CLIENT_VERSION)

    ssldir = "ssl"
    args = DictationArgs("waves/example.wav", ssldir)
    #args = DictationArgs()

    if args.wave is not None or args.mic:
        with create_audio_stream(args) as stream:
            settings = DictationSettings(args)
            recognizer = StreamingRecognizer(args.address, args.ssl_directory, settings)

            print('Recognizing...')
            results = recognizer.recognize(stream)
            print_results(results)
