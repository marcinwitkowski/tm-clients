#!/usr/bin/env python3
# coding=utf-8

import argparse
import wave
import grpc
import clients_engines.cloud_speech_extended_pb2_grpc as speech_grpc
from clients_engines.grpc_streaming_recognize import StreamingRecognizer
from clients_engines.grpc_sync_recognize import SyncRecognizer

"""
    Dictation Client script.
    Script contains Python class DictationClient - utility wrapper for GRPC Dictation client.
    Script can be also called from terminal to perform speech recognition on single wav file
"""

__author__ = "Marcin Witkowski, based on Zbyszek Latka code for Pathfinder Service"
__date__ = "5.12.2017"


class DictationClient:
    """Utility wrapper for GRPC Dictation client which takes care of the setup."""

    def __init__(self, address='localhost:3434'):
        channel = grpc.insecure_channel(address)
        self._dictation_service = speech_grpc.SpeechStub(channel)

    def recognise(self, method, audio):
        """
        Recognises speech in given audio.
        :param method: recognition method: sync or streaming
        :param audio: pydub.AudioSegment object
        :return: list of dict {transcript: =>, confidence: => }
        """
        if method == 'sync':
            service = SyncRecognizer(self._dictation_service)
        elif method == 'streaming':
            service = StreamingRecognizer(self._dictation_service)
        else:
            raise ValueError("Unknown recognition method: {}".format(method))
        results = service.recognize(audio=audio)
        return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send a wave to the dictation service and receive transcription.')
    parser.add_argument('wave', help='Wave file to send.')
    parser.add_argument('-a', '--address', default='localhost:2435', help='Address of the dictation service.')
    args = parser.parse_args()

    # Read audio
    with wave.open(args.wave) as f:
        sampling_rate = f.getframerate()
        audio = f.readframes(f.getnframes())
    print(f"Read file \"{args.wave}\" with sampling rate {sampling_rate} and {len(audio)} bytes of data.")

    # Setup connection
    channel = grpc.insecure_channel(args.address)
    dictation = speech_grpc.SpeechStub(channel)
    print(f"Setup connection with dictation service at address {args.address}")

    # Stream audio for recognition
    request_iterator = RequestIterator(audio, sampling_rate, dotdict({
        'frame_len': 1000,
        'delay': 0,
        'time_offsets': False,
        'single_utterance': False,
        'no_interim_results': True,
        'language': 'pl-PL'
    }))
    recognitions_iterator = dictation.StreamingRecognize(request_iterator)

    # Present results as they come
    for recognition in recognitions_iterator:
        if len(recognition.results) == 0:
            print("- (... received empty results ...)")
            continue
        for result in recognition.results:
            if not result.is_final:
                continue

            if len(result.alternatives) == 0:
                print("- (... received results with empty alternatives ...)")
                continue

            best_alternative = result.alternatives[0]

            # check transcript
            if len(best_alternative.transcript) == 0:
                print("(... received empty recognition ...)")
                continue

            # determine times
            try:
                begin = best_alternative.words[0].start_time
                end = best_alternative.words[-1].end_time
                time_str = f"[{begin}ms - {end}ms]"
            except:
                time_str = ""

            # determine confidence
            confidence = f"({best_alternative.confidence:.2f})" if best_alternative.confidence != 0. else ""

            print("-", time_str, best_alternative.transcript, confidence)

