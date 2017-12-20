from techmo_dictation_pathfinder_pyclients.audio_provider import get_audio
from techmo_dictation_pathfinder_pyclients.dictation_client import DictationClient
from address_provider import AddressProvider
import grpc

if __name__ == '__main__':
    ap = AddressProvider()
    address = ap.get("dictation")
    dc = DictationClient(address)

    # Read wave file
    wave_filepath = "waves/example.wav"
    audio = get_audio(wave_filepath)

    # Run Pathfinder
    try:
        results = dc.recognize(method="sync", audio=audio)
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