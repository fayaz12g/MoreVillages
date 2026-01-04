import os
import nbtlib
from pathlib import Path

# A quick way to replace minecraft villages namespace in NBT files
def replace_namespace_in_nbt(file_path, old_namespace, new_namespace):
    """Replace namespace in an NBT file"""
    try:
        # Load the NBT file
        nbt_file = nbtlib.load(file_path)

        # Track if any changes were made
        changed = False

        # Recursive function to process NBT data
        def process_nbt_data(data):
            nonlocal changed

            if isinstance(data, nbtlib.tag.Compound):
                for key, value in data.items():
                    if isinstance(value, nbtlib.tag.String):
                        old_value = str(value)
                        if old_namespace in old_value:
                            new_value = old_value.replace(old_namespace, new_namespace)
                            data[key] = nbtlib.String(new_value)
                            changed = True
                            print(f"  Changed: {old_value} -> {new_value}")
                    else:
                        process_nbt_data(value)
            elif isinstance(data, nbtlib.tag.List):
                for item in data:
                    process_nbt_data(item)

        # Process the NBT data
        process_nbt_data(nbt_file)

        # Save if changes were made
        if changed:
            nbt_file.save(file_path)
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    # Configuration
    OLD_NAMESPACE = "minecraft"
    NEW_NAMESPACE = "more-villages"
    ROOT_DIR = "./data/morevillages/structures/village/"
    ROOT_DIR = ROOT_DIR + "bamboo_jungle" # Update this line to the target village

    print(f"Searching for NBT files in: {os.path.abspath(ROOT_DIR)}")
    print(f"Replacing '{OLD_NAMESPACE}' with '{NEW_NAMESPACE}'")
    print("-" * 60)

    # Find all NBT files
    nbt_files = list(Path(ROOT_DIR).rglob("*.nbt"))

    if not nbt_files:
        print("No NBT files found!")
        return

    print(f"Found {len(nbt_files)} NBT files\n")

    # Process each file
    modified_count = 0
    for nbt_file in nbt_files:
        print(f"Processing: {nbt_file}")
        if replace_namespace_in_nbt(nbt_file, OLD_NAMESPACE, NEW_NAMESPACE):
            modified_count += 1
            print(f"  ✓ Modified")
        else:
            print(f"  - No changes needed")
        print()

    print("-" * 60)
    print(f"Complete! Modified {modified_count} out of {len(nbt_files)} files")

if __name__ == "__main__":
    main()