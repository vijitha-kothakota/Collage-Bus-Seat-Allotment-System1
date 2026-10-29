// Live Bus Tracking with Leaflet.js, OpenStreetMap, Timetable & Proximity Alerts

let map, busMarker, boardingMarker, routePolyline;
let pollInterval;
let proximityAlertTriggered = false;

// Audio Chime using Web Audio API (works natively in all modern browsers without audio file assets)
function playArrivalChime() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.type = 'sine';
        // Play high two-tone alert chime (880Hz -> 1174Hz)
        oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
        oscillator.frequency.setValueAtTime(1174, audioCtx.currentTime + 0.15); // D6

        gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.6);

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);

        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.6);
    } catch (e) {
        console.log('Web Audio notification note:', e);
    }
}

function initBusMap(config) {
    const { busId, busNumber, studentStop, allStops, initialBusLocation } = config;

    const defaultCenter = studentStop 
        ? [studentStop.latitude, studentStop.longitude] 
        : [14.4137, 77.7126];

    map = L.map('busMap').setView(defaultCenter, 13);

    // OpenStreetMap Tile Layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    const routeCoords = [];

    // Custom Stop Icon
    const stopIcon = L.divIcon({
        className: 'custom-stop-marker',
        html: '<div style="background:#475569;color:#fff;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);">📍</div>',
        iconSize: [26, 26],
        iconAnchor: [13, 26]
    });

    const myStopIcon = L.divIcon({
        className: 'custom-mystop-marker',
        html: '<div style="background:#dc2626;color:#fff;border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-size:16px;border:3px solid #fff;box-shadow:0 3px 10px rgba(220,38,38,0.6);animation:pulse 1.5s infinite;">⭐</div>',
        iconSize: [34, 34],
        iconAnchor: [17, 34]
    });

    // Add all route stops
    if (allStops && allStops.length > 0) {
        allStops.forEach((stop, index) => {
            const isStudentStop = studentStop && stop.id === studentStop.id;
            const marker = L.marker([stop.latitude, stop.longitude], {
                icon: isStudentStop ? myStopIcon : stopIcon
            }).addTo(map);

            const popupContent = `
                <div style="font-family:sans-serif;min-width:150px;">
                    <strong style="color:#b91c1c;">${stop.stop_name}</strong><br>
                    <small class="text-muted">Stop #${index + 1} &bull; Scheduled: <strong>${stop.pickup_time || 'N/A'}</strong></small>
                    ${isStudentStop ? '<br><span class="badge bg-danger mt-1" style="color:white;background:#dc2626;padding:3px 7px;border-radius:4px;font-size:11px;">Your Boarding Stop</span>' : ''}
                </div>
            `;
            marker.bindPopup(popupContent);

            if (isStudentStop) {
                boardingMarker = marker;
            }

            routeCoords.push([stop.latitude, stop.longitude]);
        });

        // Draw Route Polyline
        routePolyline = L.polyline(routeCoords, {
            color: '#b91c1c',
            weight: 5,
            opacity: 0.85,
            dashArray: '6, 6'
        }).addTo(map);
    }

    // Custom Bus Icon
    const busIcon = L.divIcon({
        className: 'custom-bus-marker',
        html: '<div style="background:#f59e0b;color:#1e293b;border-radius:50%;width:44px;height:44px;display:flex;align-items:center;justify-content:center;font-size:24px;border:3px solid #ffffff;box-shadow:0 4px 14px rgba(245,158,11,0.7);">🚌</div>',
        iconSize: [44, 44],
        iconAnchor: [22, 22]
    });

    const initialLat = initialBusLocation ? initialBusLocation.latitude : defaultCenter[0];
    const initialLng = initialBusLocation ? initialBusLocation.longitude : defaultCenter[1];

    busMarker = L.marker([initialLat, initialLng], { icon: busIcon }).addTo(map);
    busMarker.bindPopup(`<strong>${busNumber}</strong><br>Live Tracking Active`);

    if (routeCoords.length > 0) {
        const bounds = L.latLngBounds(routeCoords);
        bounds.extend([initialLat, initialLng]);
        map.fitBounds(bounds, { padding: [40, 40] });
    }

    // Start live updates polling
    updateLocation(busId, studentStop, allStops, busNumber);
    pollInterval = setInterval(() => {
        updateLocation(busId, studentStop, allStops, busNumber);
    }, 3000);
}

function updateLocation(busId, studentStop, allStops, busNumber) {
    fetch(`/api/bus-location/${busId}`)
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            if (data.status === 'success' && data.location) {
                const loc = data.location;
                const newLatLng = [loc.latitude, loc.longitude];

                // Smoothly update bus marker
                busMarker.setLatLng(newLatLng);

                // Telemetry Elements
                const latEl = document.getElementById('liveLat');
                const lngEl = document.getElementById('liveLng');
                const updatedEl = document.getElementById('lastUpdated');
                const speedEl = document.getElementById('liveSpeed');
                const statusBadge = document.getElementById('tripStatusBadge');
                const distanceEl = document.getElementById('distanceToStop');
                const nearestStopEl = document.getElementById('nearestStopName');
                const nearestDistEl = document.getElementById('nearestStopDist');
                const proximityAlertBox = document.getElementById('proximityAlertBanner');
                const alertMessageText = document.getElementById('alertMessageText');

                if (latEl) latEl.innerText = loc.latitude.toFixed(5);
                if (lngEl) lngEl.innerText = loc.longitude.toFixed(5);
                if (updatedEl) updatedEl.innerText = loc.updated_at || 'Just now';
                if (speedEl) speedEl.innerText = (loc.speed || 0).toFixed(1) + ' km/h';

                if (statusBadge) {
                    statusBadge.innerText = loc.trip_status;
                    if (loc.trip_status === 'RUNNING') {
                        statusBadge.className = 'badge bg-success';
                    } else if (loc.trip_status === 'COMPLETED') {
                        statusBadge.className = 'badge bg-secondary';
                    } else {
                        statusBadge.className = 'badge bg-warning text-dark';
                    }
                }

                // 1. Calculate Nearest Stop along the entire route
                if (allStops && allStops.length > 0) {
                    let minStopDist = Infinity;
                    let nearestStop = null;

                    allStops.forEach(stop => {
                        const d = getDistanceFromLatLonInKm(loc.latitude, loc.longitude, stop.latitude, stop.longitude);
                        if (d < minStopDist) {
                            minStopDist = d;
                            nearestStop = stop;
                        }
                    });

                    if (nearestStop && nearestStopEl && nearestDistEl) {
                        nearestStopEl.innerText = nearestStop.stop_name;
                        if (minStopDist < 0.1) {
                            nearestDistEl.innerText = 'At this stop right now!';
                        } else {
                            nearestDistEl.innerText = `${minStopDist.toFixed(2)} km away (${nearestStop.pickup_time})`;
                        }
                    }
                }

                // 2. Proximity Alert for Student's Boarding Stop
                if (studentStop && distanceEl) {
                    const distKm = getDistanceFromLatLonInKm(
                        loc.latitude, loc.longitude,
                        studentStop.latitude, studentStop.longitude
                    );
                    distanceEl.innerText = `${distKm.toFixed(2)} km`;

                    const etaEl = document.getElementById('estimatedArrival');
                    if (etaEl) {
                        if (distKm < 0.1) {
                            etaEl.innerText = 'Arrived at your stop!';
                            etaEl.className = 'badge bg-success fs-6';
                        } else {
                            const etaMinutes = Math.max(1, Math.round((distKm / 30) * 60));
                            etaEl.innerText = `~${etaMinutes} mins`;
                            etaEl.className = 'badge bg-primary fs-6';
                        }
                    }

                    // TRIGGER PROXIMITY ALERT if bus is within 1.2 KM of student's stop and running!
                    if (distKm <= 1.2 && loc.trip_status === 'RUNNING') {
                        if (proximityAlertBox) {
                            proximityAlertBox.classList.remove('d-none');
                            if (alertMessageText) {
                                alertMessageText.innerHTML = `
                                    <strong>🚨 BUS APPROACHING ALERT:</strong> 
                                    Bus <strong>${busNumber}</strong> is only <strong>${distKm.toFixed(2)} km</strong> away from your boarding stop (<strong>${studentStop.stop_name}</strong>)! 
                                    Expected arrival in <strong>~${Math.max(1, Math.round((distKm / 30) * 60))} minute(s)</strong>. Please be at your stop!
                                `;
                            }
                        }

                        // Play audio chime once when entering proximity radius
                        if (!proximityAlertTriggered) {
                            playArrivalChime();
                            proximityAlertTriggered = true;
                        }
                    } else {
                        if (proximityAlertBox && distKm > 1.5) {
                            proximityAlertBox.classList.add('d-none');
                            proximityAlertTriggered = false;
                        }
                    }
                }
            }
        })
        .catch(err => {
            console.error('Error fetching live bus coordinates:', err);
        });
}

function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

function deg2rad(deg) {
    return deg * (Math.PI / 180);
}
