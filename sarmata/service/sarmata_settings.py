import os
import io


class SarmataSettings:
    """Default settings for Techmo Sarmata ASR (timeouts and thresholds)"""

    def __init__(self):
        self.max_alternatives = 3           # Maximum number of recognition hypotheses to be returned
        self.no_match_threshold = 0.2       # Confidence threshold for recognition / no-match
        self.speech_complete_timeout = 500  # ms - MRCP speech complete timeout
        self.speech_incomplete_timeout = 3000# ms - MRCP speech incomplete timeout
        self.no_input_timeout = 5000        # ms - MRCP no input timeout
        self.recognition_timeout = 10000    # ms - MRCP no recognition timeout
        self.session_id = ''
        self.grammar_name = ''
        self.grammar = ''
        self.service_settings = ''

    def process_args(self, args):
        self.max_alternatives = args.max_alternatives
        self.no_match_threshold = args.no_match_threshold
        self.speech_complete_timeout = args.speech_complete_timeout
        self.speech_incomplete_timeout = args.speech_incomplete_timeout
        self.no_input_timeout = args.no_input_timeout
        self.recognition_timeout = args.recognition_timeout
        self.grammar_name = args.grammar_name
        self.service_settings = args.service_settings

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

