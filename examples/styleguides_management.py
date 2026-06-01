from lara_sdk import AccessKey, Translator
import os

"""
Complete styleguide management examples for the Lara Python SDK

This example demonstrates:
- Create, list, get, update, delete styleguides
- Update name, content, or both at once
- Handling of non-existent styleguides
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

    print("📋 Styleguides require a specific subscription plan.")
    print("   If you encounter errors, please check your subscription level.\n")

    styleguide_id = None

    try:
        # Example 1: Basic styleguide management
        print("=== Basic Styleguide Management ===")
        styleguide = lara.styleguides.create("MyDemoStyleguide", "Use a formal tone. Prefer British English spelling. Avoid contractions.")
        print(f"✅ Created styleguide: {styleguide.name} (ID: {styleguide.id})")
        styleguide_id = styleguide.id

        # List all styleguides
        styleguides = lara.styleguides.list()
        print(f"📝 Total styleguides: {len(styleguides)}")
        print()

        # Example 2: Styleguide operations
        print("=== Styleguide Operations ===")
        retrieved_styleguide = lara.styleguides.get(styleguide_id)
        if retrieved_styleguide:
            print(f"📖 Styleguide: {retrieved_styleguide.name} (Owner: {retrieved_styleguide.owner_id})")
            print(f"📄 Content: {retrieved_styleguide.content}")
        print()

        # Example 3: Update styleguide
        print("=== Update Styleguide ===")
        try:
            # Update only the name
            renamed_styleguide = lara.styleguides.update(styleguide_id, "UpdatedDemoStyleguide")
            print(f"📝 Updated name: '{styleguide.name}' -> '{renamed_styleguide.name}'")

            # Update only the content
            updated_styleguide = lara.styleguides.update(styleguide_id, content="Use a casual tone. Prefer American English spelling. Contractions are welcome.")
            print(f"📝 Updated content for styleguide: {updated_styleguide.name}")

            # Update both name and content
            fully_updated = lara.styleguides.update(styleguide_id, "FinalDemoStyleguide", "Use clear and concise language. Avoid jargon.")
            print(f"📝 Updated name and content: {fully_updated.name}")
        except Exception as e:
            print(f"Error updating styleguide: {e}\n")
        print()

        # Example 4: Get a non-existent styleguide
        print("=== Get Non-Existent Styleguide ===")
        try:
            missing = lara.styleguides.get("non-existent-id")
            if missing is None:
                print("ℹ️  Styleguide not found (returned None as expected)")
        except Exception as e:
            print(f"Error getting styleguide: {e}\n")
        print()

    except Exception as e:
        print(f"Error creating styleguide: {e}\n")
    finally:
        # Cleanup
        print("=== Cleanup ===")
        if styleguide_id:
            try:
                deleted_styleguide = lara.styleguides.delete(styleguide_id)
                print(f"🗑️  Deleted styleguide: {deleted_styleguide.name}")
            except Exception as e:
                print(f"Error deleting styleguide: {e}")

    print("\n🎉 Styleguide management examples completed!")

if __name__ == "__main__":
    main()
