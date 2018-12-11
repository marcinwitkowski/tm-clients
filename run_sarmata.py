#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sarmata.sarmata_client import validate_recognition_settings, create_audio_stream, print_results
from sarmata.service.sarmata_settings import SarmataSettings
from sarmata.service.sarmata_recognize import SarmataRecognizer
from address_provider import AddressProvider
from os.path import join as opjoin
import sys


class SarmataArgs:
    address = None                      # IP address and port (address:port) of a service the client will connect to.
    define_grammar = False              # Defines a new grammar to be cached by the service under ID given by `--grammar-name` option from data given by `--grammar` option.
    grammar_name = ''                   # Name (ID) of the grammar in the service's grammar cache.
    grammar = None                      # SRGS grammar file (ABNF or XML format accepted).
    max_alternatives = 3                # Maximum number of recognition hypotheses to be returned.
    mic = False                         # Use microphone as an audio source (instead of wave file).
    no_input_timeout = 5000             # MRCP v2 no input timeout [ms].
    no_match_threshold = 0.2            # Confidence acceptance threshold.
    recognition_timeout = 10000         # MRCP v2 recognition timeout [ms].
    session_id = None                   # Session ID to be passed to the service. If not specified, the service will generate a default session ID itself.
    service_settings = None             # Semicolon-separated list of key=value pairs defining settings to be sent to service via gRPC request.
    speech_complete_timeout = 5000      # MRCP v2 speech complete timeout [ms].
    speech_incomplete_timeout = 3000    # MRCP v2 speech incomplete timeout [ms].
    wave = None                         # Path to wave file with speech to be recognized. Should be mono, 8kHz or 16kHz.

    def __init__(self, wav_filepath=None, grammar=None):
        ap = AddressProvider()
        if grammar:
            self.grammar = grammar
        if wav_filepath:
            self.wave = opjoin(wav_filepath)
        self.address = ap.get("sarmata")


if __name__ == '__main__':
    wave_file = "waves/example_koncert.wav"
    grammar_file = "grammars/koncert.abnf"
    args = SarmataArgs(wave_file, grammar_file)

    settings = SarmataSettings()
    settings.process_args(args)  # load settings from cmd
    if args.grammar is not None:
        settings.load_grammar(args.grammar)

    can_define_grammar = False
    if args.define_grammar:
        if not settings.grammar_name:
            print("Bad usage. Set BOTH grammar_name and grammar file when define grammar is set True.")
            sys.exit(1)
        can_define_grammar = True

    recognizer = SarmataRecognizer(args.address)

    if can_define_grammar:
        define_grammar_response = recognizer.define_grammar(args.grammar_name, settings.grammar)
        if define_grammar_response.ok:
            if args.grammar is None:
                print("Grammar " + args.grammar_name + " removed")
            else:
                print("Grammar " + args.grammar + " defined as " + args.grammar_name)
        else:
            print("Define grammar error: " + define_grammar_response.error)

    # --------------------------
    # recognize section
    # --------------------------
    if args.wave is not None or args.mic:
        validate_recognition_settings(settings)

        with create_audio_stream(args) as stream:
            # generate id
            session_id = stream.session_id()
            settings.set_session_id(session_id)

            results = recognizer.recognize(stream, settings)
            print_results(results, stream)
