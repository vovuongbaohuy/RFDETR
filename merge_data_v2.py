import json
import shutil
from pathlib import Path
from collections import OrderedDict

def merge_coco_datasets(
    dataset_paths,
    output_root,
    splits=("train", "valid", "test"),
    info_block=None,
    licenses_block=None,
):
    """
    Merge multiple COCO-style datasets (each split has images directly under the split folder
    and an _annotations.
    
    coco.json file) into one dataset with the same split names.

    - Input per dataset:
        <dataset>/train/_annotations.coco.json + images (*.jpg/png/...)
        <dataset>/valid/_annotations.coco.json + images
        <dataset>/test/_annotations.coco.json + images

    - Output:
        <output_root>/train/_annotations.coco.json + merged images
        <output_root>/valid/_annotations.coco.json + merged images
        <output_root>/test/_annotations.coco.json + merged images
    """

    dataset_paths = [Path(p) for p in dataset_paths]
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    # ---------- 1) Build a GLOBAL category mapping (same across splits) ----------
    # We scan ALL provided splits in ALL datasets to collect the union of category names.
    cat_name_to_id = OrderedDict()  # preserve insertion order
    cat_name_to_super = {}

    for dpath in dataset_paths:
        for split in splits:
            ann_path = dpath / split / "_annotations_cleaned.coco.json"
            if not ann_path.exists():
                continue
            with ann_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            for cat in data.get("categories", []):
                name = cat["name"]
                if name not in cat_name_to_id:
                    cat_name_to_id[name] = len(cat_name_to_id)  # 0-based IDs
                    cat_name_to_super[name] = cat.get("supercategory", "vehicle")

    # Prepare the categories list once (shared across all output splits)
    global_categories = [
        {"id": new_id, "name": name, "supercategory": cat_name_to_super.get(name, "vehicle")}
        for name, new_id in cat_name_to_id.items()
    ]

    # Default info/licenses blocks if not provided
    if info_block is None:
        info_block = {
            "description": "Nepali Vehicle Dataset",
            "version": "1.0",
            "year": 2025,
            "contributor": "Custom Conversion",
            "date_created": "2025-08-19"
        }
    if licenses_block is None:
        licenses_block = [
            {"id": 1, "name": "Unknown", "url": "http://example.com"}
        ]

    # ---------- 2) Merge each split separately ----------
    for split in splits:
        out_split_dir = output_root / split
        out_split_dir.mkdir(parents=True, exist_ok=True)

        merged_images = []
        merged_annotations = []

        # Running counters (fresh per split)
        next_image_id = 1
        next_ann_id = 1

        # For quick remap by name
        def remap_cat_id(old_cat_id, local_categories):
            # Find the category name in local file, then map to global ID
            name = None
            for c in local_categories:
                if c["id"] == old_cat_id:
                    name = c["name"]
                    break
            if name is None:
                raise KeyError(f"Category id {old_cat_id} not found in local categories.")
            if name not in cat_name_to_id:
                # Shouldn't happen because we pre-built global categories
                raise KeyError(f"Category '{name}' missing from global mapping.")
            return cat_name_to_id[name]

        for dpath in dataset_paths:
            ds_split_dir = dpath / split
            ann_path = ds_split_dir / "_annotations_cleaned.coco.json"
            if not ann_path.exists():
                print(f"Skipping: {ann_path} not found.")
                continue

            with ann_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            local_images = data.get("images", [])
            local_annotations = data.get("annotations", [])
            local_categories = data.get("categories", [])

            # Map old image_id -> new image_id for this dataset chunk
            img_id_map = {}

            # Copy images and write image entries
            for img in local_images:
                old_img_id = img["id"]
                src_name = img["file_name"]

                # Build new filename with dataset prefix to avoid collisions
                dataset_prefix = dpath.name  # folder name as prefix
                new_filename = f"{dataset_prefix}_{src_name}"

                # Source and destination paths (images live directly under split dir)
                src_path = ds_split_dir / src_name
                dst_path = out_split_dir / new_filename

                if not src_path.exists():
                    print(f"Missing image file: {src_path} (skipping this image/its anns)")
                    continue

                # Copy image
                shutil.copy2(src_path, dst_path)

                # Create new image record
                new_img = {
                    **img,  # copy original fields (width, height, etc.)
                    "id": next_image_id,
                    "file_name": new_filename,
                }
                merged_images.append(new_img)

                # Record mapping
                img_id_map[old_img_id] = next_image_id
                next_image_id += 1

            # Remap and append annotations for images that were successfully copied
            for ann in local_annotations:
                old_img_id = ann["image_id"]
                if old_img_id not in img_id_map:
                    # Image was missing or skipped; drop this annotation
                    continue
                new_ann = {
                    **ann,
                    "id": next_ann_id,
                    "image_id": img_id_map[old_img_id],
                    "category_id": remap_cat_id(ann["category_id"], local_categories),
                }
                merged_annotations.append(new_ann)
                next_ann_id += 1

        # Compose final COCO dict for this split
        merged_coco = {
            "info": info_block,
            "licenses": licenses_block,
            "images": merged_images,
            "annotations": merged_annotations,
            "categories": global_categories,
        }

        # Save `_annotations.coco.json` in the split folder
        out_ann_path = out_split_dir / "_annotations.coco.json"
        with out_ann_path.open("w", encoding="utf-8") as f:
            json.dump(merged_coco, f, indent=2)
        print(f"Saved {split} → {out_ann_path}  (images: {len(merged_images)}, anns: {len(merged_annotations)})")


if __name__ == "__main__":
    dataset_paths = [
        r"Buses", #1
        r"Cars", #2
        r"Trucks", #3
        r"Vans", #4
        r"Motorcycles" #5
    ]
    output_dir = r"data\vehicle_dataset"

    merge_coco_datasets(dataset_paths, output_dir)
