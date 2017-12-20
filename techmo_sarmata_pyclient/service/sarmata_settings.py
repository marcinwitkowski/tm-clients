import os
import io


class SarmataSettings:
    """Default settings for Techmo Sarmata ASR (timeouts and thresholds)"""

    def __init__(self):
        self.nbest = 3                      # Max number of hypotheses
        self.no_match = 0.2                 # Confidence threshold for recognition / no-match
        self.speech_complete = 500          # ms - MRCP speech complete timeout
        self.speech_incomplete = 3000       # ms - MRCP speech incomplete timeout
        self.no_input_timeout = 5000        # ms - MRCP no input timeout
        self.no_recognition_timeout = 10000   # ms - MRCP no recognition
        self.session_id = ''
        self.grammar = ''

    def process_args(self, args):
        self.nbest = args.nbest
        self.no_match = args.nomatch
        self.speech_complete = args.speech_complete
        self.speech_incomplete = args.speech_incomplete
        self.no_input_timeout = args.no_input
        self.no_recognition_timeout = args.recognition_timeout

    def set_session_id(self, session_id):
        """
        Session ID is used for better log processing
        :param session_id: string identifier
        :return:
        """
        self.session_id = session_id

    def load_grammar(self, grammar_path):
        """
        Load grammar from XML or ABNF file (UTF-8 encoding)
        :param grammar_path: path to existing txt file
        :return:
        """
        if not os.path.exists(grammar_path):
            raise ValueError("Grammar file does not exist at: {}".format(grammar_path))

        with io.open(grammar_path, 'r', encoding='utf-8') as f:
            self.grammar = f.read()

    def to_map(self):
        """
        Convert settings to dictionary, used in grpc request generator
        :return:
        """

        # validate if grammar has been already loaded

        if not self.grammar:
            raise ValueError("Grammar must be load first")

        settings_map = {
            "nbest": str(self.nbest),
            "no-match-th": str(self.no_match),
            "no-input-timeout": str(self.no_input_timeout),
            "no-rec-timeout": str(self.no_recognition_timeout),
            "complete-timeout": str(self.speech_complete),
            "incomplete-timeout": str(self.speech_incomplete),
            "session_id": self.session_id,
            "grammar_data": self.grammar
        }

        return settings_map

