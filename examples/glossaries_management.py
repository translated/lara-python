from lara_sdk import AccessKey, Translator, GlossaryTerm
import os

"""
Complete glossary management examples for the Lara Python SDK

This example demonstrates:
- Create, list, update, delete glossaries
- CSV import with status monitoring
- Glossary export
- Glossary terms count
- Import status checking
- Add/replace and delete glossary term entries
"""

def main():
    # All examples can use environment variables for credentials:
    # export LARA_ACCESS_KEY_ID="your-access-key-id"
    # export LARA_ACCESS_KEY_SECRET="your-access-key-secret"

    # Set your credentials here
    access_key_id = os.getenv("LARA_ACCESS_KEY_ID", "your-access-key-id")
    access_key_secret = os.getenv("LARA_ACCESS_KEY_SECRET", "your-access-key-secret")

    credentials = AccessKey(access_key_id, access_key_secret)
    lara = Translator(credentials)
    
    print("🗒️  Glossaries require a specific subscription plan.")
    print("   If you encounter errors, please check your subscription level.\n")
    
    glossary_id = None
    
    try:
        # Example 1: Basic glossary management
        print("=== Basic Glossary Management ===")
        glossary = lara.glossaries.create("MyDemoGlossary")
        print(f"✅ Created glossary: {glossary.name} (ID: {glossary.id})")
        glossary_id = glossary.id
        
        # List all glossaries
        glossaries = lara.glossaries.list()
        print(f"📝 Total glossaries: {len(glossaries)}")
        print()

        # Example 2: Glossary operations
        print("=== Glossary Operations ===")
        # Get glossary details
        retrieved_glossary = lara.glossaries.get(glossary_id)
        if retrieved_glossary:
            print(f"📖 Glossary: {retrieved_glossary.name} (Owner: {retrieved_glossary.owner_id})")
        
        # Get glossary terms count
        counts = lara.glossaries.counts(glossary_id)

        if counts.unidirectional:
            for lang, count in counts.unidirectional.items():
                print(f"   {lang}: {count} entries")
        
        # Update glossary
        updated_glossary = lara.glossaries.update(glossary_id, "UpdatedDemoGlossary")
        print(f"📝 Updated name: '{glossary.name}' -> '{updated_glossary.name}'")

        # Example 3: CSV import functionality
        print("=== CSV Import Functionality ===")
        
        # Replace with your actual CSV file path
        csv_file_path = "sample_glossary.csv"  # Create this file with your glossary data
        
        if os.path.exists(csv_file_path):
            print(f"Importing CSV file: {os.path.basename(csv_file_path)}")
            csv_import = lara.glossaries.import_csv(glossary_id, csv_file_path)
            print(f"Import started with ID: {csv_import.id}")
            print(f"Initial progress: {round(csv_import.progress * 100)}%")
            
            # Check import status manually
            print("Checking import status...")
            import_status = lara.glossaries.get_import_status(csv_import.id)
            print(f"Current progress: {round(import_status.progress * 100)}%")
            
            # Wait for import to complete
            try:
                completed_import = lara.glossaries.wait_for_import(csv_import, max_wait_time=10)
                print("✅ Import completed!")
                print(f"Final progress: {round(completed_import.progress * 100)}%")
            except TimeoutError:
                print("Import timeout: The import process took too long to complete.")
            print()
        else:
            print(f"CSV file not found: {csv_file_path}")

        # Example 4: Export functionality
        print("=== Export Functionality ===")
        try:
            # Export as CSV table unidirectional format
            print("📤 Exporting as CSV table unidirectional...")
            csv_uni_data = lara.glossaries.export(glossary_id, content_type="csv/table-uni", source="en-US")
            print(f"✅ CSV unidirectional export successful ({len(csv_uni_data)} bytes)")

            # Save sample export to file - replace with your desired output path
            export_file_path = "exported_glossary.csv"  # Replace with actual path
            with open(export_file_path, 'wb') as f:
                f.write(csv_uni_data)
            print(f"💾 Sample export saved to: {os.path.basename(export_file_path)}")
            print()
        except Exception as e:
            print(f"Error with export: {e}\n")

        # Example 5: Glossary Terms Count
        print("=== Glossary Terms Count ===")
        try:
            # Get detailed counts
            detailed_counts = lara.glossaries.counts(glossary_id)
            
            print("📊 Detailed glossary terms count:")
            
            if detailed_counts.unidirectional:
                print("   Unidirectional entries by language pair:")
                for lang_pair, count in detailed_counts.unidirectional.items():
                    print(f"     {lang_pair}: {count} terms")
            else:
                print("   No unidirectional entries found")
            
            total_entries = 0
            if detailed_counts.unidirectional:
                total_entries += sum(detailed_counts.unidirectional.values())
            print(f"   Total entries: {total_entries}")
        except Exception as e:
            print(f"Error getting glossary terms count: {e}\n")

        # Example 6: Add/Replace and Delete glossary term entries
        print("=== Glossary Term Entries ===")
        try:
            # Add a new entry with multiple language terms
            terms = [
                GlossaryTerm(language="en-US", value="computer"),
                GlossaryTerm(language="it-IT", value="computer")
            ]
            add_result = lara.glossaries.add_or_replace_entry(glossary_id, terms)
            print(f"Added entry, import ID: {add_result.id}")

            # Add another entry with a custom GUID
            terms_with_guid = [
                GlossaryTerm(language="en-US", value="keyboard"),
                GlossaryTerm(language="it-IT", value="tastiera")
            ]
            lara.glossaries.add_or_replace_entry(glossary_id, terms_with_guid, guid="custom-guid-123")
            print("Added entry with custom GUID")

            # Replace an existing entry by using the same GUID
            updated_terms = [
                GlossaryTerm(language="en-US", value="keyboard"),
                GlossaryTerm(language="it-IT", value="tastiera"),
                GlossaryTerm(language="fr-FR", value="clavier")
            ]
            lara.glossaries.add_or_replace_entry(glossary_id, updated_terms, guid="custom-guid-123")
            print("Replaced entry using existing GUID")

            # Delete an entry by GUID
            lara.glossaries.delete_entry(glossary_id, guid="custom-guid-123")
            print("Deleted entry by GUID")

            # Delete an entry by term
            lara.glossaries.delete_entry(glossary_id, term=GlossaryTerm(language="en-US", value="computer"))
            print("Deleted entry by term")
            print()
        except Exception as e:
            print(f"Error with term entries: {e}\n")

    except Exception as e:
        print(f"Error creating glossary: {e}\n")
    finally:
        # Cleanup
        print("=== Cleanup ===")
        if glossary_id:
            try:
                deleted_glossary = lara.glossaries.delete(glossary_id)
                print(f"🗑️  Deleted glossary: {deleted_glossary.name}")
                
                # Clean up export files - replace with actual cleanup if needed
                export_file_path = "exported_glossary.csv"
                if os.path.exists(export_file_path):
                    os.remove(export_file_path)
                    print("🗑️  Cleaned up export file")
            except Exception as e:
                print(f"Error deleting glossary: {e}")
    
    print("\n🎉 Glossary management examples completed!")

if __name__ == "__main__":
    main() 