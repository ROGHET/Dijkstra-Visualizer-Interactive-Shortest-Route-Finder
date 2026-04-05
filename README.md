# 📍 Dijkstra Visualizer: Interactive Shortest Route Finder

A smart, interactive web application that computes and visualizes optimal real-world driving routes across Mumbai using **Dijkstra's Algorithm** and the **OSRM API**.  
Built for the Analysis of Algorithms (AOA) mini-project at **K. J. Somaiya School of Engineering**, this project demonstrates Dijkstra's Algorithm, graph theory, API integration, and full-stack web development.

---



## 🗺️ Application Preview

<p align="center">
  <b>🌍 Interactive Map & UI Dashboard</b><br>
  <img src="https://github.com/user-attachments/assets/52eefbce-6b0f-4c57-a948-cd8381b8cc87" alt="Map Interface" width="80%" style="border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.3); margin:20px 0;" />
</p>

<p align="center">
  <b>📄 Automated PDF Itinerary Export</b><br>
  <img src="https://github.com/user-attachments/assets/60c9edd0-d181-45bc-8f97-ef5c7d5a73bc" alt="PDF Export" width="80%" style="border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.3); margin:20px 0;" />
</p>

---

## ✨ Problem Statement
Existing navigation approaches often lack flexibility when it comes to handling multiple custom stops, and many commercial systems act as "black boxes" without demonstrating *how* routes are computed.  

This project addresses the problem by designing a transparent, educational system that not only finds the shortest path but actively demonstrates algorithmic graph computation while allowing complete user customization.

---

## 🎯 Core Objectives
1. Implement **Dijkstra's Algorithm** using a Min-Heap for highly efficient shortest-path computation on a real-world graph.  
2. Support complex routing by seamlessly segmenting journeys to handle **multiple intermediate stops**.  
3. Visualize computed paths on an interactive web map using **Leaflet.js** and the **OSRM API**.  
4. Calculate accurate geographical distances between GPS coordinates using the **Haversine formula**.  
5. Enable users to export structured travel itineraries and map screenshots as **PDF reports**.

---

## 🧩 Features

### 📍 Route Planning
- **Dynamic Selection:** Choose an Origin, Destination, and multiple custom "Via" Stops from 20+ real locations across Mumbai and surrounding suburbs.
- **Glassmorphism UI:** A sleek, floating control panel that updates real-time travel metrics (Total Distance & Estimated Time).

### 🧠 Algorithmic Routing
- **Real-World Graphing:** Automatically generates graph edge weights (distances) dynamically based on exact Latitude and Longitude coordinates.
- **Smart Path Stitching:** Runs Dijkstra's algorithm recursively to connect complex multi-stop journeys into one continuous, optimal path.

### 🗺️ Map Integration
- **Custom Map Layers:** Utilizes the CartoDB Positron minimalist map to remove street clutter and highlight the routing logic.
- **True Road Geometry:** Instead of drawing straight lines between dots, it queries the OSRM API to draw the *actual driving streets* required to make the journey.

### 📄 Report Generation
- **Instant Export:** Captures a high-resolution screenshot of the map (avoiding UI overlap) and generates a structured PDF.
- **Step-by-Step Breakdown:** Calculates and prints the exact distance and travel time for *each individual segment* of the trip.

---

## 🧠 Concepts Demonstrated

- **Dijkstra's Algorithm:** The core pathfinding logic used to guarantee the mathematically shortest route between nodes on a weighted graph.
- **Data Structures (DSA):** Utilizing Adjacency Lists for graph representation, and Min-Heaps (Priority Queues) for highly efficient `O(log V)` node extraction.
- **Mathematical Computing:** Applying spherical geometry and the Haversine formula to calculate accurate physical distances (in km) between GPS coordinates.
- **Web Architecture:** Implementing a Client-Server model where the Python Flask backend processes heavy graph logic, and the JavaScript frontend dynamically renders the UI and Map.

---



## 🖥️ Technologies Used
- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, JavaScript, Leaflet.js
- **APIs:** OpenStreetMap (Tiles), OSRM (Road Geometry)
- **Libraries:** `heapq`, `math`, `requests`, `html2canvas`, `jsPDF`

---

## 🧰 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone [https://github.com/ROGHET/Dijkstra-Visualizer.git](https://github.com/ROGHET/Dijkstra-Visualizer.git)
   cd Dijkstra-Visualizer

## 📂 Project Structure

```text
Dijkstra-Visualizer/
│
├── DijkstraVisualizer.py        # Main application file (Flask backend + Graph Logic + HTML/JS Frontend)
├── requirements.txt             # Python dependencies (Flask, requests)
├── .gitignore                   # Git ignore configurations (pycache, downloaded PDFs, etc.)
└── LICENSE                      # MIT License

```

## 📊 Time & Space Complexity

**Time Complexity:**
* **Standard Routing:** `O((V + E) log V)` 
  * *V = Vertices (Nodes), E = Edges (Roads)*
  * Extracting the minimum node from the Priority Queue takes `O(log V)` and is done up to `V` times. Relaxing (checking) neighbors takes `O(log V)` and is done `E` times.
* **Multi-Stop Routing:** `O(k × (V + E) log V)`
  * Where `k` is the number of intermediate stops. The algorithm independently computes the optimal path for each segment and stitches them seamlessly together.

**Space Complexity:** * **Overall Space:** `O(V + E)`
  * Constructing the graph using an Adjacency List requires `O(V + E)` memory. The Min-Heap priority queue and tracking dictionaries (`seen` nodes, `mins` distances) require at most `O(V)` supplementary space.

---

## 👨‍💻 Author

**Harshit Rawat** *K. J. Somaiya School of Engineering*

📧 **Email:** harshitrawat3125@gmail.com, rawatharshit3424@gmail.com, harshit.rawat@somaiya.edu  
💼 **GitHub:** [github.com/ROGHET](https://github.com/ROGHET)
