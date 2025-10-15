# Drone Control GUI Application

A Python-based graphical user interface for drone mission planning with interactive map functionality and advanced route optimization.

## Features

### Mission Planning System
-  **Set Takeoff Point** (Green Button)
  - Select any waypoint as the mission starting point
  - Marker turns green on the map
  - Required before starting a mission

-  **Set Landing Point** (Blue Button)
  - Select any waypoint as the mission ending point
  - Marker turns blue on the map
  - Required before starting a mission

-  **Add to Route** (Purple Button)
  - Add intermediate waypoints to the flight path
  - Toggle on/off by clicking again on selected waypoint
  - Markers turn purple on the map
  - Shows route position in the waypoint list

-  **Start Mission** (Orange Button)
  - Validates takeoff and landing points are set
  - Calculates and displays:
    - **Direct Distance**: Shortest path from takeoff to landing
    - **Route Distance**: Total distance following all waypoints
    - **Segment Distances**: Distance between each consecutive waypoint
  - Shows complete mission summary with full route path

-  **Emergency Stop** (Red Button)
  - Immediately halts all operations
  - Emergency safety feature

### Interactive Map Features
-  **OpenStreetMap Integration**
  - Click anywhere to add waypoints
  - Real-time GPS coordinate display
  - Color-coded markers:
    -  Green = Takeoff point
    -  Blue = Landing point
    -  Purple = Route waypoints
    -  Gray = Unused waypoints
  - Right-click context menu for waypoint removal
  - Zoom and pan controls

### Waypoint Management
-  **Interactive Waypoint List**
  - Double-click to navigate to waypoint on map
  - Right-click to rename waypoints
  - Visual indicators: `[TAKEOFF]`, `[LAND]`, `[ROUTE 1]`
  - Shows coordinates for each waypoint

-  **Save/Load Missions**
  - Export missions to JSON files with timestamp
  - Load previously saved missions
  - Preserves waypoint names and types
  - Automatic mission restoration

-  **Activity Log Panel**
  - Real-time event logging
  - Color-coded messages (INFO, SUCCESS, WARNING, ERROR)
  - Terminal-style interface
  - Timestamps for all actions

### Advanced Features
-  **Distance Calculations** (Haversine formula)
  - Direct distance between takeoff and landing
  - Total route distance through all waypoints
  - Individual segment distances
  - Displayed in kilometers

-  **Mission Analytics**
  - Waypoint count tracking
  - Route optimization information
  - Complete mission summary on start

## Installation

### Prerequisites
- Python 3.7 or higher
- Internet connection (for map tiles)

### Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install tkintermapview
```

## Usage

### Running the Application
```bash
python drone_control_gui.py
```

### Quick Start Guide

#### 1. Adding Waypoints
- Click the **"Add Waypoint"** button
- Click anywhere on the map to place waypoint markers
- Click **"Add Waypoint"** again to exit waypoint mode

#### 2. Planning Your Mission
1. Select a waypoint from the list
2. Click **"Set Takeoff Point"** (marker turns green)
3. Select another waypoint
4. Click **"Set Landing Point"** (marker turns blue)
5. (Optional) Select additional waypoints and click **"Add to Route"** (markers turn purple)

#### 3. Starting the Mission
- Click **"Start Mission"** to see:
  - Complete route path (e.g., WP1 → WP3 → WP5 → WP2)
  - Direct distance (straight line from takeoff to landing)
  - Route distance (total distance through all waypoints)
  - Segment distances (distance between each waypoint pair)

#### 4. Managing Waypoints
- **Double-click** a waypoint in the list to navigate to it on the map
- **Right-click** a waypoint to rename it or remove it
- Click **"Clear All"** to remove all waypoints

#### 5. Saving and Loading Missions
- Click **"Save"** to export your mission plan to a JSON file
- Click **"Load"** to import a previously saved mission
- Files are saved with timestamp: `mission_YYYYMMDD_HHMMSS.json`

## Technical Details

### Technology Stack
- **Framework**: Python Tkinter
- **Map Library**: TkinterMapView (OpenStreetMap)
- **Coordinate System**: WGS84 (Latitude/Longitude)
- **Distance Algorithm**: Haversine formula for great-circle distance

### Code Structure
- **DroneControlGUI Class**: Main application class
  - `setup_ui()`: Initialize user interface with black theme
  - `setup_control_buttons()`: Create mission control panel
  - `setup_map()`: Initialize interactive map widget
  - `add_waypoint()`: Create waypoint markers
  - `set_takeoff()`: Set takeoff point
  - `set_landing()`: Set landing point
  - `add_to_route()`: Manage route waypoints
  - `start_mission()`: Calculate and display mission analytics
  - `calculate_distance()`: Haversine distance calculation
  - `update_waypoint_marker()`: Update marker colors
  - `save_mission()` / `load_mission()`: Mission persistence
  - `log_message()`: Logging system

### Mission File Format

Saved missions are stored in JSON format with the following structure:

```json
{
  "timestamp": "2025-10-15T12:00:00",
  "waypoints": [
    {
      "id": 1,
      "name": "Launch Pad",
      "lat": 37.7749,
      "lon": -122.4194
    },
    {
      "id": 2,
      "name": "Checkpoint Alpha",
      "lat": 37.7849,
      "lon": -122.4094
    }
  ],
  "total_distance_km": 1.23
}
```

## User Interface

### Color Scheme
- **Background**: Black (#000000)
- **Frames**: Black with white labels
- **Waypoint Display**: Dark gray (#1a1a1a) with green text
- **Activity Log**: Black (#1e1e1e) with green terminal text
- **Buttons**: Color-coded (Green, Blue, Purple, Orange, Red)

### Log Levels
- **INFO** (Green): General information and system messages
- **SUCCESS** (Green): Successful operations
- **WARNING** (Orange): Warnings and cautions
- **ERROR** (Red): Errors and emergency stops

### Marker Colors
- **Green**: Takeoff point
- **Blue**: Landing point
- **Purple**: Route waypoints
- **Gray**: Unassigned waypoints

## Mission Planning Workflow

1. **Add Waypoints** → Place markers on map
2. **Set Takeoff** → Select and mark starting point (green)
3. **Set Landing** → Select and mark ending point (blue)
4. **Add to Route** → Select intermediate waypoints (purple)
5. **Start Mission** → View complete mission analysis
6. **Save Mission** → Export for later use

## Distance Calculations

### Direct Distance
The shortest path between takeoff and landing points using the Haversine formula:
- Accounts for Earth's curvature
- Great-circle distance
- Measured in kilometers

### Route Distance
Total distance when following the planned route:
- Takeoff → Route Waypoint 1 → Route Waypoint 2 → ... → Landing
- Sum of all segment distances
- Useful for comparing with direct distance

### Segment Distances
Individual distances between consecutive waypoints in the route:
- Helps identify longest/shortest segments
- Useful for mission timing estimates


## System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.7 or higher
- **RAM**: 512 MB minimum
- **Display**: 1200x800 minimum resolution recommended
- **Internet**: Required for map tile loading

## Dependencies

- `tkinter`: Python standard library (GUI framework)
- `tkintermapview`: Map widget for Tkinter
- `json`: Python standard library (mission file handling)
- `math`: Python standard library (distance calculations)
- `datetime`: Python standard library (timestamps)

**Built with Python & Tkinter** | **Powered by OpenStreetMap**
