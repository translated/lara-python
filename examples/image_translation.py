from lara_sdk import AccessKey, Translator
import os

"""
Complete image translation examples for the Lara Python SDK

This example demonstrates:
- Basic image translation (full image with text overlay/inpainting)
- Image text-only translation (extract and translate text without rendering)
- Translation with different styles
- Advanced options with memories and glossaries
"""

def main():
    # All examples can use environment variables for credentials:
    # export LARA_ACCESS_KEY_ID="your-access-key-id"
    # export LARA_ACCESS_KEY_SECRET="your-access-key-secret"
    # Falls back to placeholders if not set
    access_key_id = os.getenv("LARA_ACCESS_KEY_ID", "your-access-key-id")
    access_key_secret = os.getenv("LARA_ACCESS_KEY_SECRET", "your-access-key-secret")

    credentials = AccessKey(access_key_id, access_key_secret)
    lara = Translator(credentials)

    # Replace with your actual image file path
    sample_image_path = "sample_image.png"  # Create this file with text content

    if not os.path.exists(sample_image_path):
        print(f"Please create a sample image file at: {sample_image_path}")
        return

    try:
        # Example 1: Basic image translation with overlay text removal
        print("=== Basic Image Translation (Overlay) ===")
        translated_image = lara.images.translate(
            source="en-US",
            target="fr-FR",
            image_path=sample_image_path,
            text_removal="overlay"
        )

        # Save translated image
        output_path = "sample_image_translated_overlay_fr.png"
        with open(output_path, 'wb') as f:
            f.write(translated_image)

        print(f"Original image: {os.path.basename(sample_image_path)}")
        print(f"Translated image saved to: {output_path}")
        print("Translation: en-US -> fr-FR (overlay mode)\n")

        # Example 2: Image translation with inpainting text removal
        print("=== Image Translation (Inpainting) ===")
        translated_image2 = lara.images.translate(
            source="en-US",
            target="de-DE",
            image_path=sample_image_path,
            text_removal="inpainting"
        )

        output_path2 = "sample_image_translated_inpaint_de.png"
        with open(output_path2, 'wb') as f:
            f.write(translated_image2)

        print(f"Translated image saved to: {output_path2}")
        print("Translation: en-US -> de-DE (inpainting mode)\n")

        # Example 3: Image text-only translation (no image rendering)
        print("=== Image Text-Only Translation ===")
        text_results = lara.images.translate_text(
            source="en-US",
            target="es-ES",
            image_path=sample_image_path
        )

        print(f"Original image: {os.path.basename(sample_image_path)}")
        print(f"Found {len(text_results.paragraphs)} text segments:")
        for i, result in enumerate(text_results.paragraphs, 1):
            print(f"  Segment {i}:")
            print(f"    Original: {result.text}")
            print(f"    Translated: {result.translation}")
        print()

        # Example 4: Image translation with style parameter
        print("=== Image Translation with Style ===")
        translated_image3 = lara.images.translate(
            source="en-US",
            target="it-IT",
            image_path=sample_image_path,
            text_removal="overlay",
            style="fluid"
        )

        output_path3 = "sample_image_translated_fluid_it.png"
        with open(output_path3, 'wb') as f:
            f.write(translated_image3)

        print(f"Translated image saved to: {output_path3}")
        print("Translation: en-US -> it-IT (fluid style)\n")

        # Example 5: Image translation with advanced options
        print("=== Image Translation with Advanced Options ===")
        translated_image4 = lara.images.translate(
            source="en-US",
            target="ja-JP",
            image_path=sample_image_path,
            text_removal="inpainting",
            adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
            glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual glossary IDs
            style="faithful"
        )

        output_path4 = "sample_image_translated_advanced_ja.png"
        with open(output_path4, 'wb') as f:
            f.write(translated_image4)

        print(f"Translated image saved to: {output_path4}")
        print("Translation: en-US -> ja-JP (with memories and glossaries)\n")

        # Example 6: Text-only translation with advanced options
        print("=== Text-Only Translation with Advanced Options ===")
        text_results2 = lara.images.translate_text(
            source="en-US",
            target="zh-CN",
            image_path=sample_image_path,
            adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
            glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual glossary IDs
            style="creative"
        )

        print(f"Found {len(text_results2.paragraphs)} text segments with advanced options:")
        for i, result in enumerate(text_results2.paragraphs, 1):
            print(f"  Segment {i}:")
            print(f"    Original: {result.text}")
            print(f"    Translated: {result.translation}")
        print()

        # Example 7: Translation with no_trace option
        print("=== Image Translation with no_trace (Privacy Mode) ===")
        translated_image5 = lara.images.translate(
            source="en-US",
            target="ko-KR",
            image_path=sample_image_path,
            text_removal="overlay",
            no_trace=True
        )

        output_path5 = "sample_image_translated_notrace_ko.png"
        with open(output_path5, 'wb') as f:
            f.write(translated_image5)

        print(f"Translated image saved to: {output_path5}")
        print("Translation: en-US -> ko-KR (no_trace enabled for privacy)\n")

        # Example 8: Auto-detect source language
        print("=== Auto-detect Source Language ===")
        translated_image6 = lara.images.translate(
            source=None,  # Auto-detect
            target="en-US",
            image_path=sample_image_path,
            text_removal="overlay"
        )

        output_path6 = "sample_image_translated_autodetect_en.png"
        with open(output_path6, 'wb') as f:
            f.write(translated_image6)

        print(f"Translated image saved to: {output_path6}")
        print("Translation: auto-detected -> en-US\n")

    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
