import time
import threading
from argparse import ArgumentParser
import clients_engines.cloud_speech_extended_pb2 as cloud_speech_extended_pb2


class RequestIterator:
    """Thread-safe request iterator for streaming recognizer."""

    def __init__(self, audio, settings):
        # Iterator data
        self.audio_content = audio.raw_data
        self.settings = settings
        self.audio_frame_rate = audio.frame_rate
        self.frame_samples_size = (audio.frame_rate // 1000) * self.settings.frame_len * audio.sample_width
        self.request_builder = {
            True: self._initial_request,
            False: self._normal_request
        }
        # Iterator state
        self.lock = threading.Lock()
        self.is_initial_request = True
        self.data_index = 0

    def _initial_request(self):
        req = StreamingRecognizer.build_configuration_request(self.audio_frame_rate, self.settings)
        self.is_initial_request = False
        return req

    def _normal_request(self):
        data = self.audio_content[self.data_index: (self.data_index + self.frame_samples_size)]
        self.data_index += self.frame_samples_size
        if self.data_index >= len(self.audio_content):
            raise StopIteration()
        return cloud_speech_extended_pb2.StreamingRecognizeRequest(audio_content=data)

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            time.sleep(float(self.settings.delay / 1000))
            return self.request_builder[self.is_initial_request]()


class StreamingRecognizer:

    def __init__(self, service, settings_args=None):
        # Use ArgumentParser to parse settings
        self.parser = ArgumentParser(description="""Main script for running tests environment for ASR Dictation systems""")
        self.parser.add_argument("--frame_len", help="Frame size (milliseconds)", default=20, type=int)
        self.parser.add_argument("--delay", help="Simulation delay between sending next frame", default=20, type=int)
        self.parser.add_argument("--time_offsets", help="If set - the recognizer will return also word time offsets",
                            action="store_true", default=False)
        self.parser.add_argument("--single_utterance", help="If set - the recognizer will detect a single spoken utterance",
                            action="store_true", default=False)
        self.parser.add_argument("--no_interim_results", help="If set - hide stats (WER, LER)",
                            action="store_false", dest="interim_results", default=True)
        self.parser.add_argument("--language", help="Language", default='pl-PL')
        self.parser.add_argument("--max_alternatives", help="Maximum number of returned hypotheses", default=1, type=int)

        self.service = service
        self.settings = self.parser.parse_args(args=settings_args)

    def recognize(self, audio):

        requests_iterator = RequestIterator(audio, self.settings)
        return self.recognize_audio_content(requests_iterator)

    def recognize_audio_content(self, requests_iterator):
        time_offsets = self.settings.time_offsets
        recognitions = self.service.StreamingRecognize(requests_iterator)
        
        confirmed_results = []
        alignment = []
        confidence = 1.0

        for recognition in recognitions:
            # process response type
            # TODO: handle error: if recognition.has_status:
            if recognition.results is not None and len(recognition.results) > 0:
                first = recognition.results[0]
                #if first.is_final:
                if time_offsets:
                    word_indices = [j for j in range(len(first.alternatives[0].words)) if first.alternatives[0].words[j].word != '<eps>']
                    confirmed_results.append([first.alternatives[0].words[i].word for i in word_indices])
                    alignment.append([[first.alternatives[0].words[i].start_time, first.alternatives[0].words[i].end_time]  for i in word_indices])
                else:
                    confirmed_results.append(first.alternatives[0].transcript)
                confidence = min(confidence, first.alternatives[0].confidence)
                #print(u"Results - {} ({}) !confirmed!".format(first.alternatives[0].transcript,
                #                                                           first.alternatives[0].confidence))
                #else:
                    #print(u"Temporal results - {}".format(first))
            # handle end of audio / utterance

        # build final results
        final_alignment = [[]]
        if time_offsets:
            final_transc = ' '.join(confirmed_results[0])
            if alignment:
                final_alignment = alignment[0]
        else:
            final_transc = ' '.join(confirmed_results)

        return [{
            'transcript': final_transc,
            'alignment': final_alignment,
            'confidence': confidence
        }]  # array with one element

    @staticmethod
    def build_configuration_request(sampling_rate, settings):
        config_req = cloud_speech_extended_pb2.StreamingRecognizeRequest(
            streaming_config=cloud_speech_extended_pb2.StreamingRecognitionConfig(
                config=cloud_speech_extended_pb2.RecognitionConfig(
                    encoding='LINEAR16',  # one of LINEAR16, FLAC, MULAW, AMR, AMR_WB
                    sample_rate_hertz=sampling_rate,  # the rate in hertz
                    # See https://g.co/cloud/speech/docs/languages for a list of supported languages.
                    language_code=settings.language,  # a BCP-47 language tag
                    enable_word_time_offsets=settings.time_offsets,  # if true, return recognized word time offsets
                    max_alternatives=settings.max_alternatives,  # maximum number of returned hypotheses
                ),
                single_utterance=settings.single_utterance,
                interim_results=settings.interim_results
            )
            # no audio data in first request (config only)
        )

        return config_req
