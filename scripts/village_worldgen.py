# scripts/worldgen_fix.py
import os
import shutil
import json

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

MOD_NS = "morevillages"  # output namespace used for new structure references


def replace_in_string(s: str, base: str, theme: str, mod_ns: str = MOD_NS) -> str:
    """
    Replace common patterns in strings so references point to the new theme.
    This covers both "minecraft:village/plains/..." forms and file-name forms like "taiga_small_house_1".
    """
    # specific replacements for structure start_pool and fully-qualified paths
    s = s.replace(f"minecraft:village/{base}", f"{mod_ns}:village/{theme}")
    s = s.replace(f"minecraft:village_{base}", f"{mod_ns}:village_{theme}")
    # replace generic "village/<base>" without namespace
    s = s.replace(f"village/{base}", f"{mod_ns}:village/{theme}")
    # file-name style: "village_<base>" -> "village_<theme>"
    s = s.replace(f"village_{base}", f"village_{theme}")
    # filenames like "taiga_small_house_1" -> "cherry_small_house_1"
    s = s.replace(f"{base}_", f"{theme}_")
    # segments like "/taiga/" -> "/cherry/"
    s = s.replace(f"/{base}/", f"/{theme}/")
    # trailing "/taiga" -> "/cherry"
    s = s.replace(f"/{base}", f"/{theme}")
    return s


def recursive_replace(obj, base: str, theme: str):
    """Recursively walk JSON-like object and replace strings using replace_in_string."""
    if isinstance(obj, str):
        return replace_in_string(obj, base, theme)
    if isinstance(obj, list):
        return [recursive_replace(x, base, theme) for x in obj]
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            # replace in keys only if keys themselves contain strings referencing base (rare)
            new_key = replace_in_string(k, base, theme) if isinstance(k, str) else k
            new[new_key] = recursive_replace(v, base, theme)
        return new
    return obj


def copy_and_rename_pool(in_pool: str, out_pool: str, base: str, theme: str):
    """
    Copy a template_pool folder (in_pool) to out_pool.
    Rename files and replace internal JSON references.
    """
    if os.path.exists(out_pool):
        shutil.rmtree(out_pool)
    for root, dirs, files in os.walk(in_pool):
        rel = os.path.relpath(root, in_pool)
        dest_root = os.path.join(out_pool, rel) if rel != "." else out_pool
        os.makedirs(dest_root, exist_ok=True)
        for fname in files:
            src = os.path.join(root, fname)
            new_fname = fname.replace(base, theme)
            dest = os.path.join(dest_root, new_fname)
            shutil.copy2(src, dest)

            # If JSON, load and recursively replace string tokens inside
            if dest.lower().endswith(".json"):
                try:
                    with open(dest, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    data = recursive_replace(data, base, theme)
                    with open(dest, "w", encoding="utf-8") as fh:
                        json.dump(data, fh, indent=2)
                except Exception as e:
                    print(f"Warning: failed to process JSON {dest}: {e}")


def copy_and_fix_structure_json(in_struct: str, out_struct: str, base: str, theme: str):
    """Load a structure JSON, recursively replace strings, and write to out_struct."""
    with open(in_struct, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data = recursive_replace(data, base, theme)
    os.makedirs(os.path.dirname(out_struct), exist_ok=True)
    with open(out_struct, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def reskin_worldgen(base_dir="./data/minecraft", out_dir="./data/morevillages"):
    struct_dir = os.path.join("worldgen", "structure")
    pool_dir = os.path.join("worldgen", "template_pool", "village")
    set_path = os.path.join("worldgen", "structure_set", "villages.json")

    base_struct_dir = os.path.join(base_dir, struct_dir)
    base_pool_dir = os.path.join(base_dir, pool_dir)
    base_set_path = os.path.join(base_dir, set_path)

    out_struct_dir = os.path.join(out_dir, struct_dir)
    out_pool_dir = os.path.join(out_dir, pool_dir)
    out_set_path = os.path.join(out_dir, set_path)

    # copy villages.json (structure_set) and load it
    os.makedirs(os.path.dirname(out_set_path), exist_ok=True)
    shutil.copy2(base_set_path, out_set_path)
    with open(out_set_path, "r", encoding="utf-8") as fh:
        villages_set = json.load(fh)

    for theme, mats in VILLAGE_THEMES.items():
        base = mats["base"]
        print(f"\nProcessing theme: {theme}  (base: {base})")

        # 1) structure JSON (village_<base>.json -> village_<theme>.json)
        in_struct = os.path.join(base_struct_dir, f"village_{base}.json")
        out_struct = os.path.join(out_struct_dir, f"village_{theme}.json")
        if not os.path.exists(in_struct):
            print(f"  Skipping structure JSON (not found): {in_struct}")
        else:
            copy_and_fix_structure_json(in_struct, out_struct, base, theme)
            print(f"  Wrote structure JSON: {out_struct}")

        # 2) template_pool folder
        in_pool = os.path.join(base_pool_dir, base)
        out_pool = os.path.join(out_pool_dir, theme)
        if not os.path.exists(in_pool):
            print(f"  Skipping template pool (not found): {in_pool}")
        else:
            copy_and_rename_pool(in_pool, out_pool, base, theme)
            print(f"  Copied and renamed pool folder: {out_pool}")

        # 3) add entry to villages.json
        new_struct_id = f"{MOD_NS}:village_{theme}"
        if "structures" not in villages_set:
            villages_set["structures"] = []
        if not any(s.get("structure") == new_struct_id for s in villages_set["structures"]):
            villages_set["structures"].append({"structure": new_struct_id, "weight": 1})
            print(f"  Added structure_set entry: {new_struct_id}")
        else:
            print(f"  structure_set already contains {new_struct_id}")

    # Save updated villages.json
    with open(out_set_path, "w", encoding="utf-8") as fh:
        json.dump(villages_set, fh, indent=2)
    print("\n✅ worldgen JSONs generated/updated at:", os.path.abspath(out_dir))


if __name__ == "__main__":
    # Run the fixer: adjust base_dir/out_dir as needed
    reskin_worldgen(base_dir="./data/minecraft", out_dir="./data/morevillages")
