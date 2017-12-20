from pydub import AudioSegment


def get_audio(audio_path, start_time_ms=0, final_time_ms=-1):
    """
    Load audio from path
    :param audio_path: path to wave file
    :param start_time_ms: start sample (in miliseconds) of audio segment extracted from wave.
    :param final_time_ms: end sample (in miliseconds) of audio segment. -1 means all samples to the end
    :return: pydub.AudioSegment object cropped to given range (start_time_ms, final_time_ms)
    """
    audio = AudioSegment.from_file(audio_path)
    if start_time_ms < 0.0 or start_time_ms >= len(audio):
        raise ValueError("Incorrect start time for audio: {} ({} ms) ".format(audio_path, start_time_ms))

    if final_time_ms > len(audio):
        raise ValueError("Incorrect final time for audio: {} ({} ms) ".format(audio_path, final_time_ms))

    start = start_time_ms
    end = final_time_ms if final_time_ms > 0.0 else len(audio)

    audio_content = audio[start:end].raw_data

    sound = AudioSegment(
        # raw audio data (bytes)
        data=audio_content,
        # 2 byte (16 bit) samples
        sample_width=audio.sample_width,
        # frame rate
        frame_rate=audio.frame_rate,
        # should be mono
        channels=audio.channels
    )

    return sound
