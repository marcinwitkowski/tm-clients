from clients_engines.audio_provider import get_audio
from clients_engines.dictation_client import DictationClient
import grpc

if __name__ == '__main__':
    address = "149.156.121.122:2789"
    dc = DictationClient(address)

    # Read wave file
    wave_filepath = "example.wav"
    audio = get_audio(wave_filepath)

    # Run Pathfinder
    try:
        results = dc.recognise(method="sync", audio=audio)
    except grpc.RpcError as e:
        print("[Server-side error] Received following RPC error from the Pathfinder service:", str(e))
        import sys
        sys.exit(1)

    for idx, response in enumerate(results):
        if not len(response):
            print("No phrases detected.")
        else:
            print("Transcription:")
            print("\"{}\"".format(response['transcript']))