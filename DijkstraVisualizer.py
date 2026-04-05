from flask import Flask, render_template_string, request, jsonify
import heapq
import math
import requests

app = Flask(__name__)

# --- EXPANDED REAL WORLD GPS DATA ---
NODES = {
    "Borivali": (19.2290, 72.8573), "Malad": (19.1809, 72.8475),
    "Andheri": (19.1197, 72.8464), "Juhu Beach": (19.0974, 72.8265),
    "Bandra": (19.0596, 72.8295),
    "Thane": (19.1943, 72.9701), "Dombivali": (19.2094, 73.0939), "Kalyan": (19.2403, 73.1305),
    "Powai": (19.1176, 72.9060), "Ghatkopar": (19.0856, 72.9082),
    "KJSSE (Vidyavihar)": (19.0732, 72.8998), "Kurla": (19.0645, 72.8806),
    "Vashi": (19.0771, 72.9977), "Sion": (19.0390, 72.8619),
    "Dadar": (19.0178, 72.8478), "Siddhi Vinayak": (19.0169, 72.8304),
    "Parel": (19.0096, 72.8376), "CST Station": (18.9400, 72.8352),
    "Churchgate": (18.9322, 72.8264), "Gateway of India": (18.9220, 72.8347)
}

CONNECTIONS = [
    ("Borivali", "Malad"), ("Malad", "Andheri"), ("Borivali", "Thane"),
    ("Andheri", "Juhu Beach"), ("Andheri", "Bandra"), ("Andheri", "Powai"),
    ("Juhu Beach", "Bandra"), ("Bandra", "Dadar"), ("Bandra", "Kurla"),
    ("Thane", "Powai"), ("Thane", "Dombivali"), ("Dombivali", "Kalyan"), ("Thane", "Ghatkopar"),
    ("Powai", "Ghatkopar"), ("Ghatkopar", "KJSSE (Vidyavihar)"), ("Ghatkopar", "Vashi"),
    ("KJSSE (Vidyavihar)", "Kurla"), ("Kurla", "Sion"),
    ("Vashi", "Sion"), ("Sion", "Dadar"),
    ("Dadar", "Siddhi Vinayak"), ("Dadar", "Parel"),
    ("Siddhi Vinayak", "Churchgate"), ("Parel", "CST Station"),
    ("CST Station", "Gateway of India"), ("Churchgate", "Gateway of India"),
    ("Churchgate", "CST Station")
]

def haversine_distance(coord1, coord2):
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 6371 * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

GRAPH = {node: {} for node in NODES}
for u, v in CONNECTIONS:
    dist = round(haversine_distance(NODES[u], NODES[v]), 2)
    GRAPH[u][v] = {'dist': dist}
    GRAPH[v][u] = {'dist': dist}

def dijkstra(graph, start, end):
    queue = [(0, start, [])]
    seen = set()
    mins = {start: 0}
    
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node not in seen:
            seen.add(node)
            path = path + [node]
            if node == end: return cost, path
            for next_node, attrs in graph.get(node, {}).items():
                if next_node in seen: continue
                prev_cost = mins.get(next_node, None)
                next_cost = cost + attrs['dist']
                if prev_cost is None or next_cost < prev_cost:
                    mins[next_node] = next_cost
                    heapq.heappush(queue, (next_cost, next_node, path))
    return float("inf"), []

def get_full_route_geometry(path_nodes):
    try:
        coords = ";".join([f"{NODES[node][1]},{NODES[node][0]}" for node in path_nodes])
        url = f"http://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"
        res = requests.get(url).json()
        if res.get('code') == 'Ok':
            return [[lat, lon] for lon, lat in res['routes'][0]['geometry']['coordinates']]
    except Exception as e:
        print(f"API Error: {e}")
    return [NODES[node] for node in path_nodes]

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, nodes=sorted(list(NODES.keys())), node_data=NODES, connections=CONNECTIONS)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    src = data.get('src')
    dst = data.get('dst')
    stops = data.get('stops', [])
    
    valid_stops = [s for s in stops if s and s != "None"]
    waypoints = [src] + valid_stops + [dst]
    
    total_dist = 0
    full_path = []
    
    for i in range(len(waypoints) - 1):
        segment_src = waypoints[i]
        segment_dst = waypoints[i+1]
        
        dist, path = dijkstra(GRAPH, segment_src, segment_dst)
        if dist == float('inf'):
            return jsonify({"error": f"No route found between {segment_src} and {segment_dst}."})
            
        total_dist += dist
        if not full_path:
            full_path.extend(path)
        else:
            full_path.extend(path[1:])

    geometry = get_full_route_geometry(full_path)
    
    steps = [] 
    for i in range(len(full_path)-1):
        n1, n2 = full_path[i], full_path[i+1]
        step_dist = GRAPH[n1][n2]['dist']
        steps.append({
            "from": n1,
            "to": n2,
            "dist": step_dist,
            "time": int(step_dist * 2.5)
        })

    return jsonify({
        "distance": round(total_dist, 2),
        "time": int(total_dist * 2.5),
        "path": full_path,
        "geometry": geometry,
        "steps": steps,
        "src": src,
        "dst": dst,
        "valid_stops": valid_stops
    })

# --- HTML/JS FRONTEND ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dijkstra Visualizer</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        body { margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; }
        #map { height: 100vh; width: 100vw; background: #e5e3df; }
        
        .ui-panel {
            position: absolute; top: 20px; left: 20px; z-index: 1000;
            background: rgba(255, 255, 255, 0.95); padding: 25px;
            border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
            width: 340px; max-height: 90vh; overflow-y: auto; backdrop-filter: blur(10px);
        }
        .ui-panel::-webkit-scrollbar { width: 6px; }
        .ui-panel::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }
        
        h2 { margin-top: 0; color: #1A73E8; font-size: 20px; text-align: center;}
        .subtitle { text-align: center; font-size: 13px; color: #555; margin-bottom: 15px; font-weight: bold;}
        
        label { font-weight: bold; font-size: 13px; color: #555; display: block; margin-top: 10px; }
        select { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; }
        
        .stop-container { position: relative; margin-bottom: 5px; }
        .remove-stop { 
            position: absolute; right: -5px; top: -5px; background: #ff4757; color: white; 
            border: none; border-radius: 50%; width: 22px; height: 22px; font-size: 11px; 
            font-weight: bold; cursor: pointer; display: flex; justify-content: center; align-items: center; 
            padding: 0; margin: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .remove-stop:hover { background: #e84118; transform: scale(1.1); }
        
        button {
            width: 100%; padding: 12px; margin-top: 10px; border: none; border-radius: 6px;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white; font-size: 15px; font-weight: bold; cursor: pointer; transition: 0.3s;
        }
        button:hover { opacity: 0.9; transform: translateY(-1px); }
        button.add-stop { background: #f1f2f6; color: #2f3542; border: 1px dashed #a4b0be; margin-top: 15px;}
        button.add-stop:hover { background: #dfe4ea; }
        button.export { background: linear-gradient(135deg, #e52d27 0%, #b31217 100%); margin-top: 10px;}
        
        .summary { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px; display: none; border: 1px solid #eee; }
        .summary p { margin: 5px 0; font-size: 14px; }
    </style>
</head>
<body>
    <div id="map"></div>
    
    <div class="ui-panel" data-html2canvas-ignore="true">
        <h2>Dijkstra Visualizer</h2>
        <div class="subtitle">Interactive Shortest Route Finder</div>
        
        <label>🟢 Origin:</label>
        <select id="src">
            {% for node in nodes %}<option value="{{node}}">{{node}}</option>{% endfor %}
        </select>
        
        <div id="dynamic-stops"></div>
        <button type="button" class="add-stop" onclick="addStop()">➕ Add a Stop</button>
        
        <label style="margin-top: 15px;">🏁 Destination:</label>
        <select id="dst">
            {% for node in nodes %}<option value="{{node}}" {% if node == "KJSSE (Vidyavihar)" %}selected{% endif %}>{{node}}</option>{% endfor %}
        </select>
        
        <button type="button" style="margin-top: 20px;" onclick="calculateRoute()">🗺️ Generate Route</button>
        
        <div id="summary" class="summary">
            <h4 style="margin-top:0; color:#333;">Trip Dashboard</h4>
            <p><b>Distance:</b> <span id="distVal" style="color: #1A73E8; font-weight: bold;">0</span> km</p>
            <p><b>Est. Time:</b> <span id="timeVal">0</span> mins</p>
            <button type="button" class="export" onclick="exportPdf()">📄 Generate PDF Report</button>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const nodesData = {{ node_data | tojson | safe }};
        const connections = {{ connections | tojson | safe }};
        
        const dropdownOptions = `
            <option value="None">-- Select Location --</option>
            {% for node in nodes %}<option value="{{node}}">{{node}}</option>{% endfor %}
        `;

        const map = L.map('map', {zoomControl: false, preferCanvas: true}).setView([19.11, 72.90], 11);
        L.control.zoom({position: 'bottomright'}).addTo(map);
        
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap'
        }).addTo(map);

        let currentRouteLayer = null;
        let activeMarkers = [];
        let globalSteps = []; 
        let globalRouteInfo = {};
        let stopCount = 0;
        let clickState = 0; 

        // Draw initial faint dots
        for (const [name, coords] of Object.entries(nodesData)) {
            const marker = L.circleMarker(coords, {
                radius: 5, fillColor: '#ccc', color: '#fff', weight: 1, fillOpacity: 0.8
            }).addTo(map).bindTooltip(name);
            
            marker.on('click', function() {
                if (clickState === 0) {
                    document.getElementById('src').value = name;
                    clickState = 1;
                } else if (clickState === 1) {
                    document.getElementById('dst').value = name;
                    clickState = 2;
                } else {
                    addStop(); 
                    const stopSelects = document.querySelectorAll('.stop-select');
                    stopSelects[stopSelects.length-1].value = name;
                    clickState = 0; 
                }
            });
        }

        // Draw faint grey network lines
        connections.forEach(conn => {
            const p1 = nodesData[conn[0]];
            const p2 = nodesData[conn[1]];
            L.polyline([p1, p2], {color: '#bdc3c7', weight: 1.5, dashArray: '5, 5'}).addTo(map);
        });

        function addStop() {
            stopCount++;
            const container = document.getElementById('dynamic-stops');
            const stopDiv = document.createElement('div');
            stopDiv.className = 'stop-container';
            stopDiv.id = 'stop-group-' + stopCount;
            
            stopDiv.innerHTML = `
                <label>⏸️ Stop ${stopCount}:</label>
                <select class="stop-select">${dropdownOptions}</select>
                <button type="button" class="remove-stop" onclick="removeStop(${stopCount})">X</button>
            `;
            container.appendChild(stopDiv);
        }

        function removeStop(id) {
            document.getElementById('stop-group-' + id).remove();
            const labels = document.querySelectorAll('#dynamic-stops label');
            labels.forEach((lbl, index) => {
                lbl.innerText = `⏸️ Stop ${index + 1}:`;
            });
            stopCount--;
        }

        // NEW: Creating a beautiful custom HTML label that sticks firmly to the map
        function createCustomLabel(emoji, text) {
            return L.divIcon({
                html: `<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; width:120px;">
                         <span style="font-size: 28px; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5));">${emoji}</span>
                         <span style="background: white; border: 2px solid #1A73E8; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 13px; color: #333; box-shadow: 0px 2px 5px rgba(0,0,0,0.3); margin-top: -5px;">${text}</span>
                       </div>`,
                className: 'empty',
                iconSize: [120, 70],
                iconAnchor: [60, 35] // Perfectly centers the icon and text over the dot
            });
        }

        async function calculateRoute() {
            const src = document.getElementById('src').value;
            const dst = document.getElementById('dst').value;
            const stopElements = document.querySelectorAll('.stop-select');
            const stops = Array.from(stopElements).map(el => el.value);
            
            const btn = document.querySelector('button[onclick="calculateRoute()"]');
            btn.innerText = "Calculating...";
            
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({src, dst, stops})
            });
            
            const data = await response.json();
            btn.innerText = "🗺️ Generate Route";
            
            if (data.error) {
                alert(data.error);
                return;
            }
            
            globalSteps = data.steps; 
            globalRouteInfo = data;
            
            if (currentRouteLayer) map.removeLayer(currentRouteLayer);
            activeMarkers.forEach(m => map.removeLayer(m));
            activeMarkers = [];
            
            currentRouteLayer = L.polyline(data.geometry, {color: '#2ed573', weight: 6, opacity: 0.9}).addTo(map);
            map.fitBounds(currentRouteLayer.getBounds(), {padding: [70, 70]});
            
            // Add the solid, beautiful HTML labels
            activeMarkers.push(L.marker(nodesData[data.src], {icon: createCustomLabel('🟢', data.src)}).addTo(map));
            
            data.valid_stops.forEach((stopNode) => {
                activeMarkers.push(L.marker(nodesData[stopNode], {icon: createCustomLabel('⏸️', stopNode)}).addTo(map));
            });
            
            activeMarkers.push(L.marker(nodesData[data.dst], {icon: createCustomLabel('🏁', data.dst)}).addTo(map));
            
            document.getElementById('distVal').innerText = data.distance;
            document.getElementById('timeVal').innerText = data.time;
            document.getElementById('summary').style.display = "block";
        }

        async function exportPdf() {
            const btn = document.querySelector('.export');
            btn.innerText = "Capturing Map... Please Wait";
            
            // CRITICAL FIX: Reset window scroll to fix html2canvas offset bug
            window.scrollTo(0,0);
            
            // Note: We deliberately DO NOT re-fit bounds here. Moving the map right before 
            // a screenshot is exactly what causes the blue route line to visually detach!
            
            const mapContainer = document.getElementById('map');
            const canvas = await html2canvas(mapContainer, {
                useCORS: true, 
                allowTaint: true,
                ignoreElements: (element) => element.classList.contains('ui-panel')
            });
            const imgData = canvas.toDataURL('image/jpeg', 0.8);

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            doc.setFont("helvetica", "bold");
            doc.setFontSize(22);
            doc.text("Dijkstra Route Visualizer", 105, 20, null, null, "center");
            
            doc.setFontSize(14);
            const journeyText = `Prepared Route: ${globalRouteInfo.src} to ${globalRouteInfo.dst}`;
            doc.text(journeyText, 105, 30, null, null, "center");
            
            if (globalRouteInfo.valid_stops.length > 0) {
                doc.setFont("helvetica", "italic");
                doc.setFontSize(11);
                doc.text(`Includes ${globalRouteInfo.valid_stops.length} designated stop(s).`, 105, 36, null, null, "center");
                doc.line(20, 42, 190, 42);
            } else {
                doc.line(20, 36, 190, 36);
            }
            
            let yOffset = globalRouteInfo.valid_stops.length > 0 ? 52 : 46;
            const dist = document.getElementById('distVal').innerText;
            const time = document.getElementById('timeVal').innerText;
            
            doc.setFont("helvetica", "bold");
            doc.setFontSize(12);
            doc.text(`Total Distance: ${dist} km`, 20, yOffset);
            doc.text(`Estimated Travel Time: ${time} mins`, 120, yOffset);
            
            yOffset += 8;
            doc.addImage(imgData, 'JPEG', 20, yOffset, 170, 90);
            doc.setDrawColor(0);
            doc.rect(20, yOffset, 170, 90); 
            
            yOffset += 105;
            doc.setFontSize(14);
            doc.text("Step-by-Step Directions:", 20, yOffset);
            
            doc.setFont("helvetica", "normal");
            doc.setFontSize(11);
            
            let startY = yOffset + 10;
            globalSteps.forEach((step, index) => {
                if (startY > 280) {
                    doc.addPage();
                    startY = 20;
                }
                const stepText = `${index + 1}. Travel from ${step.from} -> ${step.to}`;
                const detailText = `(${step.dist} km | ~${step.time} mins)`;
                
                doc.text(stepText, 20, startY);
                doc.text(detailText, 140, startY); 
                startY += 8;
            });
            
            doc.save("Dijkstra_Route_Report.pdf");
            btn.innerText = "📄 Generate PDF Report";
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("\n🚀 Server running! Open http://127.0.0.1:5000 in your web browser.\n")
    app.run(debug=True)
