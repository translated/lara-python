from lara_sdk import AccessKey, Translator, AudioStatus
import os
import time

"""
Complete audio transcript translation examples for the Lara Python SDK

Supported audio formats: .wav, .mp3, .opus, .ogg, .webm

This example demonstrates the async Audio2Text flow, which returns only the
translated transcript (JSON) instead of a dubbed audio file:
- Basic transcript translation
- Advanced options with memories and glossaries
- Step-by-step transcript translation with status monitoring
"""

def main():
    # All examples use environment variables for credentials, so set them first:
    # export LARA_ACCESS_KEY_ID="your-access-key-id"
    # export LARA_ACCESS_KEY_SECRET="your-access-key-secret"

    # Set your credentials here
    access_key_id = os.getenv("LARA_ACCESS_KEY_ID", "your-access-key-id")
    access_key_secret = os.getenv("LARA_ACCESS_KEY_SECRET", "your-access-key-secret")

    credentials = AccessKey(access_key_id, access_key_secret)
    lara = Translator(credentials)

    # Replace with your actual audio file path
    sample_audio_file = "sample_audio.mp3"  # Supported: .wav, .mp3, .opus, .ogg, .webm

    if not os.path.exists(sample_audio_file):
        print(f"Please create a sample audio file at: {sample_audio_file}")
        return

    source_lang = "en-US"
    target_lang = "de-DE"

    try:
        # Example 1: Basic transcript translation
        print("=== Basic Transcript Translation ===")
        print(f"Transcribing audio: {os.path.basename(sample_audio_file)} from {source_lang} to {target_lang}")

        result = lara.audio.translate_transcript(
            file_path=sample_audio_file,
            filename=os.path.basename(sample_audio_file),
            source=source_lang,
            target=target_lang
        )

        print("✅ Transcript translation completed")
        print(f"📝 Translation: {result.translation}")
        print(f"🔎 Segments: {len(result.segments)}\n")

    except Exception as error:
        print(f"Error translating transcript: {error}\n")
        return

    # Example 2: Transcript translation with advanced options
    print("=== Transcript Translation with Advanced Options ===")
    try:
        result2 = lara.audio.translate_transcript(
            file_path=sample_audio_file,
            filename=os.path.basename(sample_audio_file),
            source=source_lang,
            target=target_lang,
            adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
            glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"]  # Replace with actual glossary IDs
        )

        print("✅ Advanced transcript translation completed")
        print(f"📝 Translation: {result2.translation}\n")

    except Exception as error:
        print(f"Error in advanced translation: {error}")

    print()

    # Example 3: Step-by-step transcript translation
    print("=== Step-by-Step Transcript Translation ===")

    try:
        # Upload audio
        print("Step 1: Uploading audio...")
        audio = lara.audio.upload_for_transcription(
            file_path=sample_audio_file,
            filename=os.path.basename(sample_audio_file),
            source=source_lang,
            target=target_lang,
            adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
            glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"]  # Replace with actual glossary IDs
        )
        print(f"Audio uploaded with ID: {audio.id}")
        print(f"Initial status: {audio.status.value}")

        # Poll status
        print("\nStep 2: Waiting for the transcript to be translated...")
        max_wait_time = 60 * 15  # 15 minutes
        start = time.time()
        while audio.status not in (AudioStatus.TRANSLATED, AudioStatus.ERROR):
            if time.time() - start >= max_wait_time:
                print("Timed out waiting for the transcript translation")
                return

            time.sleep(2)

            audio = lara.audio.status(audio.id)
            print(f"Current status: {audio.status.value}")

        if audio.status == AudioStatus.ERROR:
            print(f"Transcript translation failed: {audio.error_reason}")
            return

        # Retrieve the translated transcript
        print("\nStep 3: Retrieving the translated transcript...")
        result3 = lara.audio.get_translated_transcript(audio.id)

        print(f"Text: {result3.text}")
        print(f"Translation: {result3.translation}")
        for segment in result3.segments:
            print(f"[{segment.start} - {segment.end}] {segment.translation}")

        print("✅ Step-by-step transcript translation completed")

    except Exception as error:
        print(f"Error in step-by-step process: {error}")

if __name__ == "__main__":
    main()
