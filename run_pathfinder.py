#!/usr/bin/env python3
# coding=utf-8

from techmo_dictation_pathfinder_pyclients.pathfinder_client import PathfinderClient
from address_provider import AddressProvider
import wave
import grpc

if __name__ == '__main__':
    ap = AddressProvider()
    pathfinder_address = ap.get("pathfinder")
    pf = PathfinderClient(pathfinder_address)

    # Define phrases you want to spot
    phrases = ['handel', 'weekend']

    # Read wave file
    wave_filename = "waves/example.wav"
    with wave.open(wave_filename) as f:
        fs = f.getframerate()
        signal = f.readframes(f.getnframes())

    # Run Pathfinder
    try:
        response_iterator = pf.RunPathinder(phrases=phrases, audio=signal, sampling_rate=fs, method="sync")
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
                    print("{} - [ {} ms - {} ms ]\t{}".format(idx, spotted['start'], spotted['end'], spotted['phrase']))