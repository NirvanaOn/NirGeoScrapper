import argparse
import time
import sys
from google import scrape_google_maps, CONFIG
from excel import ExcelWriter
from utils import flatten_for_excel
import random
import shutil
import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn
)

THEME = {
    "primary": "cyan",
    "secondary": "bright_blue",
    "success": "green",
    "error": "red",
    "warning": "yellow",
    "muted": "dim",
    "title": "bold cyan",
    "panel": "bright_blue"
}



BANNER_FONTS = [
    "banner3", "ansi_shadow", "univers", "nancyj", "big",
    "block", "epic", "doom", "slant", "smslant", "shadow",
    "speed", "lean", "standard", "bigfig", "chunky",
    "ogre", "rectangles"
]

console = Console()
VERSION = "1.0.0"



def print_banner():
    term_width = shutil.get_terminal_size((100, 20)).columns
    font = random.choice(BANNER_FONTS)

    ascii_logo = pyfiglet.figlet_format(
        "NirGeoScrapper",
        font=font,
        width=term_width
    )

    banner = Text()
    banner.append(ascii_logo, style=THEME["title"])
    banner.append("\nLocation & Place Data Collection Tool\n", style="bold white")
    banner.append("Author: Nirvana | OSINT • Recon • Maps\n", style="bold yellow")
    banner.append(f"Version: {VERSION}\n", style=THEME["muted"])
    banner.append("Public data only • Use responsibly", style=THEME["muted"])

    console.print(
        Panel(
            banner,
            border_style=THEME["panel"],
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

def colorize_help(text: str) -> Text:
    styled = Text()

    for line in text.splitlines():
        line_strip = line.strip()

        if line_strip.startswith("-"):
            styled.append(line + "\n", style="bold cyan")
        elif line_strip.lower().startswith("usage"):
            styled.append(line + "\n", style="bold green")
        elif line_strip.endswith(":"):
            styled.append(line + "\n", style="bold yellow")
        elif "Example" in line or "Examples" in line:
            styled.append(line + "\n", style="bold magenta")
        else:
            styled.append(line + "\n", style="white")

    return styled


def main():

    print_banner()

    parser = argparse.ArgumentParser(
        prog="NirGeoScrapper",
        add_help=False,
        description=(
            "NirGeoScrapper collects publicly available business and location data\n"
            "from map search results and exports them into a structured Excel file."
        ),
        epilog=(
            "Examples:\n"
            "  python NirGeoScrapper.py -s \"Cafe in XXXX\"\n"
            "  python NirGeoScrapper.py -s \"Hospital in XXXXXXX\" --total 50\n"
            "  python NirGeoScrapper.py -s \"Restaurant in XXXXXX\" --auto --slow\n"
            "  python NirGeoScrapper.py --list-fields\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help="Show this help message and exit"
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

    if len(sys.argv) == 1 or any(a in sys.argv for a in ("-h", "--help")):
        help_text = parser.format_help()
        blocks = help_text.split("\n\n")

        console.print(Panel(
            colorize_help(blocks[0]),
            title="|| NirGeoScrapper ||",
            border_style=THEME["panel"]
        ))

        for block in blocks[1:]:
            title = "Help"
            style = THEME["secondary"]

            if "Basic options:" in block:
                title = "@ Basic Options @"
            elif "Advanced options:" in block:
                title = "# Advanced Options #"
            elif "options:" in block.lower():
                title = "$ Options $"
            elif "Examples:" in block:
                title = "* Examples *"
                style = "green"

            console.print(
                Panel(
                    colorize_help(block),
                    title=title,
                    border_style=style
                )
            )

        sys.exit(0)

    args = parser.parse_args()

    if args.list_fields:
        fields_text = Text()
        for f in ALL_FIELDS:
            fields_text.append(f"• {f}\n", style="cyan")

        console.print(
            Panel(
                fields_text,
                title="{ Available Fields }",
                border_style="bright_blue"
            )
        )
        return

    if args.search.startswith("-"):
        console.print(
            Panel(
                "[bold red]Invalid value for --search[/]\n\n"
                "[white]Search query cannot start with a flag ( - ).[/]\n"
                "[dim]Example:[/] -s \"Cafe in xxxxx\"",
                title="Error",
                border_style="red"
            )
        )
        sys.exit(1)

    if args.fields:
        field_map = {f.lower(): f for f in ALL_FIELDS}

        selected_fields = []
        for raw in args.fields.split(","):
            key = raw.strip().lower()
            if key in field_map:
                selected_fields.append(field_map[key])

        if not selected_fields:
            console.print("[bold red][!] No valid fields selected.[/]")
            console.print("[yellow][!] Use --list-fields to see valid field names.[/]")
            return
    else:
        selected_fields = ALL_FIELDS


    required_fields = {"Name", "Address"}

    if args.fields:
        missing = required_fields - set(selected_fields)
        if missing:
            console.print(
                "[bold red][!] Invalid --fields selection[/]\n"
                "[yellow]Deduplication requires BOTH 'Name' and 'Address'.[/]\n"
                f"[cyan]Missing fields:[/] {', '.join(missing)}\n\n"
                "[green]Fix:[/] Add them to --fields\n"
                "[dim]Example:[/] --fields Name,Address,Rating,Phone"
            )
            sys.exit(1)

    if "Images" in selected_fields:
        console.print(
            "[yellow][!] Note:[/] 'Images' expands into Image 1, Image 2, ... columns."
        )

    if args.auto and args.total is not None:
        console.print(
            "[bold yellow][!][/bold yellow] "
            "[cyan]Info:[/] "
            "[white]--auto ignores --total. Running in AUTO mode.[/]"
        )
        args.total = None

    if args.skip < 0:
        console.print(
            "[bold red][✖][/bold red] "
            "[white]--skip cannot be negative.[/]"
        )
        sys.exit(1)

    if args.total is not None and args.total <= 0:
        console.print(
            "[bold red][✖][/bold red] "
            "[white]--total must be greater than zero.[/]"
        )
        sys.exit(1)

    stats = {
        "fetched": 0,
        "saved": 0,
        "skipped": 0,
        "failed": 0,
        "duplicates": 0,
        "start_time": time.time(),
    }

    writer = ExcelWriter(args.search)


    if args.resume and writer.headers:
        selected_fields = [f for f in selected_fields if f in writer.headers]

        if not selected_fields:
            console.print(
                "[bold red][!] Resume failed[/]\n"
                "[yellow]None of the selected fields exist in the existing Excel file.[/]\n"
                "[dim]Use --list-fields or remove --resume[/]"
            )
            sys.exit(1)

    if args.resume:
        try:
            existing_rows = writer.get_row_count()
            stats["skipped"] = existing_rows

            if args.skip > 0:
                console.print(
                    "[bold yellow][!][/bold yellow] "
                    "[cyan]Info:[/] "
                    "[white]--resume overrides --skip.[/]"
                )

            args.skip = max(args.skip, existing_rows)
        except (FileNotFoundError, IOError):
            pass


    if args.slow:
        CONFIG["DELAY_MIN"] = 3.0
        CONFIG["DELAY_MAX"] = 6.0

    config = Text()
    config.append("Search      : ", style=THEME["secondary"])
    config.append(f"{args.search}\n", style="white")

    config.append("Mode        : ", style=THEME["secondary"])
    config.append(f"{'AUTO' if args.auto else 'BATCH'}\n", style="white")

    config.append("Max places  : ", style=THEME["secondary"])
    config.append(f"{args.total}\n", style="white")

    config.append("Skip        : ", style=THEME["secondary"])
    config.append(f"{args.skip}\n", style="white")

    config.append("Delay range : ", style=THEME["secondary"])
    config.append(f"{CONFIG['DELAY_MIN']}–{CONFIG['DELAY_MAX']} sec\n", style="white")

    config.append("Fields      : ", style=THEME["secondary"])
    config.append(", ".join(selected_fields), style="white")

    console.print(
        Panel(
            config,
            title="Configuration",
            border_style=THEME["panel"]
        )
    )

    try:
        with Progress(
                SpinnerColumn(style=THEME["primary"]),
                TextColumn(f"[{THEME['secondary']}]{{task.description}}"),
                BarColumn(
                    bar_width=40,
                    complete_style=THEME["success"],
                    finished_style=THEME["success"]
                ),
                TextColumn(f"[{THEME['success']}]{{task.completed}} saved"),
                TextColumn(f"[{THEME['warning']}]{{task.fields[duplicates]}} dup"),
                TimeElapsedColumn(),
                console=console
        ) as progress:

            task = progress.add_task(
                "Scraping places...",
                total=args.total if args.total else None,
                failed=0,
                duplicates=0
            )

            for place in scrape_google_maps(
                    search_query=args.search,
                    max_places=args.total,
                    skip=args.skip,
                    automode=args.auto
            ):
                stats["fetched"] += 1

                flat_data = flatten_for_excel(place)
                filtered_output = {
                    k: v for k, v in flat_data.items()
                    if k in selected_fields or k in ("Name", "Address", "Maps URL")
                }

                if writer.write_row(filtered_output):
                    stats["saved"] += 1
                    progress.update(
                        task,
                        advance=1,
                        description=f"[{THEME['success']}]✔[/] {place.get('Name', 'N/A')}"
                    )

                else:
                    stats["duplicates"] += 1

                    progress.update(
                        task,
                        duplicates=stats["duplicates"],
                        description=f"[{THEME['warning']}]↺ Duplicate[/] {place.get('Name', 'N/A')}"
                    )


    except KeyboardInterrupt:
        console.print("\n[bold yellow][!] Stopped by user. Excel file is SAFE.[/]")

    if args.stats:
        duration = int(time.time() - stats["start_time"])
        rate = (stats["saved"] / duration * 60) if duration > 0 else 0

        if args.auto:
            console.print(
                "[yellow][!] AUTO mode stats reflect only the current session.[/]"
            )

        summary = Text()
        summary.append(f"Fetched : {stats['fetched']}\n", style=THEME["secondary"])
        summary.append(f"Saved   : {stats['saved']}\n", style=THEME["success"])
        summary.append(f"Skipped : {stats['skipped']}\n", style=THEME["warning"])
        summary.append(f"Duplicates: {stats['duplicates']}\n", style=THEME["warning"])
        summary.append(f"Duration: {duration}s\n", style="white")
        summary.append(f"Rate    : {rate:.2f} places/min", style=THEME["primary"])

        console.print(
            Panel(
                summary,
                title="Crawl Summary",
                border_style=THEME["panel"]
            )
        )


if __name__ == "__main__":
    main()