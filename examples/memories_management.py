from lara_sdk import Credentials, Translator
import os

"""
Complete memory management examples for the Lara Python SDK

This example demonstrates:
- Create, list, update, delete memories
- Add individual translations
- Multiple memory operations
- TMX file import with progress monitoring
- Translation deletion
- Translation with TUID and context
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
    
    memory_id = None
    external_memory_id = None
    memory_2_to_delete = None
    
    try:
        # Example 1: Basic memory management
        print("=== Basic Memory Management ===")
        memory = lara.memories.create("MyDemoMemory")
        print(f"✅ Created memory: {memory.name} (ID: {memory.id})")
        memory_id = memory.id

        # Get memory details
        retrieved_memory = lara.memories.get(memory_id)
        if retrieved_memory:
            print(f"📖 Memory: {retrieved_memory.name} (Owner: {retrieved_memory.owner_id})")

        # Update memory
        updated_memory = lara.memories.update(memory_id, "UpdatedDemoMemory")
        print(f"📝 Updated name: '{memory.name}' -> '{updated_memory.name}'")
        print()
        
        # List all memories
        memories = lara.memories.list()
        print(f"📝 Total memories: {len(memories)}")
        print()

        # Example 2: Adding translations
        # Important: To update/overwrite a translation unit you must provide a tuid. Calls without a tuid always create a new unit and will not update existing entries.
        print("=== Adding Translations ===")
        try:
            # Basic translation addition (with TUID)
            mem_import1 = lara.memories.add_translation(memory_id, "en-US", "fr-FR", "Hello", "Bonjour", tuid="greeting_001")
            print(f"✅ Added: 'Hello' -> 'Bonjour' with TUID 'greeting_001' (Import ID: {mem_import1.id})")
            
            # Translation with context
            mem_import2 = lara.memories.add_translation(
                memory_id, "en-US", "fr-FR", "How are you?", "Comment allez-vous?", 
                tuid="greeting_002",
                sentence_before="Good morning", 
                sentence_after="Have a nice day"
            )
            print(f"✅ Added with context (Import ID: {mem_import2.id})")
            print()
        except Exception as e:
            print(f"Error adding translations: {e}\n")

        # Example 3: Multiple memory operations
        print("=== Multiple Memory Operations ===")
        try:
            # Create second memory for multi-memory operations
            memory2 = lara.memories.create("SecondDemoMemory")
            memory_2_id = memory2.id
            print(f"✅ Created second memory: {memory2.name}")
            
            # Add translation to multiple memories (with TUID)
            memory_ids = [memory_id, memory_2_id]
            multi_import_job = lara.memories.add_translation(memory_ids, "en-US", "it-IT", "Hello World!", "Ciao Mondo!", tuid="greeting_003")
            print(f"✅ Added translation to multiple memories (Import ID: {multi_import_job.id})")
            print()
            
            # Store for cleanup
            memory_2_to_delete = memory_2_id
        except Exception as e:
            print(f"Error with multiple memory operations: {e}\n")
            memory_2_to_delete = None

        # Example 4: TMX import functionality
        print("=== TMX Import Functionality ===")
        
        # Replace with your actual TMX file path
        tmx_file_path = "sample_memory.tmx"  # Create this file with your TMX content
        
        if os.path.exists(tmx_file_path):
            try:
                print(f"Importing TMX file: {os.path.basename(tmx_file_path)}")
                tmx_import = lara.memories.import_tmx(memory_id, tmx_file_path)
                print(f"Import started with ID: {tmx_import.id}")
                print(f"Initial progress: {round(tmx_import.progress * 100)}%")
                
                # Wait for import to complete
                try:
                    completed_import = lara.memories.wait_for_import(tmx_import, max_wait_time=10)
                    print("✅ Import completed!")
                    print(f"Final progress: {round(completed_import.progress * 100)}%")
                except TimeoutError:
                    print("Import timeout: The import process took too long to complete.")
                print()
            except Exception as e:
                print(f"Error with TMX import: {e}\n")
        else:
            print(f"TMX file not found: {tmx_file_path}")

        # Example 5: Translation deletion
        print("=== Translation Deletion ===")
        try:
            # Delete a specific translation unit (with TUID)
            # Important: if you omit tuid, all entries that match the provided fields will be removed
            delete_job = lara.memories.delete_translation(
                memory_id,
                "en-US",
                "fr-FR", 
                "Hello",
                "Bonjour",
                tuid="greeting_001"  # Specify the TUID to delete a specific translation unit
            )
            print(f"🗑️  Deleted translation unit (Job ID: {delete_job.id})")
            print()
        except Exception as e:
            print(f"Error deleting translation: {e}\n")

    except Exception as e:
        print(f"Error creating memory: {e}\n")
    finally:
        # Cleanup
        print("=== Cleanup ===")
        if memory_id:
            try:
                deleted_memory = lara.memories.delete(memory_id)
                print(f"🗑️  Deleted memory: {deleted_memory.name}")
            except Exception as e:
                print(f"Error deleting memory: {e}")
        
        if external_memory_id:
            try:
                deleted_external_memory = lara.memories.delete(external_memory_id)
                print(f"🗑️  Deleted external memory: {deleted_external_memory.name}")
            except Exception as e:
                print(f"Error deleting external memory: {e}")
        
        if memory_2_to_delete:
            try:
                deleted_memory2 = lara.memories.delete(memory_2_to_delete)
                print(f"🗑️  Deleted second memory: {deleted_memory2.name}")
            except Exception as e:
                print(f"Error deleting second memory: {e}")
    
    print("\n🎉 Memory management examples completed!")

if __name__ == "__main__":
    main() 