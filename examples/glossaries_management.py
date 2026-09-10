from lara_sdk import AccessKey, Translator, GlossaryTerm
import os

"""
Complete glossary management examples for the Lara Python SDK

This example demonstrates:
- Create, list, update, delete glossaries
- CSV import with status monitoring
- Glossary export (sync and async)
- Glossary terms count
- Import status checking
- Add/replace and delete glossary term entries
- Sharing a glossary with the account or a group (add, rename, list, revoke)
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
            csv_import = lara.glossaries.import_file(glossary_id, csv_file_path)
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

        # Example 4: CSV import with a callback URL (async notification when the import completes)
        print("=== CSV Import with Callback URL ===")
        if os.path.exists(csv_file_path):
            try:
                callback_url = "https://your-server.example.com/lara/import-callback"  # Replace with your endpoint
                import_with_callback = lara.glossaries.import_file(glossary_id, csv_file_path, callback_url=callback_url)
                print(f"Import started with ID: {import_with_callback.id} (callback: {callback_url})")
                print()
            except Exception as e:
                print(f"Error starting CSV import with callback: {e}\n")
        else:
            print(f"CSV file not found: {csv_file_path}")

        # Example 5: Export functionality
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

            # Async export - returns a job_id; the result is delivered to your callback URL when ready
            print("📤 Starting async export...")
            glossary_export = lara.glossaries.export_async(
                glossary_id,
                callback_url="https://your-server.example.com/lara/export-callback",  # Replace with your actual callback URL
                content_type="csv/table-uni",
                source="en-US"
            )
            print(f"✅ Async export started (job ID: {glossary_export.job_id})")
            print("   The export result will be delivered to your callback URL when ready.")
            print()
        except Exception as e:
            print(f"Error with export: {e}\n")

        # Example 6: Glossary Terms Count
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

        # Example 7: Add/Replace and Delete glossary term entries
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

        # Example 8: Glossary sharing
        # Sharing requires a multi-user account and the appropriate role (account owner for
        # account-wide shares, owner/admin for group shares). Each call returns the shared
        # glossary, whose `name` reflects the shared copy's name and `shared_at` the share time.
        print("=== Glossary Sharing ===")
        try:
            # Share with the whole account/team (the optional second argument names the shared copy)
            team_share = lara.glossaries.add_account_share(glossary_id, "Shared with the team")
            print(f"🤝 Shared with the account as: '{team_share.name}' (shared at {team_share.shared_at})")

            # Rename the account/team share
            renamed_team_share = lara.glossaries.rename_account_share(glossary_id, "Team glossary")
            print(f"📝 Renamed account share to: '{renamed_team_share.name}'")

            # List every share visible to the caller: the account share, group shares and user shares
            shares = lara.glossaries.get_shares(glossary_id)
            if shares.account:
                print(f"👥 Account share '{shares.account.share_name}' ({shares.account.permissions})")
            for group in shares.groups:
                print(f"👥 Group {group.name}: '{group.share_name}' ({group.permissions})")
            for user in shares.users:
                print(f"👤 User {user.name}: '{user.share_name}' ({user.permissions})")

            # Revoke the account/team share
            lara.glossaries.revoke_account_share(glossary_id)
            print("🚫 Revoked the account share")

            # Group shares work the same way, addressed by a group ID (grp_...)
            group_id = os.getenv("LARA_GROUP_ID")  # Replace with an actual group ID
            if group_id:
                group_share = lara.glossaries.add_group_share(glossary_id, group_id, "Shared with the group")
                print(f"🤝 Shared with group {group_id} as: '{group_share.name}'")

                lara.glossaries.rename_group_share(glossary_id, group_id, "Marketing group")
                print("📝 Renamed the group share")

                lara.glossaries.revoke_group_share(glossary_id, group_id)
                print("🚫 Revoked the group share")
            else:
                print("Set LARA_GROUP_ID to try the group sharing methods.")
            print()
        except Exception as e:
            print(f"Error sharing glossary: {e}\n")

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
