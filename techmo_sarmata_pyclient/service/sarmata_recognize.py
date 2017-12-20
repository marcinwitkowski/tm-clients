from . import asr_service_pb2
import grpc
import threading

class RequestIterator:
    """Thread-safe request iterator for streaming recognizer."""

    def __init__(self, audio, settings):
        # Iterator data
        self.audio = audio["samples"]
        self.audio_frame_rate = audio["frame_rate"]
        self.settings = settings

        frame_len = 200   # ms
        sample_width = 2  # 16bit
        self.frame_samples_size = (self.audio_frame_rate // 1000) * frame_len * sample_width
        self.request_builder = {
            True: self._initial_request,
            False: self._normal_request
        }
        # Iterator state
        self.lock = threading.Lock()
        self.is_initial_request = True
        self.eos = False  # indicates whether end of stream message was send (request to stop iterator)
        self.data_index = 0

    def _initial_request(self):
        request = asr_service_pb2.RecognizeRequest(
            initial_request=asr_service_pb2.InitialRecognizeRequest(
            )
        )

        settings_map = self.settings.to_map()
        for key in settings_map:
            cf = request.initial_request.config.add()
            cf.key = key
            cf.value = str(settings_map[key])

        # add sampling rate
        cf = request.initial_request.config.add()
        cf.key = "sampling-rate"
        cf.value = str(self.audio_frame_rate)

        self.is_initial_request = False
        return request

    def _normal_request(self):
        # stop iteration
        if self.eos:
            raise StopIteration()

        # send only EndOfStream indicator
        if self.data_index >= len(self.audio):
            self.eos = True
            return asr_service_pb2.RecognizeRequest(audio_request=asr_service_pb2.AudioRequest(
                end_of_stream=True
            )
            )

        end_sample = self.data_index + self.frame_samples_size
        if end_sample >= len(self.audio):
            end_sample = len(self.audio)

        data = self.audio[self.data_index: end_sample]

        import struct
        count = int(len(data) / 2)
        shorts = struct.unpack('h' * count, data)
        shorts_len = len(shorts)

        self.data_index = end_sample

        # send only audio - EndOfStream will be sent in separate message
        return asr_service_pb2.RecognizeRequest(audio_request=asr_service_pb2.AudioRequest(
            content=data,
            end_of_stream=False
            )
        )

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return self.request_builder[self.is_initial_request]()


class SarmataRecognizer:

    def __init__(self, address):
        self.service = SarmataRecognizer.connect(address)

    def recognize(self, audio, settings):
        requests_iterator = RequestIterator(audio, settings)
        recognitions = self.service.Recognize(requests_iterator)

        responses = []
        for recognition in recognitions:
            responses.append(recognition)

        return responses

    @staticmethod
    def connect(endpoint):
        service = asr_service_pb2.ASRStub(
            grpc.insecure_channel(endpoint))
        return service
