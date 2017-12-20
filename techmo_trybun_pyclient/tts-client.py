import TTS_pb2
import grpc
import os
from wave_saver import WaveSaver
from optparse import OptionParser
import codecs
def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-s", "--service", dest="service", default="",
                  help="sets service IP address and port; provide as string \"address:port\", e.g. \"127.0.0.1:4321\"")
    parser.add_option("-t", "--text", dest="text2synth", default="",
                  help="sets text in an orthographic form for the synthesis")
    parser.add_option("-i", "--input_text_file", dest="inputfile", default="",
                  help="reads text from TEXT_FILE (should be in an orthographic form) for synthesis") 
    parser.add_option("-o", "--output_file_prefix", dest="prefix", default="",
                   help="prefix added to ouput filename (default: '')")                      
    parser.add_option("-p", "--print_output", action="store_true", dest="print", default=False,
                  help="print ouptut wave instead of saving it into a file")
    parser.add_option("-f", "--sample_rate", dest="sample_rate", default=44100,
                  help="sets desired output audio's sampling frequency in hertz")
    # Parse and validate options
    (options, args) = parser.parse_args()

    # Check if service address and port are provided
    if len(options.service) == 0:
        raise RuntimeError("No service address and port provided.")

    # Input text determination
    input_text = ""
    if len(options.inputfile) > 0:
        with codecs.open(options.inputfile, encoding='utf-8', mode="r") as fread:  
            input_text = fread.read()
    elif len(options.text2synth) > 0:
        input_text = options.text2synth  
    else:
        raise RuntimeError("Empty input string for synthesis")
                    
    # Output file determination
    wavefilename = os.path.join(options.prefix+'out.wav')
    
    # Establish GRPC channel
    channel = grpc.insecure_channel(options.service)
    stub = TTS_pb2.TTSStub(channel)

    # Synthesis request
    config = TTS_pb2.SynthesizeConfig(sample_rate_hertz=int(options.sample_rate))
    request = TTS_pb2.SynthesizeRequest(text=input_text, config=config)
    ws = WaveSaver()
    for response in stub.Synthesize(request):
        if response.HasField('error'):
            print("Error [" + str(response.error.code) + "]: " + response.error.description)
            break
        else:
            if ws._framerate:
                if ws._framerate != response.audio.sample_rate_hertz:
                    raise RuntimeError("Sample rate does not match previously received")
            else:
                ws.setFrameRate(response.audio.sample_rate_hertz)
            ws.append(response.audio.content)
            if response.audio.end_of_stream:
                if options.print:
                    ws.print()
                else:
                    ws.save(wavefilename)
    ws.clear()

main()



