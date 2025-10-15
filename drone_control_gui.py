import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import tkintermapview as tkmap
from datetime import datetime
import json
import math


class DroneControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Control System")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')
        
        # Mission data
        self.waypoints = []
        self.add_waypoint_mode = False
        self.mission_active = False
        self.marker_counter = 0
        self.markers = []
        
        # Mission planning
        self.takeoff_waypoint = None
        self.land_waypoint = None
        self.route_waypoints = []  # Waypoints in the flight path
        
        # Setup UI
        self.setup_ui()
        self.log_message("System initialized successfully", "INFO")
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Configure ttk style for black background
        style = ttk.Style()
        style.configure('TFrame', background='black')
        style.configure('TLabel', background='black', foreground='white')
        style.configure('TLabelframe', background='black', foreground='white')
        style.configure('TLabelframe.Label', background='black', foreground='white')
        
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
            ("Set Takeoff Point", self.set_takeoff, "green"),
            ("Set Landing Point", self.set_landing, "blue"),
            ("Add to Route", self.add_to_route, "purple"),
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
                font=("Arial", 9, "bold"),
                height=1,
                width=20
            )
            btn.pack(fill=tk.X, pady=3)
            
        # Additional control buttons
        additional_frame = ttk.Frame(control_frame)
        additional_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            additional_frame,
            text="Add Waypoint",
            command=self.toggle_waypoint_mode
        ).pack(fill=tk.X, pady=2)
        
        button_row = ttk.Frame(control_frame)
        button_row.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            button_row,
            text="Clear All",
            command=self.clear_waypoints
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        ttk.Button(
            button_row,
            text="Save",
            command=self.save_mission
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        ttk.Button(
            button_row,
            text="Load",
            command=self.load_mission
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
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
        waypoint_frame = ttk.LabelFrame(parent, text="Mission Waypoints (Double-click to navigate)", padding=10)
        waypoint_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create listbox instead of scrolled text for better interaction
        listbox_frame = tk.Frame(waypoint_frame, bg="#1a1a1a")
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.waypoint_listbox = tk.Listbox(
            listbox_frame,
            height=8,
            font=("Consolas", 9),
            bg="#1a1a1a",
            fg="#00ff00",
            selectbackground="#004400",
            selectforeground="#00ff00",
            yscrollcommand=scrollbar.set
        )
        self.waypoint_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.waypoint_listbox.yview)
        
        # Bind double-click event
        self.waypoint_listbox.bind("<Double-Button-1>", self.on_waypoint_double_click)
        
        # Bind right-click for context menu
        self.waypoint_listbox.bind("<Button-3>", self.show_waypoint_context_menu)
        
        # Mission info
        self.mission_info_var = tk.StringVar(value="Waypoints: 0")
        ttk.Label(waypoint_frame, textvariable=self.mission_info_var, font=("Arial", 9)).pack(pady=(5, 0))
        
        # Route info
        self.route_info_var = tk.StringVar(value="Route: Not planned")
        route_label = ttk.Label(waypoint_frame, textvariable=self.route_info_var, font=("Arial", 9))
        route_label.pack(pady=(2, 0))
        
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
        
    def map_left_click(self, coords):
        """Handle left click on map"""
        lat, lon = coords
        
        # Update coordinate display
        self.lat_var.set(f"Latitude: {lat:.6f}")
        self.lon_var.set(f"Longitude: {lon:.6f}")
        
        # Add waypoint if mode is active
        if self.add_waypoint_mode:
            self.add_waypoint(lat, lon)
            
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
        waypoint_name = f"WP{waypoint_id}"
        
        # Create marker on map
        marker = self.map_widget.set_marker(
            lat, lon,
            text=waypoint_name,
            marker_color_circle="gray",
            marker_color_outside="darkgray"
        )
        
        # Store waypoint data
        waypoint_data = {
            'id': waypoint_id,
            'name': waypoint_name,
            'lat': lat,
            'lon': lon,
            'marker': marker,
            'type': 'normal'  # normal, takeoff, land, route
        }
        self.waypoints.append(waypoint_data)
        self.markers.append(marker)
        
        # Log and update display
        self.log_message(f"Waypoint {waypoint_name} added at ({lat:.6f}, {lon:.6f})", "SUCCESS")
        self.update_waypoint_display()
        
    def remove_waypoint(self, waypoint):
        """Remove a specific waypoint"""
        if waypoint in self.waypoints:
            # Remove from route if it's in there
            if waypoint in self.route_waypoints:
                self.route_waypoints.remove(waypoint)
            
            # Clear takeoff/landing if this waypoint is set as such
            if waypoint == self.takeoff_waypoint:
                self.takeoff_waypoint = None
            if waypoint == self.land_waypoint:
                self.land_waypoint = None
            
            # Remove from main list
            self.waypoints.remove(waypoint)
            waypoint['marker'].delete()
            
            self.log_message(f"Waypoint {waypoint['name']} removed", "WARNING")
            self.update_waypoint_display()
    
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
            self.takeoff_waypoint = None
            self.land_waypoint = None
            self.route_waypoints.clear()
            
            self.log_message("All waypoints cleared", "WARNING")
            self.update_waypoint_display()
            
    def update_waypoint_display(self):
        """Update waypoint list display"""
        self.waypoint_listbox.delete(0, tk.END)
        
        if not self.waypoints:
            self.waypoint_listbox.insert(tk.END, "No waypoints added yet.")
        else:
            for wp in self.waypoints:
                type_indicator = ""
                if wp == self.takeoff_waypoint:
                    type_indicator = " [TAKEOFF]"
                elif wp == self.land_waypoint:
                    type_indicator = " [LAND]"
                elif wp in self.route_waypoints:
                    route_idx = self.route_waypoints.index(wp)
                    type_indicator = f" [ROUTE {route_idx + 1}]"
                
                display_text = f"{wp['name']}{type_indicator}: ({wp['lat']:.6f}, {wp['lon']:.6f})"
                self.waypoint_listbox.insert(tk.END, display_text)
                
        # Update mission info
        self.mission_info_var.set(f"Waypoints: {len(self.waypoints)}")
        self.update_route_info()
        
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
    
    def update_route_info(self):
        """Update route information display"""
        if not self.takeoff_waypoint or not self.land_waypoint:
            self.route_info_var.set("Route: Not planned (set takeoff & land)")
            return
        
        # Calculate direct distance
        direct_dist = self.calculate_distance(
            self.takeoff_waypoint['lat'], self.takeoff_waypoint['lon'],
            self.land_waypoint['lat'], self.land_waypoint['lon']
        )
        
        # Calculate route distance
        if not self.route_waypoints:
            route_dist = direct_dist
            self.route_info_var.set(f"Direct: {direct_dist:.2f} km | Route: {route_dist:.2f} km")
        else:
            # Build full route: takeoff -> route waypoints -> land
            full_route = [self.takeoff_waypoint] + self.route_waypoints + [self.land_waypoint]
            route_dist = 0.0
            for i in range(len(full_route) - 1):
                route_dist += self.calculate_distance(
                    full_route[i]['lat'], full_route[i]['lon'],
                    full_route[i + 1]['lat'], full_route[i + 1]['lon']
                )
            self.route_info_var.set(
                f"Direct: {direct_dist:.2f} km | Route: {route_dist:.2f} km | WPs: {len(self.route_waypoints)}"
            )
    
    def set_takeoff(self):
        """Set selected waypoint as takeoff point"""
        selection = self.waypoint_listbox.curselection()
        if not selection:
            messagebox.showwarning("Set Takeoff", "Please select a waypoint from the list first.")
            return
        
        idx = selection[0]
        if idx < len(self.waypoints):
            # Clear previous takeoff
            if self.takeoff_waypoint:
                self.update_waypoint_marker(self.takeoff_waypoint)
            
            # Set new takeoff
            self.takeoff_waypoint = self.waypoints[idx]
            self.takeoff_waypoint['type'] = 'takeoff'
            self.takeoff_waypoint['marker'].marker_color_circle = "green"
            self.takeoff_waypoint['marker'].marker_color_outside = "darkgreen"
            self.takeoff_waypoint['marker'].draw()
            
            self.log_message(f"Takeoff point set to {self.takeoff_waypoint['name']}", "SUCCESS")
            self.update_waypoint_display()
    
    def set_landing(self):
        """Set selected waypoint as landing point"""
        selection = self.waypoint_listbox.curselection()
        if not selection:
            messagebox.showwarning("Set Landing", "Please select a waypoint from the list first.")
            return
        
        idx = selection[0]
        if idx < len(self.waypoints):
            # Clear previous landing
            if self.land_waypoint:
                self.update_waypoint_marker(self.land_waypoint)
            
            # Set new landing
            self.land_waypoint = self.waypoints[idx]
            self.land_waypoint['type'] = 'land'
            self.land_waypoint['marker'].marker_color_circle = "blue"
            self.land_waypoint['marker'].marker_color_outside = "darkblue"
            self.land_waypoint['marker'].draw()
            
            self.log_message(f"Landing point set to {self.land_waypoint['name']}", "SUCCESS")
            self.update_waypoint_display()
    
    def add_to_route(self):
        """Add selected waypoint to flight route"""
        selection = self.waypoint_listbox.curselection()
        if not selection:
            messagebox.showwarning("Add to Route", "Please select a waypoint from the list first.")
            return
        
        idx = selection[0]
        if idx < len(self.waypoints):
            waypoint = self.waypoints[idx]
            
            # Check if it's already takeoff or land
            if waypoint == self.takeoff_waypoint or waypoint == self.land_waypoint:
                messagebox.showwarning("Add to Route", "Takeoff and landing points are automatically in the route.")
                return
            
            # Toggle route membership
            if waypoint in self.route_waypoints:
                self.route_waypoints.remove(waypoint)
                waypoint['type'] = 'normal'
                self.update_waypoint_marker(waypoint)
                self.log_message(f"Removed {waypoint['name']} from route", "WARNING")
            else:
                self.route_waypoints.append(waypoint)
                waypoint['type'] = 'route'
                waypoint['marker'].marker_color_circle = "purple"
                waypoint['marker'].marker_color_outside = "darkviolet"
                waypoint['marker'].draw()
                self.log_message(f"Added {waypoint['name']} to route (position {len(self.route_waypoints)})", "SUCCESS")
            
            self.update_waypoint_display()
    
    def update_waypoint_marker(self, waypoint):
        """Update waypoint marker color based on type"""
        if waypoint['type'] == 'takeoff':
            waypoint['marker'].marker_color_circle = "green"
            waypoint['marker'].marker_color_outside = "darkgreen"
        elif waypoint['type'] == 'land':
            waypoint['marker'].marker_color_circle = "blue"
            waypoint['marker'].marker_color_outside = "darkblue"
        elif waypoint['type'] == 'route':
            waypoint['marker'].marker_color_circle = "purple"
            waypoint['marker'].marker_color_outside = "darkviolet"
        else:
            waypoint['marker'].marker_color_circle = "gray"
            waypoint['marker'].marker_color_outside = "darkgray"
        waypoint['marker'].draw()
        

        
    def start_mission(self):
        """Handle start mission command"""
        if not self.takeoff_waypoint:
            messagebox.showwarning("Start Mission", "Please set a takeoff point first.")
            self.log_message("Mission start failed - No takeoff point set", "ERROR")
            return
        
        if not self.land_waypoint:
            messagebox.showwarning("Start Mission", "Please set a landing point first.")
            self.log_message("Mission start failed - No landing point set", "ERROR")
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mission_active = True
        
        # Build mission route
        mission_route = [self.takeoff_waypoint] + self.route_waypoints + [self.land_waypoint]
        
        # Calculate distances
        direct_distance = self.calculate_distance(
            self.takeoff_waypoint['lat'], self.takeoff_waypoint['lon'],
            self.land_waypoint['lat'], self.land_waypoint['lon']
        )
        
        route_distance = 0.0
        segment_distances = []
        for i in range(len(mission_route) - 1):
            seg_dist = self.calculate_distance(
                mission_route[i]['lat'], mission_route[i]['lon'],
                mission_route[i + 1]['lat'], mission_route[i + 1]['lon']
            )
            segment_distances.append(seg_dist)
            route_distance += seg_dist
        
        # Log mission details
        self.log_message("=" * 50, "INFO")
        self.log_message("MISSION STARTED", "SUCCESS")
        self.log_message(f"Takeoff: {self.takeoff_waypoint['name']} ({self.takeoff_waypoint['lat']:.6f}, {self.takeoff_waypoint['lon']:.6f})", "INFO")
        
        if self.route_waypoints:
            self.log_message(f"Route waypoints: {len(self.route_waypoints)}", "INFO")
            for i, wp in enumerate(self.route_waypoints, 1):
                self.log_message(f"  {i}. {wp['name']} ({wp['lat']:.6f}, {wp['lon']:.6f})", "INFO")
        
        self.log_message(f"Landing: {self.land_waypoint['name']} ({self.land_waypoint['lat']:.6f}, {self.land_waypoint['lon']:.6f})", "INFO")
        self.log_message(f"Direct distance: {direct_distance:.2f} km", "INFO")
        self.log_message(f"Route distance: {route_distance:.2f} km", "INFO")
        
        if self.route_waypoints:
            self.log_message("Segment distances:", "INFO")
            for i, seg_dist in enumerate(segment_distances):
                if i < len(mission_route) - 1:
                    self.log_message(f"  {mission_route[i]['name']} → {mission_route[i+1]['name']}: {seg_dist:.2f} km", "INFO")
        
        self.log_message("=" * 50, "INFO")
        
        # Print to console
        print(f"\n[{timestamp}] MISSION START")
        print(f"Route: {' → '.join([wp['name'] for wp in mission_route])}")
        print(f"Direct distance: {direct_distance:.2f} km")
        print(f"Route distance: {route_distance:.2f} km")
        print(f"Total waypoints: {len(mission_route)}")
        
        # Show summary dialog
        summary = f"Mission Route:\n{' → '.join([wp['name'] for wp in mission_route])}\n\n"
        summary += f"Direct Distance: {direct_distance:.2f} km\n"
        summary += f"Route Distance: {route_distance:.2f} km\n"
        summary += f"Total Waypoints: {len(mission_route)}\n\n"
        
        if len(segment_distances) > 0:
            summary += "Segment Distances:\n"
            for i, seg_dist in enumerate(segment_distances):
                if i < len(mission_route) - 1:
                    summary += f"{mission_route[i]['name']} → {mission_route[i+1]['name']}: {seg_dist:.2f} km\n"
        
        messagebox.showinfo("Mission Started", summary)
            
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
                {'id': wp['id'], 'name': wp['name'], 'lat': wp['lat'], 'lon': wp['lon']}
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
    
    def load_mission(self):
        """Load mission plan from file"""
        # Open file dialog
        filename = filedialog.askopenfilename(
            title="Load Mission",
            initialdir=".",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'r') as f:
                mission_data = json.load(f)
            
            # Validate mission data
            if 'waypoints' not in mission_data:
                messagebox.showerror("Load Error", "Invalid mission file: missing waypoints data")
                return
            
            # Clear existing waypoints
            if self.waypoints:
                if not messagebox.askyesno("Load Mission", "This will clear current waypoints. Continue?"):
                    return
                self.clear_waypoints()
            
            # Load waypoints
            loaded_count = 0
            for wp_data in mission_data['waypoints']:
                if 'lat' in wp_data and 'lon' in wp_data:
                    self.add_waypoint(wp_data['lat'], wp_data['lon'])
                    # If the loaded waypoint has a custom name, apply it
                    if 'name' in wp_data and self.waypoints:
                        self.waypoints[-1]['name'] = wp_data['name']
                        self.waypoints[-1]['marker'].text = wp_data['name']
                        self.waypoints[-1]['marker'].draw()
                    loaded_count += 1
            
            # Update display to show names
            self.update_waypoint_display()
            
            # Center map on first waypoint
            if self.waypoints:
                first_wp = self.waypoints[0]
                self.map_widget.set_position(first_wp['lat'], first_wp['lon'])
            
            timestamp = mission_data.get('timestamp', 'Unknown')
            total_distance = mission_data.get('total_distance_km', 0)
            
            self.log_message(f"Mission loaded: {loaded_count} waypoints, {total_distance:.2f} km (saved {timestamp})", "SUCCESS")
            messagebox.showinfo("Load Mission", f"Mission loaded successfully!\n\nWaypoints: {loaded_count}\nDistance: {total_distance:.2f} km\nSaved: {timestamp}")
            
        except json.JSONDecodeError:
            self.log_message(f"Failed to load mission: Invalid JSON format", "ERROR")
            messagebox.showerror("Load Error", "Failed to load mission:\nInvalid JSON format")
        except Exception as e:
            self.log_message(f"Failed to load mission: {str(e)}", "ERROR")
            messagebox.showerror("Load Error", f"Failed to load mission:\n{str(e)}")
            
    def on_waypoint_double_click(self, event):
        """Handle double-click on waypoint to navigate to it"""
        selection = self.waypoint_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        if idx < len(self.waypoints):
            waypoint = self.waypoints[idx]
            # Navigate to waypoint on map
            self.map_widget.set_position(waypoint['lat'], waypoint['lon'])
            self.map_widget.set_zoom(15)  # Zoom in on the waypoint
            
            # Update coordinate display
            self.lat_var.set(f"Latitude: {waypoint['lat']:.6f}")
            self.lon_var.set(f"Longitude: {waypoint['lon']:.6f}")
            
            self.log_message(f"Navigated to {waypoint['name']} at ({waypoint['lat']:.6f}, {waypoint['lon']:.6f})", "INFO")
    
    def show_waypoint_context_menu(self, event):
        """Show context menu on right-click in waypoint list"""
        # Get the index of the clicked item
        index = self.waypoint_listbox.nearest(event.y)
        if index < 0 or index >= len(self.waypoints):
            return
        
        # Select the item
        self.waypoint_listbox.selection_clear(0, tk.END)
        self.waypoint_listbox.selection_set(index)
        self.waypoint_listbox.activate(index)
        
        waypoint = self.waypoints[index]
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white', 
                               activebackground='#404040', activeforeground='white')
        
        context_menu.add_command(
            label=f"Rename '{waypoint['name']}'",
            command=lambda: self.rename_waypoint(waypoint)
        )
        
        context_menu.add_command(
            label=f"Delete '{waypoint['name']}'",
            command=lambda: self.delete_waypoint_with_confirm(waypoint)
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(label="Cancel", command=lambda: context_menu.unpost())
        
        # Display the menu at cursor position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def rename_waypoint(self, waypoint):
        """Show rename dialog for waypoint"""
        # Create simple input dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Rename Waypoint")
        dialog.geometry("300x120")
        dialog.configure(bg='black')
        dialog.resizable(False, False)
        
        # Center dialog on parent
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Rename {waypoint['name']}:").pack(pady=(10, 5))
        
        entry_var = tk.StringVar(value=waypoint['name'])
        entry = ttk.Entry(dialog, textvariable=entry_var, width=30)
        entry.pack(pady=5)
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        def save_name():
            new_name = entry_var.get().strip()
            if new_name and new_name != waypoint['name']:
                old_name = waypoint['name']
                waypoint['name'] = new_name
                
                # Update marker text
                waypoint['marker'].text = new_name
                waypoint['marker'].draw()
                
                # Update display
                self.update_waypoint_display()
                self.log_message(f"Renamed '{old_name}' to '{new_name}'", "SUCCESS")
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_name).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to save
        entry.bind("<Return>", lambda e: save_name())
        entry.bind("<Escape>", lambda e: cancel())
    
    def delete_waypoint_with_confirm(self, waypoint):
        """Delete waypoint with confirmation"""
        if messagebox.askyesno("Delete Waypoint", f"Are you sure you want to delete '{waypoint['name']}'?"):
            self.remove_waypoint(waypoint)
            
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
