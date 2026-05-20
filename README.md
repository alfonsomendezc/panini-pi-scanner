# 🏆 Panini Pi Scanner

A Python + SQLite project designed to track, manage, and eventually scan a FIFA World Cup Panini sticker album using computer vision and Raspberry Pi hardware.

## 📌 Project Goal

The goal of this project is to build a smart Panini sticker album tracker that can:

- Store all official sticker data in a structured SQLite database
- Track owned, missing, and duplicate stickers
- Organize stickers by team and World Cup group
- Eventually use a Raspberry Pi camera to scan sticker codes
- Later support album-page scanning to detect completed and missing slots

## 🚧 Current Project Stage

This project is currently in the **database foundation phase**.

Current features being built:

- SQLite database connection
- Table creation for groups, teams, stickers, and collection
- CSV import for official sticker data
- Normalized database relationships
- Group and team imports from CSV

Future features:

- Manual sticker entry
- Duplicate tracking
- Missing sticker reports
- OCR sticker scanning
- Raspberry Pi camera integration
- Album page detection
- Player/team information dashboard

## 🧱 Tech Stack

| Tool | Purpose |
|---|---|
| Python | Main programming language |
| SQLite | Local database |
| CSV | Raw sticker data source |
| VS Code | Development environment |
| Git/GitHub | Version control |
| Raspberry Pi | Future hardware platform |
| OpenCV | Future image processing |
| Tesseract OCR | Future sticker code recognition |

## 🗂️ Project Structure

```text
Panini Project/
│
├── data/
│   ├── stickers.csv
│   └── panini.db
│
├── docs/
│   └── database_design.md
│
├── src/
│   ├── database.py
│   ├── import_data.py
│   └── test_database.py
│
├── test_images/
│   ├── album_pages/
│   └── stickers/
│
├── README.md
└── .gitignore