import os
import shutil
from nbtlib import load, String

# -------------------------------
# Wood replacement map (Dark Oak → Pale Oak)
# -------------------------------
def build_paleoak_wood_map():
    return {
        "minecraft:dark_oak_planks": "minecraft:pale_oak_planks",
        "minecraft:dark_oak_log": "minecraft:pale_oak_log",
        "minecraft:stripped_dark_oak_log": "minecraft:stripped_pale_oak_log",
        "minecraft:dark_oak_wood": "minecraft:pale_oak_wood",
        "minecraft:stripped_dark_oak_wood": "minecraft:stripped_pale_oak_wood",
        "minecraft:dark_oak_stairs": "minecraft:pale_oak_stairs",
        "minecraft:dark_oak_slab": "minecraft:pale_oak_slab",
        "minecraft:dark_oak_fence": "minecraft:pale_oak_fence",
        "minecraft:dark_oak_fence_gate": "minecraft:pale_oak_fence_gate",
        "minecraft:dark_oak_door": "minecraft:pale_oak_door",
        "minecraft:dark_oak_trapdoor": "minecraft:pale_oak_trapdoor",
        "minecraft:dark_oak_button": "minecraft:pale_oak_button",
        "minecraft:dark_oak_pressure_plate": "minecraft:pale_oak_pressure_plate",
        "minecraft:dark_oak_sign": "minecraft:pale_oak_sign",
        "minecraft:dark_oak_hanging_sign": "minecraft:pale_oak_hanging_sign",
    }

# -------------------------------
# Stone replacement map (Cobble → Cobbled Deepslate)
# -------------------------------
def build_stone_map():
    return {
        "minecraft:cobblestone": "minecraft:cobbled_deepslate",
        "minecraft:stone_slab": "minecraft:deepslate_slab",   # vanilla doesn’t have "cobbled_deepslate_slab"
        "minecraft:stone_stairs": "minecraft:deepslate_stairs",
        "minecraft:stone_wall": "minecraft:deepslate_wall",
        "minecraft:cobblestone_slab": "minecraft:cobbled_deepslate_slab",
        "minecraft:cobblestone_stairs": "minecraft:cobbled_deepslate_stairs",
        "minecraft:cobblestone_wall": "minecraft:cobbled_deepslate_wall",
    }

# -------------------------------
# Replace block IDs in a structure NBT
# -------------------------------
def reskin_nbt(path, out_path, replacements):
    try:
        nbt = load(path)
    except Exception as e:
        print(f"⚠️ Could not load {path}: {e}")
        return

    palette = nbt.get("palette", [])
    for block in palette:
        name = block["Name"]
        if name in replacements:
            new_val = replacements[name]
            print(f"Replacing {name} -> {new_val}")
            block["Name"] = String(new_val)  # keep as NBT string

    try:
        nbt.save(out_path)
    except Exception as e:
        print(f"⚠️ Could not save {out_path}: {e}")

# -------------------------------
# Main reskin function
# -------------------------------
def reskin_mansion(base_dir, out_dir):
    wood_map = build_paleoak_wood_map()
    stone_map = build_stone_map()
    replacements = {**wood_map, **stone_map}

    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    for root, _, files in os.walk(base_dir):
        rel_path = root.replace(base_dir, "")
        new_root = os.path.join(out_dir, rel_path.lstrip(os.sep))
        os.makedirs(new_root, exist_ok=True)

        for f in files:
            if f.endswith(".nbt"):
                in_path = os.path.join(root, f)
                out_path = os.path.join(new_root, f.replace("woodland_mansion", "paleoak_mansion"))
                print(f"Processing {f}")
                reskin_nbt(in_path, out_path, replacements)

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    reskin_mansion(
        base_dir="./data/minecraft/structures/woodland_mansion",
        out_dir="./data/morevillages/structures/paleoak_mansion"
    )
