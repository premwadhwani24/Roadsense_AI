// static/script.js

let map;
const zoneColors = {
    'GREEN': '#5cb85c',
    'YELLOW': '#f0ad4e',
    'RED': '#d9534f'
};

function initMap() {
    // Default center (e.g., New Delhi area for the simulated data)
    const defaultCenter = { lat: 28.65, lng: 77.15 }; 
    
    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultCenter,
        zoom: 12,
        mapId: "DEMO_MAP_ID" // Placeholder for a custom map ID
    });

    loadRoadSegments();
    
    document.getElementById('generateReportBtn').addEventListener('click', generateReport);
}

function loadRoadSegments() {
    fetch('/api/get_segments')
        .then(response => response.json())
        .then(segments => {
            segments.forEach(segment => {
                const marker = new google.maps.Marker({
                    position: { lat: segment.lat, lng: segment.lng },
                    map: map,
                    title: segment.name,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        fillColor: zoneColors[segment.zone] || '#999',
                        fillOpacity: 1,
                        strokeWeight: 1,
                        scale: 10
                    }
                });

                const infoWindow = new google.maps.InfoWindow({
                    content: `<div><strong>Road:</strong> ${segment.name} (${segment.id})</div>
                              <div><strong>Current Status:</strong> ${segment.zone} Zone</div>`
                });

                marker.addListener("click", () => {
                    infoWindow.open({
                        anchor: marker,
                        map,
                    });
                });
            });
        })
        .catch(error => console.error('Error loading road segments:', error));
}

function generateReport() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const area = document.getElementById('areaSelect').value;
    const statusMessage = document.getElementById('statusMessage');

    if (!startDate || !endDate) {
        statusMessage.textContent = "Please select a valid date range.";
        return;
    }

    statusMessage.textContent = "Generating report, please wait...";
    document.getElementById('generateReportBtn').disabled = true;

    fetch('/report/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ startDate, endDate, area }),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => Promise.reject(err.error));
        }
        return response.blob();
    })
    .then(blob => {
        // Create a temporary link to download the file
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        // The filename is set in the backend response header
        a.download = response.headers.get('Content-Disposition').split('filename=')[1].replace(/"/g, '');
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        statusMessage.textContent = "Report successfully generated and downloaded!";
    })
    .catch(error => {
        statusMessage.textContent = `Error: ${error}. Check server logs.`;
        console.error('Error generating report:', error);
    })
    .finally(() => {
        document.getElementById('generateReportBtn').disabled = false;
    });
}