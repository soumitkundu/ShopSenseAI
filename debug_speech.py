# File: backend/debug_speech.py
# Run: py debug_speech.py

import os
import tempfile
from dotenv import load_dotenv
load_dotenv()

import azure.cognitiveservices.speech as speechsdk

SPEECH_KEY    = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

print("Region:", SPEECH_REGION)
print()

# ── Test 1: Text-to-Speech ──────────────────────────────────────────
print("── Text-to-Speech (TTS) ───────────────────────")
tts_output = "debug_tts_output.wav"

speech_config = speechsdk.SpeechConfig(
    subscription=SPEECH_KEY, region=SPEECH_REGION
)
speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
speech_config.set_speech_synthesis_output_format(
    speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
)

audio_config = speechsdk.audio.AudioOutputConfig(filename=tts_output)
synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config, audio_config=audio_config
)

test_text = "Hello, I am ShopSense AI. I can help you find the best products."
result = synthesizer.speak_text_async(test_text).get()

if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    size_kb = os.path.getsize(tts_output) / 1024
    print(f"✅ TTS success — saved to '{tts_output}' ({size_kb:.1f} KB)")
else:
    print(f"❌ TTS failed: {result.reason}")
    if result.cancellation_details:
        print(f"   Detail: {result.cancellation_details.error_details}")

# FIX 1: Explicitly release the synthesizer so Windows frees the file handle
del synthesizer
del audio_config
del result

print()

# ── Test 2: Speech-to-Text on the WAV we just generated ────────────
print("── Speech-to-Text (STT) on generated WAV ──────")

speech_config2 = speechsdk.SpeechConfig(
    subscription=SPEECH_KEY, region=SPEECH_REGION
)
speech_config2.speech_recognition_language = "en-US"
audio_config2 = speechsdk.audio.AudioConfig(filename=tts_output)

recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config2, audio_config=audio_config2
)

stt_result = recognizer.recognize_once_async().get()

if stt_result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print(f"✅ STT success")
    print(f"   Original  : {test_text}")
    print(f"   Recognised: {stt_result.text}")
elif stt_result.reason == speechsdk.ResultReason.NoMatch:
    print(f"❌ STT no match: {stt_result.no_match_details}")
else:
    print(f"❌ STT failed: {stt_result.reason}")
    if stt_result.cancellation_details:
        print(f"   Detail: {stt_result.cancellation_details.error_details}")

# FIX 2: Release the recognizer before file cleanup too
del recognizer
del audio_config2
del stt_result

# Now safe to delete on Windows
if os.path.exists(tts_output):
    os.remove(tts_output)
    print(f"   (temp file cleaned up)")