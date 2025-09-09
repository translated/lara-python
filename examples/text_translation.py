from lara_sdk import Credentials, Translator, TextBlock
import os

"""
Complete text translation examples for the Lara Python SDK

This example demonstrates:
- Single string translation
- Multiple strings translation
- Translation with instructions
- TextBlocks translation (mixed translatable/non-translatable content)
- Auto-detect source language
- Advanced options
- Get available languages
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
        # Example 1: Basic single string translation
        print("=== Basic Single String Translation ===")
        result1 = lara.translate("Hello, world!", target="fr-FR", source="en-US")
        print("Original: Hello, world!")
        print(f"French: {result1.translation}\n")

        # Example 2: Multiple strings translation
        print("=== Multiple Strings Translation ===")
        texts = ["Hello", "How are you?", "Goodbye"]
        result2 = lara.translate(texts, target="es-ES", source="en-US")
        print(f"Original: {texts}")
        print(f"Spanish: {result2.translation}\n")

        # Example 3: TextBlocks translation (mixed translatable/non-translatable content)
        print("=== TextBlocks Translation ===")
        text_blocks = [
            TextBlock(text="Adventure novels, mysteries, cookbooks—wait, who packed those?", translatable=True),
            TextBlock(text="<br>", translatable=False),  # Non-translatable HTML
            TextBlock(text="Suddenly, it doesn't feel so deserted after all.", translatable=True),
            TextBlock(text='<div class="separator"></div>', translatable=False),  # Non-translatable HTML
            TextBlock(text="Every page you turn is a new journey, and the best part?", translatable=True)
        ]
        
        result3 = lara.translate(text_blocks, target="it-IT", source="en-US")
        print(f"Original TextBlocks: {len(text_blocks)} blocks")
        print(f"Translated blocks: {len(result3.translation)}")
        for i, translation in enumerate(result3.translation):
            print(f"Block {i + 1}: {translation['text']}")
        print()

        # Example 4: Translation with instructions
        print("=== Translation with Instructions ===")
        result4 = lara.translate(
            "Could you send me the report by tomorrow morning?",
            target="de-DE",
            source="en-US",
            instructions=["Be formal", "Use technical terminology"]
        )
        print("Original: Could you send me the report by tomorrow morning?")
        print(f"German (formal): {result4.translation}\n")

        # Example 5: Auto-detecting source language
        print("=== Auto-detect Source Language ===")
        result5 = lara.translate("Bonjour le monde!", target="en-US")
        print("Original: Bonjour le monde!")
        print(f"Detected source: {result5.source_language}")
        print(f"English: {result5.translation}\n")

        # Example 6: Advanced options with comprehensive settings
        print("=== Translation with Advanced Options ===")

        result6 = lara.translate(
            "This is a comprehensive translation example",
            target="it-IT",
            source="en-US",
            adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl", "mem_2XyZ9AbC8dEf7GhI6jKlMn"], # Replace with actual memory IDs
            glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl", "gls_2XyZ9AbC8dEf7GhI6jKlMn"], # Replace with actual glossary IDs
            instructions=["Be professional"],
            style="fluid",
            content_type="text/plain",
            timeout_ms=10000,
        )
        print("Original: This is a comprehensive translation example")
        print(f"Italian (with all options): {result6.translation}\n")

        # Example 7: Get available languages
        print("=== Available Languages ===")
        languages = lara.languages()
        print(f"Supported languages: {languages}")

    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main() 