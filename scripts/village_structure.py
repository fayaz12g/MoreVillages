import os
import shutil
from nbtlib import load, File
from nbtlib import String

# -------------------------------
# Build wood replacement map
# -------------------------------
def build_wood_map(wood_id):
    """
    wood_id: string like 'minecraft:cherry' or 'morevillages:palm'
    """
    namespace, wood = wood_id.split(":")
    return {
        "minecraft:oak_planks": f"{namespace}:{wood}_planks",
        "minecraft:oak_log": f"{namespace}:{wood}_log",
        "minecraft:stripped_oak_log": f"{namespace}:stripped_{wood}_log",
        "minecraft:oak_wood": f"{namespace}:{wood}_wood",
        "minecraft:stripped_oak_wood": f"{namespace}:stripped_{wood}_wood",
        "minecraft:oak_stairs": f"{namespace}:{wood}_stairs",
        "minecraft:oak_slab": f"{namespace}:{wood}_slab",
        "minecraft:oak_fence": f"{namespace}:{wood}_fence",
        "minecraft:oak_fence_gate": f"{namespace}:{wood}_fence_gate",
        "minecraft:oak_door": f"{namespace}:{wood}_door",
        "minecraft:oak_trapdoor": f"{namespace}:{wood}_trapdoor",
        "minecraft:oak_button": f"{namespace}:{wood}_button",
        "minecraft:oak_pressure_plate": f"{namespace}:{wood}_pressure_plate",
        "minecraft:oak_sign": f"{namespace}:{wood}_sign",
        "minecraft:oak_hanging_sign": f"{namespace}:{wood}_hanging_sign",
    }


# -------------------------------
# Stone family definitions
# -------------------------------
STONE_FAMILIES = {
    "stone": {
        "cobblestone": "cobblestone",
        "stone_bricks": "stone_bricks",
        "mossy_cobblestone": "mossy_cobblestone",
        "mossy_stone_bricks": "mossy_stone_bricks",
        "slab": "stone_slab",
        "stairs": "stone_stairs",
        "wall": "cobblestone_wall",
    },
    "deepslate": {
        "cobblestone": "cobbled_deepslate",
        "stone_bricks": "deepslate_bricks",
        "mossy_cobblestone": "deepslate_tiles",
        "mossy_stone_bricks": "deepslate_tiles",
        "slab": "deepslate_slab",
        "stairs": "deepslate_stairs",
        "wall": "deepslate_wall",
    },
    "granite": {
        "cobblestone": "granite",
        "stone_bricks": "polished_granite",
        "mossy_cobblestone": "granite",
        "mossy_stone_bricks": "polished_granite",
        "slab": "granite_slab",
        "stairs": "granite_stairs",
        "wall": "granite_wall",
    },
    "diorite": {
        "cobblestone": "diorite",
        "stone_bricks": "polished_diorite",
        "mossy_cobblestone": "diorite",
        "mossy_stone_bricks": "polished_diorite",
        "slab": "diorite_slab",
        "stairs": "diorite_stairs",
        "wall": "diorite_wall",
    },
    "andesite": {
        "cobblestone": "andesite",
        "stone_bricks": "polished_andesite",
        "mossy_cobblestone": "andesite",
        "mossy_stone_bricks": "polished_andesite",
        "slab": "andesite_slab",
        "stairs": "andesite_stairs",
        "wall": "andesite_wall",
    },
}

def build_stone_map(stone):
    family = STONE_FAMILIES[stone]
    return {
        "minecraft:cobblestone": f"minecraft:{family['cobblestone']}",
        "minecraft:stone_bricks": f"minecraft:{family['stone_bricks']}",
        "minecraft:mossy_cobblestone": f"minecraft:{family['mossy_cobblestone']}",
        "minecraft:mossy_stone_bricks": f"minecraft:{family['mossy_stone_bricks']}",
        "minecraft:stone_slab": f"minecraft:{family['slab']}",
        "minecraft:stone_stairs": f"minecraft:{family['stairs']}",
        "minecraft:stone_wall": f"minecraft:{family['wall']}",
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
            block["Name"] = String(new_val)  # ✅ wrap in NBT string

    try:
        nbt.save(out_path)
    except Exception as e:
        print(f"⚠️ Could not save {out_path}: {e}")

# -------------------------------
# Full theme mapping
# -------------------------------
VILLAGE_THEMES = {
    "cherry":        {"wood": "minecraft:cherry",   "stone": "deepslate", "base": "taiga"},
    "birch":         {"wood": "minecraft:birch",    "stone": "diorite",   "base": "plains"},
    "dark_oak":      {"wood": "minecraft:dark_oak", "stone": "granite",   "base": "savanna"},
    "pale_oak":      {"wood": "minecraft:pale_oak", "stone": "andesite",  "base": "savanna"},
    "bamboo_jungle": {"wood": "minecraft:bamboo",   "stone": "stone",     "base": "plains"},
    "mangrove":      {"wood": "minecraft:mangrove", "stone": "stone",     "base": "plains"},
    "beach":         {"wood": "morevillages:palm",  "stone": "sandstone", "base": "plains"},
    "stony_shore":   {"wood": "minecraft:oak",      "stone": "andesite",  "base": "plains"},
    "badlands":      {"wood": "minecraft:oak",      "stone": "granite",   "base": "desert"},
    "ice_spikes":    {"wood": "minecraft:spruce",   "stone": "stone",     "base": "snowy"},
}

# -------------------------------
# Main reskin function
# -------------------------------
def reskin_villages(base_dir, out_dir):
    for theme, mats in VILLAGE_THEMES.items():
        base = mats["base"]

        wood_map = build_wood_map(mats["wood"])
        stone_map = build_stone_map(mats["stone"]) if mats["stone"] in STONE_FAMILIES else {}
        replacements = {**wood_map, **stone_map}

        base_path = os.path.join(base_dir, base)
        theme_dir = os.path.join(out_dir, theme)

        print(f"\n--- Processing theme: {theme} (base: {base}) ---")
        print("Base path:", os.path.abspath(base_path))

        if not os.path.exists(base_path):
            print("!! Base path does not exist, skipping")
            continue

        if os.path.exists(theme_dir):
            shutil.rmtree(theme_dir)

        for root, _, files in os.walk(base_path):
            rel_path = root.replace(base_path, "").replace(base, theme)
            new_root = os.path.join(theme_dir, rel_path.lstrip(os.sep))
            os.makedirs(new_root, exist_ok=True)

            for f in files:
                if f.endswith(".nbt"):
                    print("Found NBT:", f)
                    new_name = f.replace(base, theme)
                    in_path = os.path.join(root, f)
                    out_path = os.path.join(new_root, new_name)
                    reskin_nbt(in_path, out_path, replacements)


# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    reskin_villages(
        base_dir="./data/minecraft/structures/village",  
        out_dir="./data/morevillages/structures/village"
    )
