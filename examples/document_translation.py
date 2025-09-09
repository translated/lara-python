from lara_sdk import Credentials, Translator
import os

"""
Complete document translation examples for the Lara Python SDK

This example demonstrates:
- Basic document translation
- Advanced options with memories and glossaries
- Step-by-step document translation with status monitoring
"""

def main():
    # All examples can use environment variables for credentials:
    # export LARA_ACCESS_KEY_ID="your-access-key-id"
    # export LARA_ACCESS_KEY_SECRET="your-access-key-secret"

    # Set your credentials here
    access_key_id = os.getenv("LARA_ACCESS_KEY_ID", "your-access-key-id")
    access_key_secret = os.getenv("LARA_ACCESS_KEY_SECRET", "your-access-key-secret")

    credentials = Credentials(access_key_id, access_key_secret)
    lara = Translator(credentials)

    # Replace with your actual document file path
    sample_file_path = "sample_document.docx"  # Create this file with your content
    
    if not os.path.exists(sample_file_path):
        print(f"Please create a sample document file at: {sample_file_path}")
        print("Add some sample text content to translate.\n")
        return

    # Example 1: Basic document translation
    print("=== Basic Document Translation ===")
    source_lang = "en-US"
    target_lang = "de-DE"
    
    print(f"Translating document: {os.path.basename(sample_file_path)} from {source_lang} to {target_lang}")
    
    try:
        translated_content = lara.documents.translate(
            file_path=sample_file_path,
            filename=os.path.basename(sample_file_path),
            source=source_lang,
            target=target_lang
        )
        
        # Save translated document - replace with your desired output path
        output_path = "sample_document_translated.docx"
        with open(output_path, 'wb') as f:
            f.write(translated_content)
        
        print("✅ Document translation completed")
        print(f"📄 Translated file saved to: {os.path.basename(output_path)}\n")
    except Exception as e:
        print(f"Error translating document: {e}\n")
        return

    # Example 2: Document translation with advanced options
    print("=== Document Translation with Advanced Options ===")
    try:
        translated_content2 = lara.documents.translate(
            file_path=sample_file_path,
            filename=os.path.basename(sample_file_path),
            source=source_lang,
            target=target_lang,
            adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
            glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"]  # Replace with actual glossary IDs
        )
        
        # Save translated document - replace with your desired output path
        output_path2 = "advanced_document_translated.docx"
        with open(output_path2, 'wb') as f:
            f.write(translated_content2)
        
        print("✅ Advanced document translation completed")
        print(f"📄 Translated file saved to: {os.path.basename(output_path2)}")
    except Exception as e:
        print(f"Error in advanced translation: {e}")
    print()

    # Example 3: Step-by-step document translation
    print("=== Step-by-Step Document Translation ===")
    
    try:
        # Upload document
        print("Step 1: Uploading document...")
        document = lara.documents.upload(
            file_path=sample_file_path,
            filename=os.path.basename(sample_file_path),
            source=source_lang,
            target=target_lang,
            adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
            glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"]  # Replace with actual glossary IDs
        )
        print(f"Document uploaded with ID: {document.id}")
        print(f"Initial status: {document.status.value}")
        
        # Check status
        print("\nStep 2: Checking status...")
        updated_document = lara.documents.status(document.id)
        print(f"Current status: {updated_document.status.value}")

        # Download translated document
        print("\nStep 3: Downloading would happen after translation completes...")

        try:
            downloaded_content = lara.documents.download(document.id)
        except Exception as download_error:
            print(f"Download demonstration: {download_error}")
        
        print("✅ Step-by-step translation completed")
    except Exception as e:
        print(f"Error in step-by-step process: {e}")

if __name__ == "__main__":
    main() 