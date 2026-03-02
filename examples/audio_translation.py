from lara_sdk import AccessKey, Translator, AudioStatus
import os
import time

"""
Complete audio translation examples for the Lara Python SDK

Supported audio formats: .wav, .mp3, .opus, .ogg, .webm

This example demonstrates:
- Basic audio translation
- Advanced options with memories and glossaries
- Step-by-step audio translation with status monitoring
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

    try:
        # Example 1: Basic audio translation
        print("=== Basic Audio Translation ===")
        source_lang = "en-US"
        target_lang = "de-DE"

        print(f"Translating audio: {os.path.basename(sample_audio_file)} from {source_lang} to {target_lang}")

        translated_audio = lara.audio.translate(
            file_path=sample_audio_file,
            filename=os.path.basename(sample_audio_file),
            source=source_lang,
            target=target_lang
        )

        output_path = "sample_audio_translated.mp3"
        with open(output_path, 'wb') as f:
            f.write(translated_audio)

        print("✅ Audio translation completed")
        print(f"📄 Translated file saved to: {output_path}\n")

    except Exception as error:
        print(f"Error translating audio: {error}\n")
        return

    # Example 2: Audio translation with advanced options
    print("=== Audio Translation with Advanced Options ===")
    try:
        translated_audio2 = lara.audio.translate(
            file_path=sample_audio_file,
            filename=os.path.basename(sample_audio_file),
            source=source_lang,
            target=target_lang,
            adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
            glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"]  # Replace with actual glossary IDs
        )

        output_path2 = "advanced_audio_translated.mp3"
        with open(output_path2, 'wb') as f:
            f.write(translated_audio2)

        print("✅ Advanced Audio translation completed")
        print(f"📄 Translated file saved to: {output_path2}\n")

    except Exception as error:
        print(f"Error in advanced translation: {error}")

    print()

    # Example 3: Step-by-step audio translation
    print("=== Step-by-Step Audio Translation ===")

    try:
        # Upload audio
        print("Step 1: Uploading audio...")
        audio = lara.audio.upload(
            file_path=sample_audio_file,
            filename=os.path.basename(sample_audio_file),
            source=source_lang,
            target=target_lang,
            adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
            glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"]  # Replace with actual glossary IDs
        )
        print(f"Audio uploaded with ID: {audio.id}")
        print(f"Initial status: {audio.status.value}")

        # Check status
        print("\nStep 2: Checking status...")
        updated_audio = lara.audio.status(audio.id)
        print(f"Current status: {updated_audio.status.value}")

        # Download translated audio
        print("\nStep 3: Downloading would happen after translation completes...")
        translated_audio3 = lara.audio.download(audio.id)

        output_path3 = "step_audio_translated.mp3"
        with open(output_path3, 'wb') as f:
            f.write(translated_audio3)

        print("✅ Step-by-step translation completed")

    except Exception as error:
        print(f"Error in step-by-step process: {error}")

if __name__ == "__main__":
    main()
