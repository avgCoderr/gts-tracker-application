# GPS Tracker Application (GTA)

A desktop GPS tracking application built with PyQt5. It allows you to create multiple projects with custom taxonomies, log GPS routes with metadata tagging, and view route logs.

* The future goals would be:
  * Provide a Map View of the Route - Either through GUI or Google Maps
* Start logging real-time GPS Coordinates


---

## Features

* Create and manage multiple **Projects**:

  * Define project name and GPS logging frequency (5–20 seconds).
  * Customize **Taxonomy**: classes with selectable attributes.
* **Route Logging**:

  * Start/stop logging sessions.
  * Select metadata tags for each class and submit them in batches.
  * Automatically logs GPS coordinates and associated metadata at configured intervals.
* **Persistent Storage**:

  * Projects stored as JSON in `app_data/projects/`.
  * Route logs stored as JSON Lines in `app_data/routes/`.
* **Log Viewing**:

  * Browse all route sessions per project.
  * Preview logs (first 50 entries) in a scrollable window.

---

## Getting Started

### Prerequisites

* **Python 3.8+**
* **PyQt5** library

Install PyQt5 via pip:

```bash
pip install PyQt5
```

### Directory Structure

```plaintext
gps_tracker_app/
├── main.py                # Entry point for the application
├── dialog.py              # Dialog classes for project and route management
├── app_data/
│   ├── projects/          # Saved project JSON files
│   └── routes/            # Generated route JSONL logs
├── README.md              # Project documentation (this file)
└── requirements.txt       # (Optional) list of dependencies
```

### Running Locally

1. **Clone the repository** or copy the code into a directory:

   ```bash
   git clone https://github.com/yourusername/new-repo-name.git
   cd new-repo-name
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   # Or directly:
   pip install PyQt5
   ```

3. **Launch the application**:

   ```bash
   python main.py
   ```

4. **Using the App**:

   * Click **Create New Project**.

     * Enter a unique project name.
     * Set GPS frequency (5–20 seconds).
     * Build taxonomy by adding classes and comma-separated attributes.
   * Select a project from the list to view details.

     * **Edit This Project** to modify frequency or taxonomy.
     * **Start Route Logging** to begin a new route session.

       * The logging dialog displays buttons for each class.
       * Click a class button, select an attribute, then click **Submit Meta** to tag metadata.
       * The app logs GPS and metadata every `X` seconds to `app_data/routes/route_<project>_<timestamp>.jsonl`.
       * Click **Stop Logging** to finish the session.
     * **Check Route Logs** to browse existing route sessions.

       * Click on a route file to preview the first 50 log entries.

---

## Data Formats

### Project File (`.json`)

```json
{
  "projectName": "My Project",
  "gpsFrequency": 10,
  "taxonomy": [
    { "className": "Weather", "attributes": ["Sunny", "Cloudy"] },
    { "className": "Traffic", "attributes": ["Light", "Heavy"] }
  ]
}
```

### Route Log File (`.jsonl`)

Each line is a JSON object:

```jsonl
{"tick_timestamp": 1626778560, "latitude": 28.6448, "longitude": 77.2167, "meta_data": {"Weather": "Rainy"}, "meta_submitted_at": 1626778555}
{"tick_timestamp": 1626778570, "latitude": 28.6449, "longitude": 77.2165, "meta_data": {}}
```

---

## Contributing

Feel free to open issues or submit pull requests for enhancements, bug fixes, or additional features.
