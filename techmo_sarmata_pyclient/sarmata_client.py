#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from utils.wave_loader import load_wave
from service.sarmata_settings import SarmataSettings
from service.sarmata_recognize import SarmataRecognizer
from service.asr_service_pb2 import ResponseStatus
import os


def print_results(responses):
    if responses is None:
        print("Empty results - None object")
        return

    for response in responses:
        if response is None:
            print("Empty results - skipping response")
            continue

        print("Received response with status: {}".format(ResponseStatus.Name(response.status)))

        if response.error:
            print("[ERROR]: {}".format(response.error))

        n = 1
        for res in response.results:
            transcript = " ".join([word.transcript for word in res.words])
            print("[{}.] {} /{}/ ({})".format(n, transcript, res.semantic_interpretation, res.confidence))
            n += 1


if __name__ == '__main__':
    parser = ArgumentParser(description="""Main script for running tests of Techmo Sarmata ASR system""")
    parser.add_argument("--address", help="Techmo Sarmata ASR service")
    parser.add_argument("--wave", help="Wave path, should be mono, 8kHz or 16kHz")
    parser.add_argument("--grammar", help="SRGS grammar file (ABNF or XML format accepted)")
    # Timeouts, settings
    parser.add_argument("--nbest", help="Maximal number of hypotheses", default=3, type=int)
    parser.add_argument("--nomatch", help="Confidence acceptance threshold", default=0.2, type=float)
    parser.add_argument("--speech-complete", help="MRCP v2 speech complete timeout [ms]", default=500, type=int)
    parser.add_argument("--speech-incomplete", help="MRCP v2 speech incomplete timeout [ms]", default=3000, type=int)
    parser.add_argument("--no-input", help="MRCP v2 no input timeout [ms]", default=5000, type=int)
    parser.add_argument("--recognition-timeout", help="MRCP v2 recognition timeout [ms]", default=10000, type=int)

    args = parser.parse_args()
    audio = load_wave(args.wave)

    settings = SarmataSettings()
    settings.process_args(args) # load settings from cmd
    session_id = os.path.basename(args.wave)
    settings.set_session_id(session_id)

    settings.load_grammar(args.grammar)

    recognizer = SarmataRecognizer(args.address)
    results = recognizer.recognize(audio, settings)

    print_results(results)
