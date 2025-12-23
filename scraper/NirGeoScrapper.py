import argparse
import time
import sys
from google import scrape_google_maps, CONFIG
from excel import ExcelWriter
from utils import flatten_for_excel
from colorama import Fore, Style, init
init(autoreset=True)
import random
import shutil
import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text



BANNER_FONTS = [
    "banner3", "ansi_shadow", "univers", "nancyj", "big",
    "block", "epic", "doom", "slant", "smslant", "shadow",
    "speed", "lean", "standard", "bigfig", "chunky",
    "ogre", "rectangles"
]

console = Console()
VERSION = "1.0.0"

def color_text(text, color):
    return f"{color}{text}{Style.RESET_ALL}"


def print_banner():
    term_width = shutil.get_terminal_size((100, 20)).columns
    font = random.choice(BANNER_FONTS)

    ascii_logo = pyfiglet.figlet_format(
        "NirGeoScrapper",
        font=font,
        width=term_width
    )

    banner = Text()
    banner.append(ascii_logo, style="bold cyan")
    banner.append("\nLocation & Place Data Collection Tool\n", style="bold white")
    banner.append("Author: Nirvana | OSINT • Recon • Maps\n", style="yellow")
    banner.append(f"Version: {VERSION}\n", style="dim cyan")
    banner.append("Public data only • Use responsibly", style="dim")

    console.print(
        Panel(
            banner,
            border_style="bright_blue",
            padding=(1, 4),
            expand=False
        )
    )

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

    print_banner()

    parser = argparse.ArgumentParser(
        prog="NirGeoScrapper",
        description=(
            "NirGeoScrapper collects publicly available business and location data\n"
            "from map search results and exports them into a structured Excel file."
        ),
        epilog=(
            "Examples:\n"
            "  python NirGeoScrapper.py -s \"Cafe in Surat\"\n"
            "  python NirGeoScrapper.py -s \"Hospital in Ahmedabad\" --total 50\n"
            "  python NirGeoScrapper.py -s \"Restaurant in Mumbai\" --auto --slow\n"
            "  python NirGeoScrapper.py --list-fields\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    action_group = parser.add_mutually_exclusive_group(required=True)

    action_group.add_argument(
        "-s", "--search",
        help=(
            "Search query used to find places on the map.\n"
            "Example: \"Cafe in Surat\", \"Hospitals in Ahmedabad\""
        )
    )

    action_group.add_argument(
        "--list-fields",
        action="store_true",
        help=(
            "List all available data fields supported by the tool and exit.\n"
            "This option can be used without --search."
        )
    )

    basic_opts = parser.add_argument_group("Basic options")

    basic_opts.add_argument(
        "-t", "--total",
        type=int,
        default=None,
        help=(
            "Maximum number of UNIQUE places to save.\n"
            "If not set, scraping continues until results end or tool is stopped."
        )
    )

    basic_opts.add_argument(
        "--skip",
        type=int,
        default=0,
        help=(
            "Skip the first N UNIQUE places before saving.\n"
            "Useful when continuing or dividing large searches."
        )
    )

    basic_opts.add_argument(
        "--fields",
        help=(
            "Select specific fields to save (comma-separated).\n"
            "Example: Name,Rating,Phone,Website"
        )
    )

    advanced_opts = parser.add_argument_group("Advanced options")

    advanced_opts.add_argument(
        "--auto",
        action="store_true",
        help=(
            "Enable automatic mode.\n"
            "Runs continuously until Ctrl+C is pressed (ignores --total)."
        )
    )

    advanced_opts.add_argument(
        "--resume",
        action="store_true",
        help=(
            "Resume scraping from an existing Excel file.\n"
            "Automatically continues from the last saved place."
        )
    )

    advanced_opts.add_argument(
        "--stats",
        action="store_true",
        help=(
            "Display crawl statistics after completion.\n"
            "Shows total saved places and execution time."
        )
    )

    advanced_opts.add_argument(
        "--slow",
        action="store_true",
        help=(
            "Enable slow, human-like scraping speed.\n"
            "Recommended for long runs and safer execution."
        )
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)


    args = parser.parse_args()

    if args.list_fields:
        print("\nAvailable Fields:")
        for field in ALL_FIELDS:
            print(" -", field)
        return

    if args.search.startswith("-"):
        parser.error("Invalid value for --search. Search query cannot be a flag.")

    if args.fields:
        selected_fields = [
            f.strip() for f in args.fields.split(",")
            if f.strip() in ALL_FIELDS
        ]
        if not selected_fields:
            print("[!] No valid fields selected.")
            print("[!] Use --list-fields to see available fields.")
            return
    else:
        selected_fields = ALL_FIELDS

    if args.auto and args.total is not None:
        print("[!] Info: --auto ignores --total. Running in AUTO mode.")
        args.total = None

    if args.skip < 0:
        parser.error("--skip cannot be negative")

    if args.total is not None and args.total <= 0:
        parser.error("--total must be greater than zero")

    stats = {
        "fetched": 0,
        "saved": 0,
        "skipped": 0,
        "failed": 0,
        "start_time": time.time(),
    }

    writer = ExcelWriter(args.search)

    if args.resume:
        try:
            existing_rows = writer.get_row_count()
            stats["skipped"] = existing_rows

            if args.skip > 0:
                print("[!] Info: --resume overrides --skip.")

            args.skip = max(args.skip, existing_rows)
        except (FileNotFoundError, IOError):
            pass


    if args.slow:
        CONFIG["DELAY_MIN"] = 3.0
        CONFIG["DELAY_MAX"] = 6.0

    print("\n====== Configuration  ======")
    print(f"[+] Search      : {args.search}")
    print(f"[+] Mode        : {'AUTO' if args.auto else 'BATCH'}")
    print(f"[+] Max places  : {args.total}")
    print(f"[+] Skip        : {args.skip}")
    print(f"[+] Delay range : {CONFIG['DELAY_MIN']}–{CONFIG['DELAY_MAX']} sec")
    print(f"[+] Fields      : {', '.join(selected_fields)}")
    print("===========================\n")


    try:
        for place in scrape_google_maps(
            search_query=args.search,
            max_places=args.total,
            skip=args.skip,
            automode=args.auto
        ):
            stats["fetched"] += 1

            filtered_place = {
                k: v for k, v in place.items()
                if k in selected_fields
            }

            flat = flatten_for_excel(filtered_place)

            if writer.write_row(flat):
                stats["saved"] += 1
                print("Saved:", place.get("Name", "N/A"))
            else:
                stats["failed"] += 1
    except KeyboardInterrupt:
        print("\n[!] Stopped by user. Excel file is SAFE.")


    if args.stats:
        duration = int(time.time() - stats["start_time"])
        rate = (stats["saved"] / duration * 60) if duration > 0 else 0

        print("\n--- Crawl Stats ---")
        print("Fetched  :", stats["fetched"])
        print("Saved    :", stats["saved"])
        print("Skipped  :", stats["skipped"])
        print("Failed   :", stats["failed"])
        print("Duration :", f"{duration}s")
        print("Rate     :", f"{rate:.2f} places/min")


if __name__ == "__main__":
    main()