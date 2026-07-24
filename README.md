# Plant Phase Manager

A desktop application for managing plant growth phases, tracking germination, and visualizing planting calendars.

## Features

- **Plant Catalog**: Create, edit, and delete plant entries with detailed growth phase information
- **Germination Tracking**: Track plants from germination through each growth phase
- **Calendar View**: Visualize plant timelines across months

## Requirements

- Python 3.10+
- pip (Python package manager)

## Setup

### 1. Clone or navigate to the project

```bash
cd plants
```

### 2. Environment variables (optional)

Copy or edit the `.env` file to configure environment-specific settings:

```
# Environment variables for the Plant Phase Manager
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `customtkinter` — Modern UI toolkit
- `python-dateutil` — Date arithmetic utilities
- `python-dotenv` — Environment variable loading

### 4. Run the application

```bash
python main.py
```

## Usage

1. **Catalog tab**: Add new plants, configure their growth phases (name, duration, light, water, temperature, humidity requirements)
2. **Seguimiento (Tracking) tab**: Register plants that have germinated and monitor their current phase
3. **Calendario (Calendar) tab**: View a timeline of all tracked plants across months

## Data

The application stores data in a local SQLite database (`plants.db`) created automatically in the project directory. You can also import/export plant data via JSON files.
