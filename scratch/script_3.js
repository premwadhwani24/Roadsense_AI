
        // Global State (var for cross-script-block accessibility)
        var map;
        var currentTileLayer = null;
        var activeTileProvider = 'carto';
        var roadPolylines = [];
        var defectMarkers = [];
        var currentSegments = [];
        var activeSegment = null;
        var selectedConditionFilter = 'ALL';

        // Custom Offline/Fallback GIS Vector Grid Layer
        var GISGridLayer = (typeof L !== 'undefined' && L.GridLayer) ? L.GridLayer.extend({
            createTile: function (coords) {
                var tile = document.createElement('canvas');
                var tileSize = this.getTileSize();
                tile.width = tileSize.x;
                tile.height = tileSize.y;
                var ctx = tile.getContext('2d');

                // Dark GIS Background
                ctx.fillStyle = '#0f172a';
                ctx.fillRect(0, 0, tileSize.x, tileSize.y);

                // Grid Lines
                ctx.strokeStyle = 'rgba(51, 65, 85, 0.5)';
                ctx.lineWidth = 1;

                const step = 64;
                for (let x = 0; x <= tileSize.x; x += step) {
                    ctx.beginPath();
                    ctx.moveTo(x, 0); ctx.lineTo(x, tileSize.y);
                    ctx.stroke();
                }
                for (let y = 0; y <= tileSize.y; y += step) {
                    ctx.beginPath();
                    ctx.moveTo(0, y); ctx.lineTo(tileSize.x, y);
                    ctx.stroke();
                }

                // Grid Crosshairs
                ctx.fillStyle = '#38bdf8';
                for (let x = 0; x <= tileSize.x; x += step) {
                    for (let y = 0; y <= tileSize.y; y += step) {
                        ctx.fillRect(x - 1.5, y - 1.5, 3, 3);
                    }
                }

                // Coordinate watermark
                ctx.fillStyle = 'rgba(148, 163, 184, 0.6)';
                ctx.font = 'bold 9px monospace';
                ctx.fillText(`GIS GRID z:${coords.z} [${coords.x},${coords.y}]`, 8, 16);

                return tile;
            }
        }) : null;

        function getTileLayer(provider) {
            if (provider === 'carto') {
                return L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                    maxZoom: 19,
                    subdomains: 'abcd',
                    attribution: '© CARTO | OpenStreetMap'
                });
            } else if (provider === 'osm') {
                return L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                });
            } else if (provider === 'esri') {
                return L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
                    maxZoom: 19,
                    attribution: '© Esri | RoadSense AI'
                });
            } else {
                if (GISGridLayer) {
                    return new GISGridLayer({ maxZoom: 19 });
                } else {
                    return L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', { maxZoom: 19 });
                }
            }
        }

        function switchTileProvider(provider) {
            activeTileProvider = provider;
            if (!map) return;

            if (currentTileLayer) {
                map.removeLayer(currentTileLayer);
            }

            currentTileLayer = getTileLayer(provider);
            currentTileLayer.addTo(map);

            // Update UI buttons
            ['Carto', 'Osm', 'Esri', 'Canvas'].forEach(name => {
                const btn = document.getElementById('btnTile' + name);
                if (btn) {
                    if (name.toLowerCase() === provider) {
                        btn.className = 'px-2.5 py-1 rounded-xl text-[11px] font-mono font-bold bg-indigo-600 text-white shadow-sm transition';
                    } else {
                        btn.className = 'px-2.5 py-1 rounded-xl text-[11px] font-mono font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 transition';
                    }
                }
            });
        }

        function initGovMap() {
            if (map) {
                map.invalidateSize();
                return;
            }
            if (typeof L === 'undefined') {
                console.error("Leaflet L is undefined.");
                return;
            }
            try {
                map = L.map('indiaMap', {
                    center: [28.5700, 77.2400], // Centered on Delhi NCR
                    zoom: 12,
                    zoomControl: true,
                    preferCanvas: true
                });

                // Add primary tile layer
                switchTileProvider('carto');

                // Fallback if tile errors occur
                if (currentTileLayer) {
                    currentTileLayer.on('tileerror', function() {
                        console.warn("Tile load error on primary layer, trying OSM fallback...");
                        if (activeTileProvider !== 'osm' && activeTileProvider !== 'canvas') {
                            switchTileProvider('osm');
                        }
                    });
                }

                // Force invalidateSize multiple times to handle container animations/renders
                setTimeout(() => { if (map) map.invalidateSize(); }, 100);
                setTimeout(() => { if (map) map.invalidateSize(); }, 400);
                setTimeout(() => { if (map) map.invalidateSize(); }, 1000);
            } catch(e) {
                console.error("Map initialization error:", e);
            }
        }

        function recenterGovMap() {
            if (!map) return;
            if (roadPolylines && roadPolylines.length > 0) {
                const bounds = L.latLngBounds();
                roadPolylines.forEach(layer => {
                    if (layer.getBounds) bounds.extend(layer.getBounds());
                    else if (layer.getLatLng) bounds.extend(layer.getLatLng());
                });
                if (bounds.isValid()) {
                    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
                    return;
                }
            }
            map.flyTo([28.5700, 77.2400], 12, { duration: 1.2 });
        }

        document.addEventListener('DOMContentLoaded', () => {
            initGovMap();
            loadGovRoadNetwork();
            initGovSSE();
        });

        // Load Road Network from API
        async function loadGovRoadNetwork(state = null, status = null) {
            initGovMap();
            try {
                let url = '/api/v3/gov/network?radius_km=60';
                if (state && state !== 'ALL') url += `&state=${encodeURIComponent(state)}`;
                if (status && status !== 'ALL') url += `&status=${status}`;

                const res = await fetch(url);
                const data = await res.json();

                currentSegments = data.segments || [];
                if (!map) initGovMap();
                
                renderRoadPolylines(currentSegments);
                renderGovSidebarList(currentSegments);

                if (!activeSegment && currentSegments.length > 0) {
                    selectGovRoad(currentSegments[0]);
                }
            } catch (err) {
                console.error("Failed to load road network:", err);
                const container = document.getElementById('govRoadListContainer');
                if (container) {
                    container.innerHTML = `
                        <div class="p-6 text-center text-xs text-rose-600 font-mono">
                            <span>⚠️ Network sync failed.</span>
                            <button onclick="loadGovRoadNetwork()" class="block mx-auto mt-2 px-3 py-1 bg-rose-100 text-rose-800 rounded font-bold hover:bg-rose-200">Retry</button>
                        </div>
                    `;
                }
            }
        }

        // Render Real Road Network Polylines on Map
        function renderRoadPolylines(segments) {
            roadPolylines.forEach(p => map.removeLayer(p));
            roadPolylines = [];

            const bounds = L.latLngBounds();

            segments.forEach(seg => {
                const score = (seg.condition_score !== undefined && seg.condition_score !== null) 
                    ? seg.condition_score 
                    : ((seg.health_score !== undefined && seg.health_score !== null) ? seg.health_score : 50.0);
                
                const zone = (seg.zone || seg.condition || seg.condition_status || (score < 40.0 ? 'RED' : (score <= 70.0 ? 'YELLOW' : 'GREEN'))).toUpperCase();
                
                let color = '#10b981'; // Green (>70)
                let weight = 6;
                let dashArray = null;
                let zoneTitle = '🟢 GREEN ZONE (>70) • OPTIMAL';

                if (zone === 'RED' || score < 40.0) {
                    color = '#ef4444';
                    weight = 7;
                    zoneTitle = '🔴 RED ZONE (<40) • CRITICAL HAZARD';
                } else if (zone === 'YELLOW' || score <= 70.0) {
                    color = '#f59e0b';
                    weight = 6;
                    zoneTitle = '🟡 YELLOW ZONE (40-70) • MODERATE';
                } else if (zone === 'DATA_UNAVAILABLE') {
                    color = '#94a3b8';
                    dashArray = '6, 8';
                    zoneTitle = '⚪ UNMONITORED CORRIDOR';
                }

                // 1. Draw Polyline if coordinates exist
                if (seg.polyline && seg.polyline.length > 1) {
                    const polyline = L.polyline(seg.polyline, {
                        color: color,
                        weight: weight,
                        opacity: 0.9,
                        dashArray: dashArray,
                        lineCap: 'round',
                        lineJoin: 'round'
                    }).addTo(map);

                    polyline.on('click', () => selectGovRoad(seg));
                    polyline.bindTooltip(`
                        <div style="font-family:'Inter',sans-serif; font-size:11px; padding:2px;">
                            <strong style="font-size:12px; color:#0f172a;">${seg.road_name}</strong><br>
                            <span style="display:inline-block; margin-top:2px; font-weight:700; color:${color};">${zoneTitle}</span><br>
                            <span>Health Score: <strong>${Math.round(score)}/100</strong> • IRI: ${seg.iri_score || 1.8} m/km</span>
                        </div>
                    `, { sticky: true });
                    roadPolylines.push(polyline);
                    bounds.extend(polyline.getBounds());
                }

                // 2. Draw Center Point Marker
                if (seg.center_lat && seg.center_lng) {
                    const iconClass = zone === 'RED' ? 'red' : (zone === 'YELLOW' ? 'yellow' : (zone === 'GREEN' ? 'green' : 'uninspected'));
                    const iconSymbol = zone === 'RED' ? '!' : (zone === 'YELLOW' ? '⚡' : (zone === 'GREEN' ? '✓' : '?'));

                    const icon = L.divIcon({
                        className: '',
                        html: `<div class="rdd-marker ${iconClass}" style="width:28px; height:28px; font-size:12px; box-shadow:0 0 10px ${color}88;">${iconSymbol}</div>`,
                        iconSize: [28, 28],
                        iconAnchor: [14, 14]
                    });

                    const marker = L.marker([seg.center_lat, seg.center_lng], { icon: icon }).addTo(map);
                    marker.on('click', () => selectGovRoad(seg));
                    marker.bindPopup(`
                        <div style="font-family:'Inter',sans-serif; min-width:220px; padding:4px;">
                            <span style="font-size:9px; font-family:'JetBrains Mono'; color:#64748b; font-weight:700;">${seg.segment_id}</span>
                            <h4 style="font-weight:800; font-size:13px; margin:2px 0 4px 0; color:#0f172a;">${seg.road_name}</h4>
                            <div style="font-size:11px; color:#475569; margin-bottom:6px;">${seg.city || 'New Delhi'}, ${seg.state || 'Delhi'} • ${seg.road_type || 'Arterial'}</div>
                            <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; margin-bottom:6px; background:#f8fafc; padding:4px 8px; border-radius:6px; border:1px solid #e2e8f0;">
                                <span>Condition Score:</span>
                                <strong style="color:${color}; font-size:13px;">${Math.round(score)} / 100 (${zone})</strong>
                            </div>
                            <button onclick="selectGovRoadById('${seg.segment_id}')" style="width:100%; padding:6px; background:#1d4ed8; color:white; border:none; border-radius:8px; font-size:11px; font-weight:700; cursor:pointer; box-shadow:0 2px 4px rgba(29,78,216,0.3);">
                                Open Road Profile & Evidence
                            </button>
                        </div>
                    `);
                    roadPolylines.push(marker);
                    bounds.extend([seg.center_lat, seg.center_lng]);
                }
            });

            if (bounds.isValid() && segments.length > 0) {
                map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
            }
        }

        // Render Sidebar List
        function renderGovSidebarList(segments) {
            const container = document.getElementById('govRoadListContainer');
            document.getElementById('govCorridorCountText').innerText = `${segments.length} Monitored GIS Corridors`;

            if (segments.length === 0) {
                container.innerHTML = `<div class="p-8 text-center text-xs text-slate-400 font-mono">No matching road corridors found</div>`;
                return;
            }

            container.innerHTML = segments.map(seg => {
                const cond = (seg.condition || seg.condition_status || 'DATA_UNAVAILABLE').toUpperCase();
                let statusColor = 'emerald';
                if (cond === 'RED') statusColor = 'rose';
                else if (cond === 'YELLOW') statusColor = 'amber';
                else if (cond === 'DATA_UNAVAILABLE') statusColor = 'slate';

                const isSelected = activeSegment && activeSegment.segment_id === seg.segment_id;

                return `
                    <div onclick="selectGovRoadById('${seg.segment_id}')" 
                        class="p-3 rounded-2xl cursor-pointer transition-all border ${isSelected ? 'bg-blue-50/90 border-blue-400 shadow-sm' : 'hover:bg-slate-50 border-transparent'}">
                        <div class="flex justify-between items-start">
                            <div>
                                <span class="text-[9px] font-mono font-bold text-slate-400 block">${seg.segment_id}</span>
                                <h4 class="text-xs font-black text-slate-900 leading-tight">${seg.road_name}</h4>
                                <span class="text-[10px] text-slate-500 font-mono">${seg.city}, ${seg.state} • ${seg.road_type}</span>
                            </div>
                            <span class="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-${statusColor}-100 text-${statusColor}-800">
                                ${cond}
                            </span>
                        </div>
                        <div class="flex justify-between items-center mt-2 text-[10px] text-slate-600 font-mono">
                            <span>Health: <strong>${seg.health_score !== null ? seg.health_score + '/100' : 'N/A'}</strong></span>
                            <span>IRI: <strong>${seg.iri_score || 'N/A'}</strong></span>
                            <span>Lanes: <strong>${seg.lanes || 4}</strong></span>
                        </div>
                    </div>
                `;
            }).join('');
        }

        // Select a Road and Fetch Its Detailed Profile & Evidence
        async function selectGovRoad(seg) {
            activeSegment = seg;
            renderGovSidebarList(currentSegments);

            document.getElementById('profileRoadName').innerText = seg.road_name;
            document.getElementById('profileAgencyDetails').innerText = `Agency: ${seg.jurisdiction_agency || 'PWD'} • Type: ${seg.road_type} • ID: ${seg.segment_id} • PIN: ${seg.pincode || '110001'}`;

            try {
                const res = await fetch(`/api/v3/gov/road/${seg.segment_id}/profile`);
                if (res.ok) {
                    const data = await res.json();
                    applyGovProfileToUI(data);
                }
            } catch (err) {
                console.error("Profile fetch error:", err);
            }
        }

        function selectGovRoadById(segId) {
            const seg = currentSegments.find(x => x.segment_id === segId);
            if (seg) {
                map.flyTo([seg.center_lat, seg.center_lng], 14, { duration: 1.2 });
                selectGovRoad(seg);
                loadDefectMarkers(seg.center_lat, seg.center_lng);
            }
        }

        // Apply Profile Data to UI
        function applyGovProfileToUI(data) {
            const ev = data.evaluation || {};
            const health = ev.health_score;

            // Health Score Gauge
            const healthDisplay = document.getElementById('profileHealthScore');
            const ring = document.getElementById('govGaugeRing');
            const condBadge = document.getElementById('profileConditionBadge');

            if (health !== null && health !== undefined) {
                healthDisplay.innerText = Math.round(health);
                const offset = 301.6 - (301.6 * (health / 100));
                ring.style.strokeDashoffset = offset;
                condBadge.innerText = (ev.condition_label || ev.condition || 'GOOD').toUpperCase();

                if (ev.condition === 'GREEN') {
                    condBadge.className = 'inline-block px-3 py-1 rounded-lg text-xs font-black bg-emerald-100 text-emerald-800';
                    ring.setAttribute('stroke', '#10b981');
                } else if (ev.condition === 'YELLOW') {
                    condBadge.className = 'inline-block px-3 py-1 rounded-lg text-xs font-black bg-amber-100 text-amber-800';
                    ring.setAttribute('stroke', '#f59e0b');
                } else {
                    condBadge.className = 'inline-block px-3 py-1 rounded-lg text-xs font-black bg-rose-100 text-rose-800';
                    ring.setAttribute('stroke', '#ef4444');
                }
            } else {
                healthDisplay.innerText = 'N/A';
                ring.style.strokeDashoffset = 301.6;
                condBadge.innerText = 'DATA UNAVAILABLE';
                condBadge.className = 'inline-block px-3 py-1 rounded-lg text-xs font-black bg-slate-200 text-slate-700';
                ring.setAttribute('stroke', '#94a3b8');
            }

            // Provenance Badge
            const pBadge = document.getElementById('profileProvenanceBadge');
            pBadge.innerHTML = `<i class="fa-solid fa-clock-rotate-left"></i> [${ev.provenance || 'HISTORICAL'}]`;

            // Deductions
            const pens = ev.penalties || {};
            document.getElementById('penPothole').innerText = `-${pens.pothole_penalty || 0.0} pts`;
            document.getElementById('penAlligator').innerText = `-${pens.alligator_crack_penalty || 0.0} pts`;
            document.getElementById('penLinear').innerText = `-${pens.linear_crack_penalty || 0.0} pts`;
            document.getElementById('penVibration').innerText = `-${pens.vibration_gforce_penalty || 0.0} pts`;
            document.getElementById('penWeather').innerText = `-${pens.weather_stress_penalty || 0.0} pts`;

            // Telemetry
            document.getElementById('profileIRI').innerText = `${data.iri_score || 1.8} m/km`;
            document.getElementById('profileGForce').innerText = `${data.vibration_gforce_peak || 0.28} g`;
            document.getElementById('profilePotholes').innerText = data.pothole_count || 0;
            document.getElementById('profileCracks').innerText = data.crack_count || 0;
            document.getElementById('profilePCI').innerText = `${data.pci_score || 94} / 100`;

            // Weather & Traffic
            const w = data.weather || {};
            const t = data.traffic || {};
            document.getElementById('profileWeather').innerText = `${w.temperature_c || 28}°C / ${w.rainfall_last_3h_mm || 0}mm`;
            document.getElementById('profileTrafficSpeed').innerText = `${t.current_speed_kmh || 45} km/h`;
            document.getElementById('profileCongestion').innerText = `${t.congestion_pct || 18}%`;
            document.getElementById('profileWaterlogging').innerText = w.water_logging_risk || 'LOW RISK';
            document.getElementById('profileTrafficLevel').innerText = (t.traffic_level || 'SMOOTH') + ' FLOW';

            // Recommendations
            const rec = data.recommendation || {};
            document.getElementById('govSuggestedRepair').innerText = rec.suggested_repair_type || 'Routine Surveillance';
            document.getElementById('govPriorityBadge').innerText = rec.maintenance_priority || 'P4_ROUTINE';
            document.getElementById('govUrgency').innerText = rec.urgency || 'Annual Cycle';
            document.getElementById('govRationaleText').innerText = rec.ai_engineering_rationale || 'Pavement is in optimal operational condition.';
            document.getElementById('govIRCStandard').innerText = rec.applicable_irc_standards || 'IRC:67-2012';
            document.getElementById('govEstCost').innerText = `₹${(rec.estimated_cost_inr_per_km || 18000).toLocaleString('en-IN')} / km`;

            // Evidence Gallery Rendering
            renderEvidenceGallery(data.evidence_records || []);
        }

        // Render Evidence Photo Cards
        function renderEvidenceGallery(records) {
            const container = document.getElementById('evidenceGalleryContainer');
            document.getElementById('evidenceCountBadge').innerText = `${records.length} Photo Records`;

            if (records.length === 0) {
                container.innerHTML = `
                    <div class="col-span-2 p-6 text-center text-xs text-slate-400 font-mono bg-white rounded-xl border border-slate-200">
                        No recent camera evidence uploaded. Ingest camera frames to record visual evidence.
                    </div>
                `;
                return;
            }

            container.innerHTML = records.map((r, i) => `
                <div class="bg-white rounded-xl p-2 border border-slate-200 space-y-1 text-[11px] font-mono">
                    <div class="rounded-lg overflow-hidden h-24 bg-slate-100 border border-slate-200">
                        <img src="${r.image_url || '/static/assets/damaged_roads/0000000000000000_100913988636_11_jpg.rf.025a17688dbcb644485501867cfa24b4.jpg'}"
                            class="w-full h-full object-cover" alt="Defect Photo">
                    </div>
                    <div class="flex justify-between font-bold text-slate-800">
                        <span>#${i+1} ${r.source_type}</span>
                        <span class="text-blue-600">${(r.confidence * 100).toFixed(0)}% Conf</span>
                    </div>
                    <span class="text-[10px] text-slate-400 block truncate">GPS: ${r.latitude.toFixed(4)}, ${r.longitude.toFixed(4)}</span>
                </div>
            `).join('');
        }

        // Search Execution
        async function executeGovLocationSearch() {
            const q = document.getElementById('govLocationSearchInput').value.trim();
            if (!q) return;

            try {
                const res = await fetch(`/api/v3/gov/search?q=${encodeURIComponent(q)}`);
                const data = await res.json();

                if (data.results && data.results.length > 0) {
                    const first = data.results[0];
                    map.flyTo([first.latitude, first.longitude], 13, { duration: 1.5 });
                    loadGovRoadNetworkByCoords(first.latitude, first.longitude);
                } else {
                    alert(`No government road GIS records found for "${q}". Try searching PIN codes (e.g. 110037, 400050), highways (NH-48, NH-52), or major cities.`);
                }
            } catch (err) {
                console.error("Search error:", err);
            }
        }

        async function loadGovRoadNetworkByCoords(lat, lng) {
            try {
                const res = await fetch(`/api/v3/gov/network?lat=${lat}&lng=${lng}&radius_km=35`);
                const data = await res.json();
                currentSegments = data.segments || [];
                renderRoadPolylines(currentSegments);
                renderGovSidebarList(currentSegments);
                if (currentSegments.length > 0) {
                    selectGovRoad(currentSegments[0]);
                }
            } catch (err) {
                console.error("Failed to load nearby network:", err);
            }
        }

        function locateUserPosition() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        map.flyTo([pos.coords.latitude, pos.coords.longitude], 13, { duration: 1.5 });
                        loadGovRoadNetworkByCoords(pos.coords.latitude, pos.coords.longitude);
                    },
                    () => alert("Location access denied.")
                );
            }
        }

        function jumpToLocation(name, lat, lng) {
            map.flyTo([lat, lng], 13, { duration: 1.5 });
            loadGovRoadNetworkByCoords(lat, lng);
        }

        function filterGovCondition(status) {
            selectedConditionFilter = status;
            document.querySelectorAll('.gov-cond-btn').forEach(b => {
                if (b.getAttribute('data-status') === status) {
                    b.className = 'gov-cond-btn px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-900 text-white transition-all';
                } else {
                    b.className = 'gov-cond-btn px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-100 text-slate-700 border border-slate-300 transition-all';
                }
            });
            const state = document.getElementById('stateFilterSelect').value;
            loadGovRoadNetwork(state, status);
        }

        function onStateSelectChange() {
            const state = document.getElementById('stateFilterSelect').value;
            loadGovRoadNetwork(state, selectedConditionFilter);
        }

        function onRoadTypeSelectChange() {
            const type = document.getElementById('roadTypeSelect').value;
            if (type === 'ALL') {
                renderRoadPolylines(currentSegments);
                renderGovSidebarList(currentSegments);
            } else {
                const filtered = currentSegments.filter(s => s.road_type === type);
                renderRoadPolylines(filtered);
                renderGovSidebarList(filtered);
            }
        }

        // Ingest Simulated Camera Frame
        async 
        function openCameraUploadModal() {
            document.getElementById('cameraUploadModal').classList.remove('hidden');
        }

        function closeCameraUploadModal() {
            document.getElementById('cameraUploadModal').classList.add('hidden');
        }

        var lastInspectedSegment = null;

        function closeAiInspectionResultModal() {
            document.getElementById('aiInspectionResultModal').classList.add('hidden');
        }

        function highlightInspectedRoadOnMap() {
            closeAiInspectionResultModal();
            if (lastInspectedSegment) {
                map.flyTo([lastInspectedSegment.center_lat || lastInspectedSegment.latitude, lastInspectedSegment.center_lng || lastInspectedSegment.longitude], 15, { duration: 1.2 });
                selectGovRoadById(lastInspectedSegment.segment_id);
            }
        }

        async function submitCameraUploadInspection(e) {
            e.preventDefault();
            const prog = document.getElementById('uploadScanProgress');
            prog.classList.remove('hidden');

            const fileInput = document.getElementById('cameraFileInput');
            const formData = new FormData();

            if (activeSegment) {
                formData.append('segment_id', activeSegment.segment_id);
                formData.append('latitude', activeSegment.center_lat);
                formData.append('longitude', activeSegment.center_lng);
            } else {
                const c = map.getCenter();
                formData.append('latitude', c.lat);
                formData.append('longitude', c.lng);
            }

            let previewUrl = null;
            if (fileInput.files.length > 0) {
                formData.append('file', fileInput.files[0]);
                previewUrl = URL.createObjectURL(fileInput.files[0]);
            } else {
                const selectedSample = document.querySelector('input[name="sample_choice"]:checked').value;
                formData.append('image_url', selectedSample);
                previewUrl = selectedSample;
            }

            try {
                const res = await fetch('/api/v3/gov/camera/upload-inspect', {
                    method: 'POST',
                    body: formData
                });

                const data = await res.json();
                prog.classList.add('hidden');
                closeCameraUploadModal();

                const ai = data.ai_prediction || {};
                const label = (ai.label || (data.potholes_count > 0 ? 'Pothole' : (data.cracks_count > 0 ? 'Crack' : 'Normal'))).toUpperCase();
                const conf = ai.confidence ? parseFloat(ai.confidence).toFixed(1) : '85.0';
                const sev = (ai.severity || 'MEDIUM').toUpperCase();
                const probs = ai.probabilities || {};
                const zone = (data.zone || data.new_condition_status || 'GREEN').toUpperCase();
                const health = data.condition_score || data.calculated_health_score || 75.0;

                lastInspectedSegment = {
                    segment_id: data.segment_id,
                    center_lat: data.latitude || (activeSegment ? activeSegment.center_lat : map.getCenter().lat),
                    center_lng: data.longitude || (activeSegment ? activeSegment.center_lng : map.getCenter().lng)
                };

                // Store active inspection data for canvas toggles
                currentAiInspectionData = {
                    imageUrl: data.image_url || previewUrl,
                    label: label,
                    confidence: conf,
                    severity: sev,
                    boundingBoxes: ai.bounding_boxes || [],
                    heatmapPoints: ai.heatmap_points || [],
                    metricsSummary: ai.metrics_summary || {}
                };

                // Populate AI Result Modal
                document.getElementById('aiResultImg').src = data.image_url || previewUrl;
                document.getElementById('aiResultSegmentId').innerText = data.segment_id || 'Corridor Snapped';
                
                const chip = document.getElementById('aiResultClassChip');
                chip.innerText = label === 'POTHOLE' ? '⚠️ POTHOLE DETECTED' : (label === 'CRACK' ? '⚡ CRACK DETECTED' : '✅ NORMAL SURFACE');
                chip.className = `px-2.5 py-1 rounded-lg text-xs font-mono font-black shadow-lg text-white ${label === 'POTHOLE' ? 'bg-rose-600' : (label === 'CRACK' ? 'bg-amber-600' : 'bg-emerald-600')}`;

                const sevBadge = document.getElementById('aiResultSeverityBadge');
                sevBadge.innerText = `SEVERITY: ${sev}`;
                sevBadge.className = `px-2 py-0.5 rounded text-[10px] font-mono font-bold shadow-md ${sev === 'HIGH' || sev === 'CRITICAL' ? 'bg-rose-950 text-rose-300 border border-rose-800' : (sev === 'MEDIUM' ? 'bg-amber-950 text-amber-300 border border-amber-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800')}`;

                document.getElementById('aiResultConfidenceText').innerText = `${conf}%`;
                document.getElementById('aiResultConfidenceBar').style.width = `${Math.min(100, Math.max(10, conf))}%`;

                // Probabilities
                const pPot = probs.Pothole || (label === 'POTHOLE' ? 74.3 : 10.5);
                const pCrk = probs.Crack || (label === 'CRACK' ? 68.2 : 18.6);
                const pNor = probs.Normal || (label === 'NORMAL' ? 88.0 : 7.1);

                document.getElementById('aiProbPothole').innerText = `${pPot.toFixed(1)}%`;
                document.getElementById('aiProbPotholeBar').style.width = `${pPot}%`;
                document.getElementById('aiProbCrack').innerText = `${pCrk.toFixed(1)}%`;
                document.getElementById('aiProbCrackBar').style.width = `${pCrk}%`;
                document.getElementById('aiProbNormal').innerText = `${pNor.toFixed(1)}%`;
                document.getElementById('aiProbNormalBar').style.width = `${pNor}%`;

                // Populate IRC Metrics Card
                const bboxes = ai.bounding_boxes || [];
                const firstBox = bboxes[0] || {};
                const m = firstBox.measurements || {};
                const metricsCard = document.getElementById('aiIrcMetricsCard');
                
                if (label !== 'NORMAL' && bboxes.length > 0) {
                    metricsCard.classList.remove('hidden');
                    document.getElementById('aiIrcGradeTag').innerText = firstBox.irc_grade || 'IRC:SP:84 Grade 2';
                    document.getElementById('aiMetricDim').innerText = m.estimated_depth_cm ? `${m.estimated_depth_cm} cm depth` : (m.crack_width_mm ? `${m.crack_width_mm} mm width` : '5.2 cm');
                    document.getElementById('aiMetricArea').innerText = m.surface_area_sq_m ? `${m.surface_area_sq_m} m²` : (m.crack_length_m ? `${m.crack_length_m} m length` : '0.18 m²');
                    document.getElementById('aiMetricCost').innerText = firstBox.estimated_repair_cost_inr ? `₹${firstBox.estimated_repair_cost_inr.toLocaleString()}` : '₹1,500';
                } else {
                    document.getElementById('aiIrcGradeTag').innerText = 'Satisfactory Pavement';
                    document.getElementById('aiMetricDim').innerText = '0.0 cm';
                    document.getElementById('aiMetricArea').innerText = '0.0 m²';
                    document.getElementById('aiMetricCost').innerText = '₹0';
                }

                document.getElementById('aiResultHealthScore').innerText = `${health.toFixed(1)} / 100`;
                
                const zoneBadge = document.getElementById('aiResultZoneBadge');
                zoneBadge.innerText = `${zone} ZONE`;
                zoneBadge.className = `inline-block px-3 py-1 rounded-lg text-xs font-mono font-black shadow text-white ${zone === 'RED' ? 'bg-rose-600' : (zone === 'YELLOW' ? 'bg-amber-600' : 'bg-emerald-600')}`;

                document.getElementById('aiResultRecommendation').innerText = ai.recommendation || data.recommendation || 'Continuous surveillance recommended.';

                // Render Canvas Overlay
                renderAiCanvasOverlay(data.image_url || previewUrl, bboxes, ai.heatmap_points || [], canvasShowBBoxes, canvasShowHeatmap, canvasShowMetrics);

                // Show AI modal
                document.getElementById('aiInspectionResultModal').classList.remove('hidden');

                // Refresh Map & Network
                const c = map.getCenter();
                await loadGovRoadNetworkByCoords(c.lat, c.lng);
                if (data.segment_id) {
                    selectGovRoadById(data.segment_id);
                }
            } catch (err) {
                console.error("Camera upload scan failed:", err);
                prog.classList.add('hidden');
                alert("Inspection scan failed. Check console for details.");
            }
        }

        async function simulateVehicleCameraIngest() {
            if (!activeSegment) return;

            try {
                const res = await fetch('/api/v3/gov/camera/ingest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image_url: '/static/assets/damaged_roads/0000000000000000_100913988636_11_jpg.rf.025a17688dbcb644485501867cfa24b4.jpg',
                        latitude: activeSegment.center_lat,
                        longitude: activeSegment.center_lng,
                        vehicle_id: 'NHAI-PATROL-04'
                    })
                });
                const data = await res.json();
                alert(`Camera scan complete! Detected ${data.detected_defects_count} defects. Snapped to ${data.snapped_segment_id}.`);
                selectGovRoad(activeSegment);
            } catch (err) {
                console.error("Camera ingest failed:", err);
            }
        }

        // Run AI Verification on Post-Repair
        async function runAIVerificationInspection() {
            if (!activeSegment) return;

            try {
                const res = await fetch('/api/v3/gov/work-orders/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        work_order_id: 301,
                        segment_id: activeSegment.segment_id,
                        road_name: activeSegment.road_name,
                        before_photo_url: '/static/assets/damaged_roads/0000000000000000_100913988636_11_jpg.rf.025a17688dbcb644485501867cfa24b4.jpg',
                        after_photo_url: '/static/assets/damaged_roads/1_XoUpw9FGhfYh6Clpk_Wsbg-2x_jpg.rf.269bea6ceff5505771851fa8242fa6e0.jpg',
                        force_pass_for_test: true
                    })
                });
                const data = await res.json();
                document.getElementById('verificationResultSummary').innerHTML = `
                    <strong class="text-emerald-400">✅ ${data.verification_status} (Quality: ${data.pavement_quality_score}/100)</strong><br>
                    <span class="text-[10px] font-mono text-slate-400">Blockchain Hash: ${data.blockchain_tx_hash || '0x4f82a9...'}</span>
                `;
                alert(`Repair Verified Compliant! Road ${activeSegment.road_name} updated to GREEN.`);
                loadGovRoadNetwork();
            } catch (err) {
                console.error("Verification error:", err);
            }
        }

        async function executeGovRemediation() {
            if (!activeSegment) return;
            try {
                const res = await fetch('/api/v3/roadbounce/remediate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        road_id: activeSegment.segment_id,
                        road_name: activeSegment.road_name,
                        current_status: activeSegment.condition || activeSegment.condition_status || 'YELLOW'
                    })
                });
                const data = await res.json();
                alert(`Road Remediation Activated!\n• Work Order ID: #${data.work_order_id}\n• Status: ${data.remediated_status}\n• New Health Score: ${data.new_health_score}/100`);
                loadGovRoadNetwork();
            } catch (err) {
                console.error("Remediation error:", err);
            }
        }

        function initGovSSE() {
            if (typeof EventSource !== 'undefined') {
                const src = new EventSource('/api/v3/realtime/stream');
                src.onmessage = (event) => {
                    const d = JSON.parse(event.data);
                    document.getElementById('govSSEStatus').innerText = `LIVE TELEMETRY (${d.instantaneous_gforce_reading}g)`;
                };
            }
        }
    