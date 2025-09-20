import os
import json
import shutil

VILLAGE_THEMES = {
    "cherry":        {"biomes": ["minecraft:cherry_grove"]},
    "birch":         {"biomes": ["minecraft:birch_forest", "minecraft:old_growth_birch_forest"]},
    "dark_oak":      {"biomes": ["minecraft:dark_forest"]},
    "pale_oak":      {"biomes": ["minecraft:pale_oak_forest"]},  # custom biome if you added one
    "bamboo_jungle": {"biomes": ["minecraft:bamboo_jungle"]},
    "mangrove":      {"biomes": ["minecraft:mangrove_swamp"]},
    "beach":         {"biomes": ["minecraft:beach"]},
    "stony_shore":   {"biomes": ["minecraft:stony_shore"]},
    "badlands":      {"biomes": ["minecraft:badlands", "minecraft:eroded_badlands", "minecraft:wooded_badlands"]},
    "ice_spikes":    {"biomes": ["minecraft:ice_spikes"]},
}

MOD_NS = "morevillages"

def reskin_tags(base_dir="./data/minecraft", out_dir="./data/morevillages"):
    # Biome tags folder
    biome_tag_dir = os.path.join(out_dir, "tags", "worldgen", "biome", "has_structure")
    os.makedirs(biome_tag_dir, exist_ok=True)

    # Structure tag (village.json)
    struct_tag_in = os.path.join(base_dir, "tags", "worldgen", "structure", "village.json")
    struct_tag_out = os.path.join(out_dir, "tags", "worldgen", "structure", "village.json")
    os.makedirs(os.path.dirname(struct_tag_out), exist_ok=True)

    # Copy vanilla structure tag first
    shutil.copy2(struct_tag_in, struct_tag_out)
    with open(struct_tag_out, "r", encoding="utf-8") as f:
        struct_tag = json.load(f)

    # Process each theme
    for theme, mats in VILLAGE_THEMES.items():
        # --- biome tag ---
        biome_file = os.path.join(biome_tag_dir, f"village_{theme}.json")
        biome_json = {"values": mats["biomes"]}
        with open(biome_file, "w", encoding="utf-8") as f:
            json.dump(biome_json, f, indent=2)
        print(f"Created biome tag: {biome_file}")

        # --- structure tag ---
        struct_id = f"{MOD_NS}:village_{theme}"
        if struct_id not in struct_tag["values"]:
            struct_tag["values"].append(struct_id)
            print(f"Added structure ID to tag: {struct_id}")

    # Save updated structure tag
    with open(struct_tag_out, "w", encoding="utf-8") as f:
        json.dump(struct_tag, f, indent=2)

    print("\n✅ Tags generated/updated at:", os.path.abspath(out_dir))


if __name__ == "__main__":
    reskin_tags(
        base_dir="./data/minecraft",
        out_dir="./data/morevillages"
    )
