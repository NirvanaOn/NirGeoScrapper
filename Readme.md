# NirGeoScrapper 🌍🔎

**NirGeoScrapper** is a Python-based OSINT and reconnaissance tool designed to collect **publicly available business and location data** from map search results and export them into a **structured Excel file**.

It is built to be **simple, clean, and reliable**, with a strong focus on automation, data accuracy, and usability for OSINT, recon, and research purposes.

---

## ✨ Features

- 🔍 Search places by keyword (e.g., *Hospitals in Ahmedabad*)
- 📄 Export results directly to Excel (`.xlsx`)
- 🎯 Select specific fields to save
- 🔁 Resume scraping from existing files
- 🤖 Automatic (continuous) mode
- 🐢 Slow / human-like scraping mode
- 📊 Crawl statistics after execution
- 🎨 Clean banner UI for better CLI experience

---

## 📂 Data Fields Supported

- Name  
- Category  
- Rating  
- Reviews Count  
- Address  
- Plus Code  
- Located In  
- Phone  
- Website  
- Open Status  
- Latitude  
- Longitude  
- Maps URL  
- Images  
- Star Breakdown  
- Reviewers  

---

## 🚀 Usage

```bash
# Basic search
python NirGeoScrapper.py -s "Cafe in xxx"

# Limit number of results
python NirGeoScrapper.py -s "Hospital in xxxxx" --total 50

# Automatic mode (run until stopped)
python NirGeoScrapper.py -s "Restaurant in xxxxx" --auto

# Slow & human-like mode
python NirGeoScrapper.py -s "Clinics in xxxxxx" --slow

# Select specific fields
python NirGeoScrapper.py -s "Gyms in xxxxxxx" --fields Name,Rating,Phone,Website

# Resume previous scrape
python NirGeoScrapper.py -s "Hospitals in xxxxxx" --resume

# List all available fields
python NirGeoScrapper.py --list-fields


---

## ⚠️ Disclaimer

NirGeoScrapper collects **publicly available information only** from map search results.  
This tool is intended for **OSINT, research, educational, and reconnaissance purposes**.

The author is **not responsible** for any misuse of this tool.  
Users are solely responsible for ensuring compliance with:
- Google Maps Terms of Service
- Local, national, and international laws
- Ethical data usage practices

Use this tool **responsibly and legally**.

---

## ⭐ Support & Contribution

If you find NirGeoScrapper useful:

- ⭐ Star the repository on GitHub
- 🐞 Report bugs or issues via GitHub Issues
- 💡 Suggest features or improvements
- 🤝 Contribute code via pull requests

Every contribution helps improve the project 🚀
