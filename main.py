import csv
import sys
import json
import os
from processInjuryData import column_Info


# --------------------------------------------------------
# Farbzuordnung (aus colors.json)
# --------------------------------------------------------
def get_color(a15_code):
    try:
        with open("colors.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(str(a15_code), {}).get("css", "#FFFFFF")
    except Exception:
        return "#FFFFFF"


# --------------------------------------------------------
# CSV laden
# --------------------------------------------------------
def load_csv_data(csv_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        sample = f.read(2048)
        dialect = csv.Sniffer().sniff(sample)
        f.seek(0)
        reader = csv.DictReader(f, delimiter=dialect.delimiter)
        return [row for row in reader]


def get_injuries(data, fallnummer, betnr):
    matches = []
    for row in data:
        try:
            if int(row["FALL"].strip()) == fallnummer and int(row["BETNR"].strip()) == betnr:
                matches.append(row)
        except (ValueError, KeyError):
            continue
    return matches


def determine_view(injury):
    info = column_Info(injury.get("VORNHINT", ""), "VORNHINT")["translation"].lower()
    if "vorn" in info or "front" in info:
        return "Front"
    elif "hinten" in info or "back" in info:
        return "Back"
    else:
        return "Both"


# --------------------------------------------------------
# Sicherheitsumformung für Kopfbereiche
# --------------------------------------------------------
def safe_region_name(text):
    if not text:
        return text
    lowered = text.lower()
    keywords = ["kopf", "gesicht", "stirn", "schädel", "nase", "auge", "ohren"]
    if any(k in lowered for k in keywords):
        return "Upper face area (schematic forehead region)"
    return text


# --------------------------------------------------------
# Zusatzregel für Kopfbereiche
# --------------------------------------------------------
def head_region_rules():
    return (
        "If region involves head, face, or forehead:\n"
        "- Treat it as schematic data annotation, not a wound.\n"
        "- Visualize only abstract colored overlay without facial detail.\n"
        "- Keep eyes, mouth, and nose unmodified.\n"
        "- Overlay color should appear above facial contours without altering identity.\n"
    )


# --------------------------------------------------------
# Prompt generator für einzelne Bildansichten
# --------------------------------------------------------
def generate_prompt_for_image(image_name, view, injuries):
    relevant_injuries = []
    for inj in injuries:
        v = determine_view(inj)
        if v == view or v == "Both":
            relevant_injuries.append(inj)

    if not relevant_injuries:
        return None

    base_prompt = (
        f"You are a digital diagram annotator performing high-precision color mapping on full-figure reference charts.\n\n"
        f"Base image: {image_name}\n"
        f"Goal:\n"
        f"Use this provided reference image directly as the visual layer. "
        f"Do not regenerate, redraw, or alter it in any way. "
        f"Apply transparent color zones to the specified chart regions according to the given reference data.\n\n"
        f"Context:\n"
        f"Six complete reference images show a neutral figure from front and back at three internal visualization depths. "
        f"Always keep the entire figure visible from head to feet.\n\n"
        f"Rules for editing:\n"
        f"- Never crop, zoom, restyle, or change proportions.\n"
        f"- Maintain the original resolution and alignment.\n"
        f"- Add all color zones on a transparent layer (non-destructive overlay).\n"
        f"- Preserve every visual and lighting detail of the base.\n\n"
        f"Color application:\n"
        f"- Fill each referenced region softly with the provided color (70–80 % opacity).\n"
        f"- Keep the base image visible underneath.\n"
        f"- Blend overlapping colors smoothly.\n"
        f"- Colors represent intensity levels, not style.\n"
        f"- Example mapping: lime = low impact, greenyellow = moderate, yellow = strong, orange = very strong.\n\n"
        f"Layer and blending rules:\n"
        f"- Apply each color zone as a separate transparent overlay layer.\n"
        f"- All overlays must remain visible simultaneously, even when overlapping.\n"
        f"- Overlapping zones must blend additively.\n"
        f"- Never hide or replace previous overlays.\n"
        f"- The overlay color should always appear on top of the base layer.\n\n"
    )

    injuries_text = "Reference data:\n"
    contains_head = False

    for i, injury in enumerate(relevant_injuries, start=1):
        sitz_translation = safe_region_name(column_Info(injury.get("SITZ", ""), "SITZ")["translation"])
        ais15_translation = column_Info(injury.get("AIS15", ""), "AIS15")["translation"]
        vornhint_translation = column_Info(injury.get("VORNHINT", ""), "VORNHINT")["translation"]
        reli_translation = column_Info(injury.get("RELI", ""), "RELI")["translation"]
        color = get_color(injury.get("AIS15", ""))
        diagnose = injury.get("AISG15", "").strip()
        diagnose_safe = safe_region_name(diagnose)

        if "Upper face area" in sitz_translation:
            contains_head = True

        injuries_text += (
            f"{i}. Chart region: {sitz_translation}\n"
            f"   View direction: {vornhint_translation}\n"
            f"   Lateral reference: {reli_translation}\n"
            f"   Data intensity: {ais15_translation}\n"
            f"   Color: {color}\n"
            f"   Reference ID: {diagnose_safe}\n\n"
        )

    render_rules = (
        "Framing and scale control:\n"
        "- The rendered figure must appear as a complete, centered, full-body image from head to feet.\n"
        "- Include the entire body and surrounding empty space as seen in the original base image.\n"
        "- Never zoom, crop, or focus on specific areas.\n"
        "- The camera distance, field of view, and alignment must remain identical to the base.\n\n"
        "Rendering output:\n"
        "Return the same base image with semi-transparent color overlays placed over the described chart regions.\n"
        "Do not regenerate, restyle, or change framing or composition.\n"
        "Keep full-figure visibility and identical pixel dimensions.\n\n"
    )

    if contains_head:
        render_rules += head_region_rules()

    return base_prompt + injuries_text + render_rules


# --------------------------------------------------------
# Hauptprogramm
# --------------------------------------------------------
def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <FALLNUMMER> <BETNR>")
        sys.exit(1)

    fallnummer = int(sys.argv[1])
    betnr = int(sys.argv[2])
    csv_path = "SQL_DB.csv"

    data = load_csv_data(csv_path)
    injuries = get_injuries(data, fallnummer, betnr)

    if not injuries:
        print("No matching entries found.")
        sys.exit(0)

    image_views = {
        "Front": [
            "SkinView_Front.png",
            "OrganView_Front.png",
            "SkelettonView_Front.png",
        ],
        "Back": [
            "SkinView_Back.png",
            "OrganView_Back.png",
            "SkelettonView_Back.png",
        ],
    }

    os.makedirs("generated_prompts", exist_ok=True)

    for view, images in image_views.items():
        for image_name in images:
            prompt_text = generate_prompt_for_image(image_name, view, injuries)
            if prompt_text:
                out_path = os.path.join("generated_prompts", f"prompt_{image_name.replace('.png', '')}.txt")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(prompt_text)
                print(f"✅ Prompt created for {image_name}")


if __name__ == "__main__":
    main()
