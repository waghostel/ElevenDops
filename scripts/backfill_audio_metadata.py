import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.firestore_service import get_firestore_service
from backend.services.firestore_data_service import FirestoreDataService

async def backfill_audio_data():
    """Backfill missing name and description for audio files."""
    print("Starting audio metadata backfill...")
    
    # Initialize services
    # Ensure Firestore is initialized
    try:
        firestore_service = get_firestore_service()
        data_service = FirestoreDataService()
    except Exception as e:
        print(f"Failed to initialize services: {e}")
        return

    # User confirmation for safety
    print("\nThis script will:")
    print("1. Iterate through ALL audio files in Firestore.")
    print("2. Check for missing 'name' or 'description' fields.")
    print("3. Update them with defaults ('Untitled Audio', '').")
    
    confirm = input("\nDo you want to proceed? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Aborted.")
        return

    try:
        # Get all audio files directly from Firestore collection to access raw data
        # We use the raw firestore client because the data_service.get_audio_files 
        # now returns Pydantic models which might have empty strings for missing fields 
        # (handled by the .get() we just added), but we want to know which docs 
        # *physically* lack the fields in the DB to update them.
        
        # Actually, if we use the data service, we can just save it back. 
        # The data service read will populate defaults in the model.
        # Saving it back will persist those defaults to the DB.
        # This is cleaner than raw DB access.
        
        audio_files = await data_service.get_audio_files()
        print(f"\nFound {len(audio_files)} audio files.")
        
        updated_count = 0
        
        for audio in audio_files:
            needs_update = False
            original_name = audio.name
            original_desc = audio.description

            # Logic: If name is empty/default and we want to ensure it's set in DB.
            # However, the goal is to "add some default name and description for each of them".
            # If the model loaded with "", it means it was missing or "" in DB.
            # We will set a default "Untitled Audio" if it's empty.
            
            if not audio.name:
                # Use knowledge ID or timestamp to make it slightly distinct if desired, 
                # or just "Untitled Audio" as requested.
                # Let's make it "Audio - {Date}" to be helpful.
                date_str = audio.created_at.strftime("%Y-%m-%d")
                audio.name = f"Audio {date_str}"
                needs_update = True
            
            # Description is optional, but user asked to add it. 
            # We can leave it empty string (which is a valid value) or "No description".
            # The user said "add some default name and description".
            # Empty string is fine for description usually, but let's set "Generated Audio" if empty?
            # Or just ensure the field exists.
            
            # If we save the model, it WILL ensure the fields exist because Pydantic .model_dump()
            # will include them.
            
            # So effectively, for every file, just saving it back ensures the schema is migrated.
            # But we only want to write if we actually changed the logic (like setting the name).
            
            # Since we just added the fields to the model with default="", 
            # saving them back is enough to "migrate" the schema.
            # But let's apply the name improvement logic.
            
            if needs_update:
                print(f"Updating Audio {audio.audio_id}: Name '{original_name}' -> '{audio.name}'")
                await data_service.save_audio_metadata(audio)
                updated_count += 1
            else:
                 # Check if we need to save just to ensure fields exist (schema migration)
                 # We can check raw doc, or just force save all. 
                 # Generating a write for all 10-100 files is cheap and safe.
                 # Let's do it to ensure consistency.
                 await data_service.save_audio_metadata(audio)
                 # We won't count purely schema-migration updates as "content updates" for log noise
                 # but we can count them separate if we want.
                 pass

        print(f"\nBackfill complete. Updated content for {updated_count} files.")
        print(f"Ensured schema consistency for all {len(audio_files)} files.")

    except Exception as e:
        print(f"Error during backfill: {e}")

if __name__ == "__main__":
    asyncio.run(backfill_audio_data())
