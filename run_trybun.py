#!/usr/bin/env python3
# coding=utf-8

from techmo_trybun_pyclient import TTS_pb2
from techmo_trybun_pyclient.wave_saver import WaveSaver
from address_provider import AddressProvider
import grpc

if __name__ == '__main__':
    # Config:
    output_wave_file = 'tts_output.wav'
    ap = AddressProvider()
    address = ap.get("trybun")
    sampling_rate = 44100
    input_text = "Ala ma kota i chciałaby zaliczyć Technologię Mowy"

    # Establish GRPC channel
    channel = grpc.insecure_channel(address)
    stub = TTS_pb2.TTSStub(channel)

    # Synthesis request
    config = TTS_pb2.SynthesizeConfig(sample_rate_hertz=44100)
    request = TTS_pb2.SynthesizeRequest(text=input_text, config=config)
    ws = WaveSaver()
    for response in stub.Synthesize(request):
        if response.HasField('error'):
            print("Error [" + str(response.error.code) + "]: " + response.error.description)
            break
        else:
            if ws._samplerate:
                if ws._samplerate != response.audio.sample_rate_hertz:
                    raise RuntimeError("Sample rate does not match previously received")
            else:
                ws.setFrameRate(response.audio.sample_rate_hertz)
            ws.append(response.audio.content)
            if response.audio.end_of_stream:
                    ws.save(output_wave_file)
    ws.clear()
