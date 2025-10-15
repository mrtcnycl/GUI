"""
Drone Control GUI Application
A graphical interface for drone control with interactive map functionality
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import tkintermapview as tkmap
from datetime import datetime
import json
import math


class DroneControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Control System")
        self.root.geometry("1200x800")
        
        # Mission data
        self.waypoints = []
        self.add_waypoint_mode = False
        self.mission_active = False
        self.marker_counter = 0
        self.markers = []
        
        # Setup UI
        self.setup_ui()
        self.log_message("System initialized successfully", "INFO")
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls and Logs
        left_panel = ttk.Frame(main_container, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Right panel - Map
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup components
        self.setup_control_buttons(left_panel)
        self.setup_coordinate_display(left_panel)
        self.setup_waypoint_list(left_panel)
        self.setup_log_panel(left_panel)
        self.setup_map(right_panel)
        
    def setup_control_buttons(self, parent):
        """Setup control buttons panel"""
        control_frame = ttk.LabelFrame(parent, text="Drone Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Button configurations
        buttons = [
            ("Takeoff", self.takeoff, "green"),
            ("Land", self.land, "blue"),
            ("Add Waypoint", self.toggle_waypoint_mode, "purple"),
            ("Start Mission", self.start_mission, "orange"),
            ("Emergency Stop", self.emergency_stop, "red")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                control_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 10, "bold"),
                height=2
            )
            btn.pack(fill=tk.X, pady=5)
            
        # Additional control buttons
        additional_frame = ttk.Frame(control_frame)
        additional_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            additional_frame,
            text="Clear All Waypoints",
            command=self.clear_waypoints
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(
            additional_frame,
            text="Save Mission",
            command=self.save_mission
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
    def setup_coordinate_display(self, parent):
        """Setup coordinate display panel"""
        coord_frame = ttk.LabelFrame(parent, text="Current Coordinates", padding=10)
        coord_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lat_var = tk.StringVar(value="Latitude: --")
        self.lon_var = tk.StringVar(value="Longitude: --")
        
        ttk.Label(coord_frame, textvariable=self.lat_var, font=("Arial", 10)).pack(anchor=tk.W)
        ttk.Label(coord_frame, textvariable=self.lon_var, font=("Arial", 10)).pack(anchor=tk.W)
        
    def setup_waypoint_list(self, parent):
        """Setup waypoint list display"""
        waypoint_frame = ttk.LabelFrame(parent, text="Mission Waypoints", padding=10)
        waypoint_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrolled text for waypoints
        self.waypoint_display = scrolledtext.ScrolledText(
            waypoint_frame,
            height=8,
            font=("Consolas", 9),
            bg="#f0f0f0"
        )
        self.waypoint_display.pack(fill=tk.BOTH, expand=True)
        
        # Mission info
        self.mission_info_var = tk.StringVar(value="Waypoints: 0 | Total Distance: 0.00 km")
        ttk.Label(waypoint_frame, textvariable=self.mission_info_var, font=("Arial", 9)).pack(pady=(5, 0))
        
    def setup_log_panel(self, parent):
        """Setup logging panel"""
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_display = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#00ff00"
        )
        self.log_display.pack(fill=tk.BOTH, expand=True)
        
    def setup_map(self, parent):
        """Setup interactive map"""
        map_frame = ttk.LabelFrame(parent, text="Mission Map", padding=10)
        map_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create map widget (default location: San Francisco)
        self.map_widget = tkmap.TkinterMapView(map_frame, corner_radius=0)
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        
        # Set initial position
        self.map_widget.set_position(37.7749, -122.4194)
        self.map_widget.set_zoom(12)
        
        # Bind events
        self.map_widget.add_left_click_map_command(self.map_left_click)
        self.map_widget.add_right_click_menu_command(
            "Remove Waypoint",
            self.map_right_click
        )
        
    def map_left_click(self, coords):
        """Handle left click on map"""
        lat, lon = coords
        
        # Update coordinate display
        self.lat_var.set(f"Latitude: {lat:.6f}")
        self.lon_var.set(f"Longitude: {lon:.6f}")
        
        # Add waypoint if mode is active
        if self.add_waypoint_mode:
            self.add_waypoint(lat, lon)
            
    def map_right_click(self, coords):
        """Handle right click on map"""
        lat, lon = coords
        self.remove_nearest_waypoint(lat, lon)
        
    def toggle_waypoint_mode(self):
        """Toggle waypoint adding mode"""
        self.add_waypoint_mode = not self.add_waypoint_mode
        
        if self.add_waypoint_mode:
            self.log_message("Waypoint mode ACTIVATED - Click on map to add waypoints", "INFO")
            messagebox.showinfo("Waypoint Mode", "Click on the map to add waypoints.\nClick 'Add Waypoint' again to exit this mode.")
        else:
            self.log_message("Waypoint mode DEACTIVATED", "INFO")
            
    def add_waypoint(self, lat, lon):
        """Add a waypoint to the mission"""
        self.marker_counter += 1
        waypoint_id = self.marker_counter
        
        # Create marker on map
        marker = self.map_widget.set_marker(
            lat, lon,
            text=f"WP{waypoint_id}",
            marker_color_circle="blue",
            marker_color_outside="darkblue"
        )
        
        # Store waypoint data
        waypoint_data = {
            'id': waypoint_id,
            'lat': lat,
            'lon': lon,
            'marker': marker
        }
        self.waypoints.append(waypoint_data)
        self.markers.append(marker)
        
        # Log and update display
        self.log_message(f"Waypoint {waypoint_id} added at ({lat:.6f}, {lon:.6f})", "SUCCESS")
        self.update_waypoint_display()
        
    def remove_nearest_waypoint(self, lat, lon):
        """Remove the nearest waypoint to clicked position"""
        if not self.waypoints:
            return
            
        # Find nearest waypoint
        min_distance = float('inf')
        nearest_idx = -1
        
        for idx, wp in enumerate(self.waypoints):
            distance = self.calculate_distance(lat, lon, wp['lat'], wp['lon'])
            if distance < min_distance:
                min_distance = distance
                nearest_idx = idx
                
        # Remove if within reasonable distance (0.5 km)
        if nearest_idx >= 0 and min_distance < 0.5:
            waypoint = self.waypoints.pop(nearest_idx)
            waypoint['marker'].delete()
            self.log_message(f"Waypoint {waypoint['id']} removed", "WARNING")
            self.update_waypoint_display()
        else:
            self.log_message("No waypoint found near clicked location", "ERROR")
            
    def clear_waypoints(self):
        """Clear all waypoints"""
        if not self.waypoints:
            messagebox.showinfo("Clear Waypoints", "No waypoints to clear.")
            return
            
        if messagebox.askyesno("Clear Waypoints", "Are you sure you want to clear all waypoints?"):
            for waypoint in self.waypoints:
                waypoint['marker'].delete()
                
            self.waypoints.clear()
            self.markers.clear()
            self.log_message("All waypoints cleared", "WARNING")
            self.update_waypoint_display()
            
    def update_waypoint_display(self):
        """Update waypoint list display"""
        self.waypoint_display.delete(1.0, tk.END)
        
        if not self.waypoints:
            self.waypoint_display.insert(tk.END, "No waypoints added yet.\n")
        else:
            for idx, wp in enumerate(self.waypoints, 1):
                self.waypoint_display.insert(
                    tk.END,
                    f"WP{wp['id']}: ({wp['lat']:.6f}, {wp['lon']:.6f})\n"
                )
                
        # Update mission info
        total_distance = self.calculate_total_distance()
        self.mission_info_var.set(
            f"Waypoints: {len(self.waypoints)} | Total Distance: {total_distance:.2f} km"
        )
        
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in km"""
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
        
    def calculate_total_distance(self):
        """Calculate total mission distance"""
        if len(self.waypoints) < 2:
            return 0.0
            
        total = 0.0
        for i in range(len(self.waypoints) - 1):
            wp1 = self.waypoints[i]
            wp2 = self.waypoints[i + 1]
            total += self.calculate_distance(wp1['lat'], wp1['lon'], wp2['lat'], wp2['lon'])
            
        return total
        
    def takeoff(self):
        """Handle takeoff command"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_message(f"TAKEOFF command initiated", "SUCCESS")
        print(f"[{timestamp}] TAKEOFF - Drone launching...")
        
    def land(self):
        """Handle land command"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_message(f"LAND command initiated", "SUCCESS")
        print(f"[{timestamp}] LAND - Drone landing at current position...")
        
    def start_mission(self):
        """Handle start mission command"""
        if len(self.waypoints) < 1:
            messagebox.showwarning("Start Mission", "Please add at least one waypoint before starting mission.")
            self.log_message("Mission start failed - No waypoints defined", "ERROR")
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mission_active = True
        self.log_message(f"MISSION STARTED - {len(self.waypoints)} waypoints, {self.calculate_total_distance():.2f} km", "SUCCESS")
        print(f"[{timestamp}] MISSION START - Executing {len(self.waypoints)} waypoint mission...")
        
        for wp in self.waypoints:
            print(f"  → Waypoint {wp['id']}: ({wp['lat']:.6f}, {wp['lon']:.6f})")
            
    def emergency_stop(self):
        """Handle emergency stop command"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mission_active = False
        self.log_message("⚠️ EMERGENCY STOP ACTIVATED ⚠️", "ERROR")
        print(f"[{timestamp}] EMERGENCY STOP - All operations halted immediately!")
        messagebox.showwarning("Emergency Stop", "All drone operations have been halted!")
        
    def save_mission(self):
        """Save mission plan to file"""
        if not self.waypoints:
            messagebox.showinfo("Save Mission", "No waypoints to save.")
            return
            
        mission_data = {
            'timestamp': datetime.now().isoformat(),
            'waypoints': [
                {'id': wp['id'], 'lat': wp['lat'], 'lon': wp['lon']}
                for wp in self.waypoints
            ],
            'total_distance_km': self.calculate_total_distance()
        }
        
        filename = f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(mission_data, f, indent=2)
            self.log_message(f"Mission saved to {filename}", "SUCCESS")
            messagebox.showinfo("Save Mission", f"Mission saved successfully to:\n{filename}")
        except Exception as e:
            self.log_message(f"Failed to save mission: {str(e)}", "ERROR")
            messagebox.showerror("Save Error", f"Failed to save mission:\n{str(e)}")
            
    def log_message(self, message, level="INFO"):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding
        colors = {
            "INFO": "#00ff00",
            "SUCCESS": "#00ff00",
            "WARNING": "#ffaa00",
            "ERROR": "#ff0000"
        }
        
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        self.log_display.insert(tk.END, log_entry)
        self.log_display.see(tk.END)
        
        # Also print to console
        print(log_entry.strip())


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = DroneControlGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
