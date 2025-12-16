import json


def flatten_for_excel(place: dict, max_images: int = 20) -> dict:
    """
    Convert nested scraper data into Excel-safe flat columns.

    Rules:
    - Images -> Image 1, Image 2, ...
    - List of dicts -> readable multiline text
    - Dicts -> formatted JSON
    """

    flat = {}

    for key, value in place.items():

        # ================= IMAGES =================
        if key == "Images" and isinstance(value, list):
            for i in range(max_images):
                flat[f"Image {i + 1}"] = value[i] if i < len(value) else ""
            continue

        # ================= LIST =================
        if isinstance(value, list):

            # list of dicts (e.g. reviewers)
            if value and isinstance(value[0], dict):
                flat[key] = "\n".join(
                    ", ".join(f"{k}: {v}" for k, v in item.items())
                    for item in value
                )
            else:
                flat[key] = "\n".join(map(str, value))

            continue

        # ================= DICT =================
        if isinstance(value, dict):
            flat[key] = json.dumps(value, ensure_ascii=False, indent=2)
            continue

        # ================= SCALAR =================
        flat[key] = value

    return flat
