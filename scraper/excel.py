import os
import re
from openpyxl import Workbook, load_workbook


# ================= HELPERS =================

def sanitize_name(name: str) -> str:
    """
    Make search string safe for filenames
    """
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name


# ================= EXCEL WRITER =================

class ExcelWriter:

    def __init__(self, search_query: str, base_folder: str = "data"):

        # 1️⃣ Ensure folder exists
        os.makedirs(base_folder, exist_ok=True)

        # 2️⃣ Stable filename (IMPORTANT for resume)
        safe_query = sanitize_name(search_query)
        self.path = os.path.join(base_folder, f"{safe_query}.xlsx")

        # 3️⃣ Load or create workbook
        if os.path.exists(self.path):
            self.wb = load_workbook(self.path)
            self.ws = self.wb.active

            # Safe header load
            if self.ws.max_row >= 1:
                self.headers = [cell.value for cell in self.ws[1] if cell.value]
            else:
                self.headers = []

            self._load_existing_urls()
        else:
            self.wb = Workbook()
            self.ws = self.wb.active
            self.ws.title = "Places"
            self.headers = []
            self.seen_urls = set()
            self.wb.save(self.path)

    # ================= INTERNAL =================

    def _load_existing_urls(self):
        """
        Load existing Maps URLs to prevent duplicates on resume.
        """
        self.seen_urls = set()

        if not self.headers:
            return

        if "Maps URL" not in self.headers:
            return

        url_col = self.headers.index("Maps URL") + 1

        for row in self.ws.iter_rows(min_row=2, values_only=True):
            url = row[url_col - 1]
            if url:
                self.seen_urls.add(url)

    def _sync_headers(self, data: dict):
        """
        Expand headers dynamically if new keys appear.
        """
        new_cols = [k for k in data.keys() if k not in self.headers]

        if new_cols:
            self.headers.extend(new_cols)

            # Rewrite header row
            self.ws.delete_rows(1)
            self.ws.insert_rows(1)
            self.ws.append(self.headers)

    # ================= PUBLIC METHODS =================

    def write_row(self, data: dict) -> bool:

        maps_url = data.get("Maps URL")

        # 🔥 DUPLICATE PROTECTION
        if maps_url and maps_url in self.seen_urls:
            return False

        # Initialize headers on first write
        if not self.headers:
            self.headers = list(data.keys())
            self.ws.append(self.headers)
        else:
            self._sync_headers(data)

        # Align row with headers
        row = [data.get(h, "") for h in self.headers]
        self.ws.append(row)

        if maps_url:
            self.seen_urls.add(maps_url)

        # 🔥 CRASH SAFE SAVE
        self.wb.save(self.path)
        return True

    def get_row_count(self) -> int:
        if self.ws.max_row <= 1:
            return 0
        return self.ws.max_row - 1
