// Driver GPS Tracking Engine - Uses HTML5 Geolocation API

let watchId = null;
let simulationInterval = null;
let pingCounter = 0;

function initDriverTracking(config) {
    const { busId, busNumber, routeStops } = config;

    const startBtn = document.getElementById('startTripBtn');
    const endBtn = document.getElementById('endTripBtn');
    const statusText = document.getElementById('driverTripStatus');
    const liveCoords = document.getElementById('driverLiveCoords');
    const pingDisplay = document.getElementById('pingCount');
    const lastPingDisplay = document.getElementById('lastPingTime');
    const accuracyDisplay = document.getElementById('gpsAccuracy');
    const simToggle = document.getElementById('simulationToggle');

    if (!startBtn || !endBtn) return;

    startBtn.addEventListener('click', function () {
        if (simToggle && simToggle.checked) {
            startSimulation(busId, routeStops);
            return;
        }

        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser.');
            return;
        }

        // Disable start, enable end
        startBtn.disabled = true;
        endBtn.disabled = false;
        statusText.innerText = 'TRIP IN PROGRESS (REAL GPS)';
        statusText.className = 'badge bg-success p-2';

        const geoOptions = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        };

        watchId = navigator.geolocation.watchPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const accuracy = position.coords.accuracy;
                const speed = (position.coords.speed ? (position.coords.speed * 3.6) : 0); // Convert m/s to km/h

                sendLocationToBackend(busId, lat, lng, speed, 'RUNNING');

                pingCounter++;
                if (pingDisplay) pingDisplay.innerText = pingCounter;
                if (liveCoords) liveCoords.innerText = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
                if (accuracyDisplay) accuracyDisplay.innerText = `±${accuracy.toFixed(1)}m`;
                if (lastPingDisplay) lastPingDisplay.innerText = new Date().toLocaleTimeString();
            },
            (error) => {
                console.error('GPS Error:', error);
                alert(`GPS Warning: ${error.message}. Ensure location permissions are granted.`);
            },
            geoOptions
        );
    });

    endBtn.addEventListener('click', function () {
        if (watchId !== null) {
            navigator.geolocation.clearWatch(watchId);
            watchId = null;
        }
        if (simulationInterval !== null) {
            clearInterval(simulationInterval);
            simulationInterval = null;
        }

        startBtn.disabled = false;
        endBtn.disabled = true;
        statusText.innerText = 'TRIP ENDED / IDLE';
        statusText.className = 'badge bg-secondary p-2';

        // Notify backend trip completed
        fetch('/api/bus-location', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                bus_id: busId,
                trip_status: 'COMPLETED'
            })
        }).then(res => res.json()).then(data => {
            console.log('Trip ended status sent:', data);
        });
    });
}

function sendLocationToBackend(busId, latitude, longitude, speed, tripStatus) {
    fetch('/api/bus-location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            bus_id: busId,
            latitude: latitude,
            longitude: longitude,
            speed: speed || 25.0,
            trip_status: tripStatus || 'RUNNING'
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Location update response:', data);
    })
    .catch(err => {
        console.error('Failed to send GPS location:', err);
    });
}

// Demo Route Simulator for classroom / seminar testing
function startSimulation(busId, routeStops) {
    const startBtn = document.getElementById('startTripBtn');
    const endBtn = document.getElementById('endTripBtn');
    const statusText = document.getElementById('driverTripStatus');
    const liveCoords = document.getElementById('driverLiveCoords');
    const pingDisplay = document.getElementById('pingCount');
    const lastPingDisplay = document.getElementById('lastPingTime');
    const accuracyDisplay = document.getElementById('gpsAccuracy');

    startBtn.disabled = true;
    endBtn.disabled = false;
    statusText.innerText = 'TRIP IN PROGRESS (ROUTE SIMULATION)';
    statusText.className = 'badge bg-primary p-2';

    if (!routeStops || routeStops.length === 0) {
        alert('No route stops defined for simulation.');
        return;
    }

    let currentStopIdx = 0;
    let step = 0;
    const totalStepsBetweenStops = 10;

    simulationInterval = setInterval(() => {
        const currentStop = routeStops[currentStopIdx];
        const nextStop = routeStops[(currentStopIdx + 1) % routeStops.length];

        const progress = step / totalStepsBetweenStops;
        const lat = currentStop.latitude + (nextStop.latitude - currentStop.latitude) * progress;
        const lng = currentStop.longitude + (nextStop.longitude - currentStop.longitude) * progress;

        sendLocationToBackend(busId, lat, lng, 35.0, 'RUNNING');

        pingCounter++;
        if (pingDisplay) pingDisplay.innerText = pingCounter;
        if (liveCoords) liveCoords.innerText = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
        if (accuracyDisplay) accuracyDisplay.innerText = 'Simulated (Lab Mode)';
        if (lastPingDisplay) lastPingDisplay.innerText = new Date().toLocaleTimeString();

        step++;
        if (step > totalStepsBetweenStops) {
            step = 0;
            currentStopIdx = (currentStopIdx + 1) % routeStops.length;
        }
    }, 2500);
}
