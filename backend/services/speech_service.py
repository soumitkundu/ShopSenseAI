import os
import tempfile
import azure.cognitiveservices.speech as speechsdk
from config import Config


def speech_to_text_from_file(audio_bytes: bytes) -> str:
    # ... (keep everything the same until the finally block)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    try:
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()

        audio_config = speechsdk.audio.AudioConfig(filename=tmp.name)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )
        result = recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return "Sorry, I could not understand the audio. Please try again."
        else:
            return f"Speech recognition failed: {result.reason}"

    finally:
        # Release SDK objects before file deletion (Windows file lock fix)
        del recognizer
        del audio_config
        del result
        if os.path.exists(tmp.name):
            os.remove(tmp.name)

def text_to_speech_bytes(text: str) -> bytes:
    """
    Convert a text string to audio using Azure Neural TTS.
    Returns raw audio bytes (PCM WAV) for streaming to the client.
    """
    speech_config = speechsdk.SpeechConfig(
        subscription=Config.AZURE_SPEECH_KEY,
        region=Config.AZURE_SPEECH_REGION,
    )
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
    )

    # Synthesise to in-memory stream
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=None,  # no speaker output — capture bytes directly
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return result.audio_data
    else:
        raise RuntimeError(f"TTS failed: {result.reason}")