import os
import tempfile
import azure.cognitiveservices.speech as speechsdk
from config import Config


def speech_to_text_from_file(audio_bytes: bytes) -> str:
    """
    Convert audio bytes (uploaded WAV file) to text using Azure Speech SDK.
    Writes to a temp file on Windows, recognises once, then cleans up safely.
    """
    # Build speech config BEFORE the try block so it is always defined
    speech_config = speechsdk.SpeechConfig(
        subscription=Config.AZURE_SPEECH_KEY,
        region=Config.AZURE_SPEECH_REGION,
    )
    speech_config.speech_recognition_language = "en-US"

    tmp_path = None
    recognizer = None
    audio_config = None
    result = None

    try:
        # Write bytes to a named temp file (Windows requires delete=False)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()

        audio_config = speechsdk.audio.AudioConfig(filename=tmp_path)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )
        result = recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return "Sorry, I could not understand the audio. Please try again."
        else:
            cancellation = result.cancellation_details
            return f"Speech recognition failed: {cancellation.reason} — {cancellation.error_details}"

    except Exception as e:
        return f"Speech service error: {str(e)}"

    finally:
        # Release SDK objects first — Windows holds file handles until these are freed
        if result is not None:
            del result
        if recognizer is not None:
            del recognizer
        if audio_config is not None:
            del audio_config
        # Now safe to delete the temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except PermissionError:
                pass  # SDK may still briefly hold the handle; file will be cleaned by OS


def text_to_speech_bytes(text: str) -> bytes:
    """
    Convert a text string to audio using Azure Neural TTS.
    Returns raw WAV bytes for streaming to the client.
    """
    speech_config = speechsdk.SpeechConfig(
        subscription=Config.AZURE_SPEECH_KEY,
        region=Config.AZURE_SPEECH_REGION,
    )
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
    )

    synthesizer = None
    result = None

    try:
        # audio_config=None captures bytes directly without writing to speaker/file
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None,
        )
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        else:
            cancellation = result.cancellation_details
            raise RuntimeError(
                f"TTS failed: {cancellation.reason} — {cancellation.error_details}"
            )

    finally:
        # Release in reverse order of creation
        if result is not None:
            del result
        if synthesizer is not None:
            del synthesizer