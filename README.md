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
   <img width="1198" height="831" alt="image" src="https://github.com/user-attachments/assets/b2d9b897-4ca7-410a-b853-7ce1f7b73083" />

3. **Seguimiento (Tracking) tab**: Register plants that have germinated and monitor their current phase
  <img width="1184" height="271" alt="image" src="https://github.com/user-attachments/assets/00af576d-24ca-4cd4-9a39-cd82f33241fe" />

4. **Calendario (Calendar) tab**: View a timeline of all tracked plants across months
<img width="901" height="339" alt="image" src="https://github.com/user-attachments/assets/1f8faaca-894f-4fea-9402-f4ffbd4a13c3" />


## Data

The application stores data in a local SQLite database (`plants.db`) created automatically in the project directory. You can also import/export plant data via JSON files.
