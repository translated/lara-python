from lara_sdk import Credentials, Translator
import os

"""
Language detection examples for the Lara Python SDK

This example demonstrates:
- Detecting language of a single string
- Detecting language of multiple strings
- Using hint parameter to improve detection
- Using passlist to restrict detected languages
"""

def main():
    # All examples can use environment variables for credentials:
    # export LARA_ACCESS_KEY_ID="your-access-key-id"
    # export LARA_ACCESS_KEY_SECRET="your-access-key-secret"
    # Falls back to placeholders if not set
    access_key_id = os.getenv("LARA_ACCESS_KEY_ID", "your-access-key-id")
    access_key_secret = os.getenv("LARA_ACCESS_KEY_SECRET", "your-access-key-secret")

    credentials = Credentials(access_key_id, access_key_secret)
    lara = Translator(credentials)
    
    try:
        # Example 1: Detect language of a single string
        print("=== Single String Detection ===")
        result1 = lara.detect("Bonjour, comment allez-vous?")
        print("Text: Bonjour, comment allez-vous?")
        print(f"Detected language: {result1.language}")
        print(f"Content type: {result1.content_type}\n")

        # Example 2: Detect language of multiple strings
        print("=== Multiple Strings Detection ===")
        texts = [
            "Hello, how are you?",
            "Hola, ¿cómo estás?",
            "Ciao, come stai?"
        ]
        result2 = lara.detect(texts)
        print(f"Texts: {texts}")
        print(f"Detected language: {result2.language}")
        print(f"Content type: {result2.content_type}\n")

        # Example 3: Using hint parameter
        print("=== Detection with Hint ===")
        result3 = lara.detect("Hello", hint="en")
        print("Text: Hello")
        print(f"Hint: en")
        print(f"Detected language: {result3.language}")
        print(f"Content type: {result3.content_type}\n")

        # Example 4: Using passlist to restrict detected languages
        print("=== Detection with Passlist ===")
        result4 = lara.detect(
            "Guten Tag",
            passlist=["de-DE", "en-US", "fr-FR"]
        )
        print("Text: Guten Tag")
        print(f"Passlist: ['de-DE', 'en-US', 'fr-FR']")
        print(f"Detected language: {result4.language}")
        print(f"Content type: {result4.content_type}\n")

        # Example 5: Combined hint and passlist
        print("=== Detection with Hint and Passlist ===")
        result5 = lara.detect(
            "Buongiorno",
            hint="it",
            passlist=["it-IT", "es-ES", "pt-PT"]
        )
        print("Text: Buongiorno")
        print(f"Hint: it")
        print(f"Passlist: ['it-IT', 'es-ES', 'pt-PT']")
        print(f"Detected language: {result5.language}")
        print(f"Content type: {result5.content_type}\n")

    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
