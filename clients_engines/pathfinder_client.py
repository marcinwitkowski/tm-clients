#!/usr/bin/env python3
#coding=utf-8

import argparse
import os
import threading
import time
import wave

import grpc
import clients_engines.pathfinder_pb2 as pb
import clients_engines.pathfinder_pb2_grpc as pf_grpc

from clients_engines.transcription_sanitizer import sanitize

"""
    Pathfinder Client script.
    Script contains Python class PathfinderClient - utility wrapper for GRPC Pathfinder client.
    Script can be also called from terminal to perform keywords spotting on single wav file
"""

__author__ = "Zbigniew Latka"
__date__ = "5.12.2017"


class RequestIterator:
    """Thread-safe request iterator for streaming recognizer."""

    def __init__(self, audio_content, sampling_rate, phrases, sanitize, delay, frame_len):
        # Iterator data
        self.audio_content = audio_content
        self.sampling_rate = sampling_rate
        self.delay = delay
        self.frame_len = frame_len
        self.phrases = phrases
        self.sanitize = sanitize
        self.frame_samples_size = (self.sampling_rate // 1000) * self.frame_len
        self.request_builder = {
            True: self._initial_request,
            False: self._normal_request
        }
        # Iterator state
        self.lock = threading.Lock()
        self.is_initial_request = True
        self.data_index = 0

    def _initial_request(self):
        config_req = pb.SpotPhraseConfig(phrases=list(map(self.sanitize, self.phrases)), sample_rate=self.sampling_rate)
        phrase_req = pb.SpotPhraseRequest(config=config_req)
        self.is_initial_request = False
        return phrase_req

    def _normal_request(self):
        data = self.audio_content[self.data_index: (self.data_index + self.frame_samples_size)]
        self.data_index += self.frame_samples_size
        if self.data_index >= len(self.audio_content):
            raise StopIteration()
        audio_req = pb.SpotPhraseAudio(content=data)
        phrase_req = pb.SpotPhraseRequest(audio=audio_req)
        return phrase_req

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            time.sleep(float(self.delay / 1000))
            return self.request_builder[self.is_initial_request]()


class PathfinderClient:
    """Utility wrapper for GRPC Pathfinder client which takes care of the setup."""

    def __init__(self, address='localhost:3434', ssl_dir=None, use_sanitizer=True):
        if ssl_dir is not None:
            if not os.path.isdir(ssl_dir):
                raise ValueError("No such directory: %s" % ssl_dir)
            channel = grpc.secure_channel(address,
                                          grpc.ssl_channel_credentials(
                root_certificates=open(os.path.join(ssl_dir, 'ca.crt')).read(),
                private_key=open(os.path.join(ssl_dir, 'client.key'), 'rb').read(),
                certificate_chain=open(os.path.join(ssl_dir, 'client.crt'), 'rb').read()
            ))
        else:
            channel = grpc.insecure_channel(address)
        self.pathfinder_ = pf_grpc.PathfinderStub(channel)
        self.sanitize = sanitize if use_sanitizer else lambda x: x


    def SpotPhrase(self, phrases, audio, sampling_rate):
        """Perform keyword spotting on the given audio data.

        :param phrases: a list of strings to be spotted
        :param audio: bytes-like object with audio samples
        :param sampling_rate: the sampling rate as an int
        :return: SpotPhraseResponse protobuf object
        """
        config_req = pb.SpotPhraseConfig(phrases=list(map(self.sanitize, phrases)), sample_rate=sampling_rate)
        audio_req = pb.SpotPhraseAudio(content=audio)
        request = pb.SpotPhraseRequest(config=config_req, audio=audio_req)

        return self.pathfinder_.SpotPhrase(request)


    def SpotPhraseStreaming(self, phrases, audio, sampling_rate, delay, frame_len):
        """Perform keyword spotting on the given audio data.

        :param phrases: a list of strings to be spotted
        :param audio: bytes-like object with audio samples
        :param sampling_rate: the sampling rate as an int
        :param delay: delay in milliseconds between sending next frame
        :param frame_len: length of single audio frame in milliseconds
        :return: SpotPhraseResponse protobuf object
        """
        requests_iterator = RequestIterator(audio_content=audio, sampling_rate=sampling_rate,
                                  phrases=phrases, sanitize=self.sanitize, delay=delay, frame_len=frame_len)
        recognitions = self.pathfinder_.SpotPhraseStreaming(requests_iterator)
        return recognitions


    def SpotPhraseBidirectionalStreaming(self, phrases, audio, sampling_rate, delay, frame_len):
        """Perform keyword spotting on the given audio data.

        :param phrases: a list of strings to be spotted
        :param audio: bytes-like object with audio samples
        :param sampling_rate: the sampling rate as an int
        :param delay: delay in milliseconds between sending next frame
        :param frame_len: length of single audio frame in milliseconds
        :return: An iterator of SpotPhraseResponse protobuf objects
        """
        requests_iterator = RequestIterator(audio_content=audio, sampling_rate=sampling_rate,
                                            phrases=phrases, sanitize=self.sanitize, delay=delay, frame_len=frame_len)
        recognitions_iterator = self.pathfinder_.SpotPhraseBidirectionalStreaming(requests_iterator)
        return recognitions_iterator


    def RunPathinder(self, method, phrases, audio, sampling_rate, delay=200, frame_len=200):
        if method == 'sync':
            return (self.SpotPhrase(phrases, audio, sampling_rate), )
        elif method == 'streaming':
            return (self.SpotPhraseStreaming(phrases, audio, sampling_rate, delay, frame_len), )
        elif method == 'bidirectional_streaming':
            return self.SpotPhraseBidirectionalStreaming(phrases, audio, sampling_rate, delay, frame_len)
        else:
            raise ValueError("Unknown recognition method: {}".format(method))


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser("Pathfinder service client. Sends wave file and list of phrases to spot and displays results. Requires SSL certificates in the 'ssl' directory.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--ssl_dir', default=None, help='Path to ssl directory')
    parser.add_argument('-w', '--wave', default='audio.wav', help='Path to the WAVE file.')
    parser.add_argument('-p', '--phrases', default='phrases.txt', help='Text file with one phrase per line.')
    parser.add_argument('-a', '--address', default='localhost:3434', help='Address of the service with port. Example 0.0.0.0:1234 .')
    parser.add_argument('-m', '--method', default='streaming', help='Recognition method: sync or streaming')
    parser.add_argument('-t', '--transcription', action='store_true', help='Prints transcription of audio')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show full stats of found keywords')
    parser.add_argument('-c', '--crop_wave_dir', default=None, help='Path to directory where cropped waves will be stored')
    parser.add_argument('--delay', default=0, help='delay in milliseconds between sending next frame in streaming mode')
    parser.add_argument('--frame_len', default=1000, help='length of single audio frame in milliseconds in streaming mode')
    args = parser.parse_args()

    pf = PathfinderClient(args.address, args.ssl_dir)

    # Read phrases
    with open(args.phrases, 'r', encoding='utf-8') as f:
        phrases = list(map(str.strip, f.readlines()))

    # Read audio
    with wave.open(args.wave) as f:
        sampling_rate = f.getframerate()
        sample_width = f.getsampwidth()
        audio = f.readframes(f.getnframes())

    # Build request
    print("Searching for phrases:")
    print(*phrases, sep='\n')
    print("in file:", args.wave)

    # Get response and print results
    try:
        response_iterator = pf.RunPathinder(args.method,
                                            phrases,
                                            audio,
                                            sampling_rate,
                                            int(args.delay),
                                            int(args.frame_len))
    except grpc.RpcError as e:
        print("[Server-side error] Received following RPC error from the Pathfinder service:", str(e))
        import sys
        sys.exit(1)

    for idx, response in enumerate(response_iterator):
        if not len(response.phrases):
            print("No phrases detected.")
        else:
            print("Found:")
            spotted_phrases = sorted(({'start': spotted.start, 'end': spotted.end, 'phrase': spotted.phrase,
                                       'score': spotted.score} for spotted in response.phrases),
                                     key=lambda k: (k['start'], k['score']))
            for idx, spotted in enumerate(spotted_phrases):
                if args.verbose:
                    print("{} - [ {} ms - {} ms ]\t{} ({:.1f})".format(idx, spotted['start'], spotted['end'],
                                                                       spotted['phrase'], spotted['score']))
                else:
                    print("{} - [ {} ms - {} ms ]\t{}".format(idx, spotted['start'], spotted['end'], spotted['phrase']))
                if args.crop_wave_dir is not None:
                    os.makedirs(args.crop_wave_dir, exist_ok=True)
                    # Write cropped audio
                    out_wav = os.path.join(args.crop_wave_dir, "{}_{}.wav".format(idx, (spotted['phrase'][0:32])))
                    with wave.open(args.wave, 'rb') as f_in:
                        with wave.open(out_wav, 'wb') as f_out:
                            f_in.setpos(round(spotted['start']*sampling_rate/1000))
                            f_out.setparams((1, sample_width, sampling_rate, 0, 'NONE', 'not compressed'))
                            f_out.writeframes(f_in.readframes(int((spotted['end']-spotted['start'])*sampling_rate/1000)))

        if args.transcription:
            if not len(response.transcription):
                print("No words recognized.")
            else:
                print("Recognized:")
                for idx, recognized in enumerate(response.transcription):
                    print("{} - [ {} ms - {} ms ]\t{}".format(idx, recognized.start, recognized.end, recognized.transcript))
