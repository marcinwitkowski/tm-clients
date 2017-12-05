import clients_engines.cloud_speech_extended_pb2 as cloud_speech_extended_pb2
from argparse import ArgumentParser


class SyncRecognizer:

    def __init__(self, service, settings_args=None):
        self.parser = ArgumentParser(description="""Main script for running tests environment for ASR Dictation systems""")
        self.parser.add_argument("--deadline", help="Communication timeout (seconds)", default=60, type=int)
        self.parser.add_argument("--language", help="Language", default='pl-PL')
        self.parser.add_argument("--time_offsets", help="If set - the recognizer will return also word time offsets",
                                 action="store_true", default=False)
        self.parser.add_argument("--max_alternatives", help="Maximum number of returned hypotheses", default=1, type=int)

        self.service = service
        self.settings = self.parser.parse_args(args=settings_args)

    def recognize(self, audio):
        """
        Synchronous method to call GoogleSpeechApi
        :param audio: WAVE (pydub::AudioSegment object), with sampling rate
        :param sampling_rate: WAVE sampling rate
        :return: list of dict {transcript: =>, confidence: => }
        """
        response = self.service.Recognize(cloud_speech_extended_pb2.RecognizeRequest(
            config=cloud_speech_extended_pb2.RecognitionConfig(
                # There are a bunch of config options you can specify. See https://goo.gl/KPZn97 for the full list.
                encoding='LINEAR16',  # one of LINEAR16, FLAC, MULAW, AMR, AMR_WB
                sample_rate_hertz=audio.frame_rate,  # the rate in hertz
                # See https://g.co/cloud/speech/docs/languages for a list of supported languages.
                language_code=self.settings.language,  # a BCP-47 language tag
                enable_word_time_offsets=self.settings.time_offsets,  # if true, return recognized word time offsets
                max_alternatives=self.settings.max_alternatives,  # maximum number of returned hypotheses
            ),
            audio=cloud_speech_extended_pb2.RecognitionAudio(
                uri=None,
                content=audio.raw_data
            )
        ), self.settings.deadline)

        # Print the recognition result alternatives and confidence scores.
        results = []

        # for result in response.results:
        if len(response.results) > 0:
            result = response.results[0]  # TODO: check why here we have list of results ?, when it is possible ?

            alternative = result.alternatives[0]
            alignment = []  #
            confirmed_results = []
            if self.settings.time_offsets:
                word_indices = [j for j in range(len(alternative.words)) if
                                alternative.words[j].word != '<eps>']

                if len(word_indices) > 0:
                    confirmed_results.append([alternative.words[i].word for i in word_indices])
                else:  # alignment was not returned
                    confirmed_results.append(alternative.transcript)

                alignment.append(
                    [[alternative.words[i].start_time, alternative.words[i].end_time] for i in
                     word_indices])
                results.append({
                    'transcript': ' '.join(confirmed_results),
                    'confidence': alternative.confidence,
                    'alignment': alignment,
                })
            else:
                results.append({
                    'transcript': alternative.transcript,
                    'confidence': alternative.confidence
                })

        return results
