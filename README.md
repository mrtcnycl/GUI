# Drone Control GUI Application

A Python-based graphical user interface for drone control with interactive map functionality.

## Features

### Core Features
- ✅ **5 Control Buttons**:
  - **Takeoff** - Initiates drone launch sequence (Green)
  - **Land** - Commands drone to land at current position (Blue)
  - **Add Waypoint** - Toggles waypoint marking mode on map (Purple)
  - **Start Mission** - Begins executing planned mission (Orange)
  - **Emergency Stop** - Immediately halts all operations (Red)

- ✅ **Console Logging** - All button presses send notifications to both GUI log panel and terminal
- ✅ **Interactive Map** - OpenStreetMap integration with:
  - Click to select locations
  - Add waypoint markers
  - Remove markers (right-click context menu)
  - GPS coordinate display
  - Visual mission path representation

- ✅ **Coordinate Display** - Real-time GPS coordinates panel
- ✅ **Activity Log** - Easy-to-read log panel with timestamps and color-coded events

### Bonus Features
- ✅ **Save Mission Plans** - Export missions to JSON files
- ✅ **Clear All Waypoints** - One-click waypoint clearing
- ✅ **Distance Calculation** - Automatic total mission distance calculation
- ✅ **Mission Statistics** - Waypoint count and distance display

## Installation

### Prerequisites
- Python 3.7 or higher

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application
```bash
python drone_control_gui.py
```

### How to Use

1. **Add Waypoints**:
   - Click the "Add Waypoint" button (purple) to activate waypoint mode
   - Click anywhere on the map to place waypoints
   - Click "Add Waypoint" again to exit waypoint mode

2. **Remove Waypoints**:
   - Right-click near a waypoint on the map
   - Select "Remove Waypoint" from the context menu
   - Or use "Clear All Waypoints" button to remove all at once

3. **Control Drone**:
   - **Takeoff**: Launch the drone
   - **Land**: Land at current position
   - **Start Mission**: Execute the planned waypoint mission
   - **Emergency Stop**: Immediately halt all operations

4. **Save Mission**:
   - Click "Save Mission" to export your waypoint plan to a JSON file
   - Files are saved with timestamp: `mission_YYYYMMDD_HHMMSS.json`

### Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│  Drone Control System                                   │
├──────────────────┬──────────────────────────────────────┤
│ Control Buttons  │                                      │
│ ┌──────────────┐ │        Interactive Map               │
│ │  Takeoff     │ │                                      │
│ │  Land        │ │   (Click to add waypoints,           │
│ │  Add WP      │ │    Right-click to remove)            │
│ │  Start       │ │                                      │
│ │  Emergency   │ │                                      │
│ └──────────────┘ │                                      │
│                  │                                      │
│ Coordinates:     │                                      │
│ Lat: xx.xxxxxx   │                                      │
│ Lon: yy.yyyyyy   │                                      │
│                  │                                      │
│ Mission WPs:     │                                      │
│ WP1: (x, y)      │                                      │
│ WP2: (x, y)      │                                      │
│                  │                                      │
│ Activity Log:    │                                      │
│ [TIME] [INFO]... │                                      │
└──────────────────┴──────────────────────────────────────┘
```

## Technical Details

- **Framework**: Python Tkinter
- **Map Integration**: TkinterMapView (OpenStreetMap)
- **Coordinate System**: WGS84 (Latitude/Longitude)
- **Distance Calculation**: Haversine formula

## Code Structure

- **DroneControlGUI Class**: Main application class
  - `setup_ui()`: Initialize user interface
  - `setup_control_buttons()`: Create control panel
  - `setup_map()`: Initialize interactive map
  - `add_waypoint()`: Handle waypoint creation
  - `calculate_distance()`: Haversine distance calculation
  - `log_message()`: Logging system

## Log Levels

- **INFO** (Green): General information
- **SUCCESS** (Green): Successful operations
- **WARNING** (Orange): Warnings and cautions
- **ERROR** (Red): Errors and emergency stops

## Mission File Format

Saved missions are stored in JSON format:
```json
{
  "timestamp": "2025-10-15T12:00:00",
  "waypoints": [
    {"id": 1, "lat": 37.7749, "lon": -122.4194},
    {"id": 2, "lat": 37.7849, "lon": -122.4094}
  ],
  "total_distance_km": 1.23
}
```

## Notes

- All button presses are logged to both the GUI and terminal console
- Coordinates are displayed with 6 decimal places for precision
- Right-click waypoint removal works within 0.5 km radius
- Map requires internet connection for tile loading

## Future Enhancements

- Load saved mission files
- Real-time drone telemetry simulation
- Flight path visualization with lines
- Altitude planning for waypoints
- Estimated mission time calculation
- Multi-drone support
