from argparse import ArgumentParser
import codecs
from SARMATA_CLIENT_VERSION import TRIBUNE_CLIENT_VERSION
from call_synthesize import call_synthesize


def main():
    print("Tribune TTS gRPC client " + TRIBUNE_CLIENT_VERSION)

    parser = ArgumentParser()
    parser.add_argument("-s", "--service-address", dest="service", required=True,
                  help="IP address and port (address:port) of a service the client will connect to.", type=str)
    parser.add_argument("-t", "--text", dest="text", default="Techmo Trybun: Syntezator mowy polskiej.",
                  help="Text to be synthesized (in polish).", type=str)
    parser.add_argument("-i", "--input_text_file", dest="inputfile", default="",
                  help="A file with text to be synthesized (in polish).", type=str) 
    parser.add_argument("-o", "--out-path", dest="out_path", default="TechmoTTS.wav",
                   help="Path to output wave file with synthesized audio content.", type=str)
    parser.add_argument("-f", "--sample_rate", dest="sample_rate", default=0,
                  help="Sample rate in Hz of synthesized audio. Set to 0 (default) to use voice's original sample rate.", type=int)
    
    # Parse and validate options
    args = parser.parse_args()

    # Check if service address and port are provided
    if len(args.service) == 0:
        raise RuntimeError("No service address and port provided.")

    # Input text determination
    input_text = ""
    if len(args.inputfile) > 0:
        with codecs.open(args.inputfile, encoding='utf-8', mode="r") as fread:
            input_text = fread.read()
    elif len(args.text) > 0:
        input_text = args.text
    else:
        raise RuntimeError("Empty input string for synthesis.")

    call_synthesize(args.service, input_text, args.out_path, args.sample_rate)


if __name__ == '__main__':
    main()
