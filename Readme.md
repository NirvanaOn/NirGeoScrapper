# NirGeoScrapper 🌍🔎

**NirGeoScrapper** is a Python-based **OSINT and reconnaissance tool** designed to collect **publicly available business and geospatial intelligence** from map search results and export it into a **clean, structured, and analysis-ready Excel (.xlsx) dataset**.

The tool is built with a strong emphasis on **automation, data accuracy, resumability, and operational reliability**, making it suitable for **OSINT investigations, reconnaissance workflows, research, analytics, and educational use cases**.

---

## 🎯 Purpose

NirGeoScrapper automates the process of exploring map-based search results and extracting structured information about places such as businesses, hospitals, cafes, and other points of interest.

It is designed to behave in a **controlled and human-like manner**, ensuring stable execution while preventing duplicate entries and maintaining data consistency across long-running sessions.

---

## ✨ Key Features

- 🔍 Search places using natural-language queries (e.g., *Hospitals in Ahmedabad*)
- 📊 Export collected data directly into Excel (`.xlsx`)
- 🎯 Select specific data fields to collect
- 🔁 Resume scraping from existing Excel files without duplication
- 🤖 Automatic mode for continuous data collection
- 🐢 Slow, human-like mode for safer execution
- 📈 Crawl statistics including saved entries and execution time
- 🎨 Clean and readable terminal interface
- 🧠 Intelligent deduplication using place identity (Name + Address)

---

## 📂 Supported Data Fields

NirGeoScrapper supports extraction of the following fields:

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

The output schema adapts dynamically based on selected fields while preserving Excel compatibility.

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
```

---

## ⚙️ How It Works (High-Level)

1. Accepts a user-defined search query  
2. Opens map search results using browser automation  
3. Scrolls and explores results similar to a real user  
4. Extracts structured place information safely  
5. Normalizes and flattens complex data  
6. Writes clean rows into Excel  
7. Prevents duplicate entries automatically  
8. Supports resuming interrupted or partial runs  

This architecture ensures **scalability, reliability, and data integrity** during both small and large scraping operations.

---

## 🧪 Use Cases

- OSINT and reconnaissance research  
- Market and location-based analysis  
- Academic and educational projects  
- Dataset generation for analytics or ML preprocessing  
- Ethical competitive intelligence  

---

## ⚠️ Disclaimer

NirGeoScrapper collects **only publicly available information** from map search results.

This tool is intended strictly for:
- OSINT  
- Research  
- Educational purposes  
- Ethical reconnaissance  

The author **does not take responsibility** for misuse of this tool.  
Users are solely responsible for ensuring compliance with:

- Google Maps Terms of Service  
- Local, national, and international laws  
- Ethical data collection and usage practices  

⚠️ **Always use this tool responsibly and legally.**

---

## ⭐ Support & Contributions

If you find NirGeoScrapper useful:

- ⭐ Star the repository to support the project  
- 🐞 Report bugs or issues via GitHub Issues  
- 💡 Suggest features or improvements  
- 🤝 Contribute code via pull requests  

Every contribution helps improve the project 🚀
