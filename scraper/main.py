import argparse
import time

from google import scrape_google_maps, CONFIG
from excel import ExcelWriter
from utils import flatten_for_excel


# ================= AVAILABLE FIELDS =================

ALL_FIELDS = [
    "Name",
    "Category",
    "Rating",
    "Reviews Count",
    "Address",
    "Plus Code",
    "Located In",
    "Phone",
    "Website",
    "Open Status",
    "Latitude",
    "Longitude",
    "Maps URL",
    "Images",
    "Star Breakdown",
    "Reviewers",
]


def main():
    # ==================================================
    # CLI ARGUMENTS
    # ==================================================
    parser = argparse.ArgumentParser(
        description="Google Maps Crawler (Linux-style CLI)"
    )

    parser.add_argument(
        "-s", "--search",
        help="Search query (e.g. 'Cafe in Surat')"
    )

    parser.add_argument(
        "-t", "--total",
        type=int,
        default=None,
        help="Max number of UNIQUE places to SAVE"
    )

    parser.add_argument(
        "--skip",
        type=int,
        default=0,
        help="Skip first N UNIQUE places"
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automode: run until Ctrl+C (ignores --total)"
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume automatically from existing Excel"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show crawl statistics at the end"
    )

    parser.add_argument(
        "--fields",
        help=(
            "Comma-separated fields to save. "
            "Example: Name,Rating,Phone,Website"
        )
    )

    parser.add_argument(
        "--list-fields",
        action="store_true",
        help="List all available fields and exit"
    )

    parser.add_argument(
        "--slow",
        action="store_true",
        help="Slow down scraping speed (safer, human-like)"
    )

    args = parser.parse_args()

    # --list-fields can run without --search
    if not args.list_fields and not args.search:
        parser.error("the following arguments are required: -s/--search")

    # ==================================================
    # FIELD HANDLING
    # ==================================================
    if args.list_fields:
        print("\nAvailable Fields:")
        for f in ALL_FIELDS:
            print(" -", f)
        return

    if args.fields:
        selected_fields = [
            f.strip() for f in args.fields.split(",")
            if f.strip() in ALL_FIELDS
        ]

        if not selected_fields:
            print("[!] No valid fields selected.")
            print("[!] Use --list-fields to see available options.")
            return
    else:
        selected_fields = ALL_FIELDS

    # ==================================================
    # OPTION NORMALIZATION
    # ==================================================
    if args.auto:
        args.total = None

    # ==================================================
    # WRITER + RESUME
    # ==================================================
    writer = ExcelWriter(args.search)

    if args.resume:
        try:
            existing_rows = writer.get_row_count()
            args.skip = max(args.skip, existing_rows)
        except Exception:
            pass

    # ================= SPEED CONTROL =================
    if args.slow:
        CONFIG["DELAY_MIN"] = 3.0
        CONFIG["DELAY_MAX"] = 6.0

    # ==================================================
    # FINAL CONFIG OUTPUT
    # ==================================================
    print("\n=== Google Maps Crawler ===")
    print(f"[+] Search      : {args.search}")
    print(f"[+] Mode        : {'AUTO' if args.auto else 'BATCH'}")
    print(f"[+] Max places  : {args.total}")
    print(f"[+] Skip        : {args.skip}")
    print(f"[+] Delay range : {CONFIG['DELAY_MIN']}–{CONFIG['DELAY_MAX']} sec")
    print(f"[+] Fields      : {', '.join(selected_fields)}")
    print("===========================\n")

    # ==================================================
    # STATS
    # ==================================================
    stats = {
        "saved": 0,
        "start_time": time.time(),
    }

    # ==================================================
    # SCRAPE LOOP
    # ==================================================
    try:
        for place in scrape_google_maps(
            search_query=args.search,
            max_places=args.total,
            skip=args.skip,
            automode=args.auto
        ):
            filtered_place = {
                k: v for k, v in place.items()
                if k in selected_fields
            }

            flat = flatten_for_excel(filtered_place)

            if writer.write_row(flat):
                stats["saved"] += 1
                print("Saved:", place.get("Name", "N/A"))

    except KeyboardInterrupt:
        print("\n[!] Stopped by user. Excel file is SAFE.")

    # ==================================================
    # FINAL STATS
    # ==================================================
    if args.stats:
        duration = int(time.time() - stats["start_time"])
        print("\n--- Crawl Stats ---")
        print("Saved    :", stats["saved"])
        print("Duration :", f"{duration}s")


if __name__ == "__main__":
    main()
