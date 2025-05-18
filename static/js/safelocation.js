const showAlert = (message, type) => {
    const alertElement = document.getElementById('alert');
    alertElement.className = `alert ${type}`;
    alertElement.textContent = message;
  };
  
  // Function to update the details on the webpage
  const updateResourceDetails = (resourceType, data) => {
    const nameElement = document.getElementById(`${resourceType}-name`);
    const addressElement = document.getElementById(`${resourceType}-address`);
    const phoneElement = document.getElementById(`${resourceType}-phone`);
  
    if (data) {
      nameElement.textContent = data.name;
      addressElement.textContent = `Address: ${data.address || 'N/A'}`;
      phoneElement.textContent = `Contact: ${data.phone || 'No contact info available'}`;
    } else {
      nameElement.textContent = `No ${resourceType} found nearby.`;
      addressElement.textContent = '';
      phoneElement.textContent = '';
    }
  };
  
  // Fetch nearest police station
  // Function to calculate the distance using Haversine formula (in km)
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Radius of the Earth in km
    const dLat = (lat2 - lat1) * (Math.PI / 180); // Convert degrees to radians
    const dLon = (lon2 - lon1) * (Math.PI / 180); // Convert degrees to radians
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in km
  };
  
  
  
  // Function to add the current location marker
  const addCurrentLocationMarker = (latitude, longitude, map) => {
    const currentLocationIcon = L.icon({
      iconUrl: "/static/img/currentLocation.png", // Example icon
      iconSize: [32, 32],
    });
  
    // Add marker for the current location
    L.marker([latitude, longitude], { icon: currentLocationIcon })
      .addTo(map)
      .bindPopup("You are here")
      .openPopup();
  };
  
  // Fetch nearest police station
  const fetchNearestPoliceStation = async (latitude, longitude, bounds) => {
    const foursquareApiKey = 'fsq3zW62tmq53Q0lM1Z1IGnYJqdyjQfiLcFOERGodmpyDZg='; // Replace with your API key
    const endpoint = `https://api.foursquare.com/v3/places/search`;
    const params = new URLSearchParams({
      query: 'police station',
      ll: `${latitude},${longitude}`,
      radius: 2, // Search within 5km
      limit: 10, // Max results
    });
  
    try {
      const response = await fetch(`${endpoint}?${params}`, {
        headers: {
          Authorization: foursquareApiKey,
        },
      });
  
      if (!response.ok) throw new Error("Failed to fetch data from Foursquare API");
  
      const data = await response.json();
      if (data.results.length === 0) {
        showAlert("No police stations found nearby.", "danger");
        updateResourceDetails('police', null); // Update the webpage with "No Police Station found"
        return;
      }
  
      let nearestStation = null;
      let minDistance = Infinity;
  
      data.results.forEach((place) => {
        const { geocodes, name, location, contact } = place;
        const stationLat = geocodes.main.latitude;
        const stationLon = geocodes.main.longitude;
  
        // Calculate the distance using the Haversine formula
        const distance = calculateDistance(latitude, longitude, stationLat, stationLon);
  
        if (distance < minDistance) {
          minDistance = distance;
          nearestStation = {
            name,
            address: location.formatted_address,
            lat: stationLat,
            lon: stationLon,
            phone: contact && contact.formatted ? contact.formatted : "No contact info available",
          };
        }
      });
  
      if (nearestStation) {
        // Update the webpage with the nearest police station details
        updateResourceDetails('police', nearestStation);
  
        // Add marker for the nearest police station
        const policeIcon = L.icon({
          iconUrl: '/static/img/police-station.png', // Adjust path if needed
          iconSize: [32, 37],
          iconAnchor: [16, 37],
          popupAnchor: [0, -30],
        });
  
        const policeMarker = L.marker([nearestStation.lat, nearestStation.lon], { icon: policeIcon })
          .addTo(map)
          .bindPopup(
            `<b>${nearestStation.name}</b><br>Address: ${nearestStation.address || 'N/A'}<br>Contact: ${nearestStation.phone}`
          )
          .openPopup();
  
        // Extend bounds to include the police station
        bounds.extend(policeMarker.getLatLng());
  
        showAlert(`Nearest Police Station: ${nearestStation.name}`, "success");
      }
    } catch (error) {
      console.error(error);
      showAlert("Error fetching police station data.", "danger");
      updateResourceDetails('police', null); // Update the webpage in case of an error
    }
  };
  
  // Fetch nearest hospital
  const fetchNearestHospital = async (latitude, longitude, bounds) => {
    const foursquareApiKey = 'fsq3zW62tmq53Q0lM1Z1IGnYJqdyjQfiLcFOERGodmpyDZg='; // Replace with your API key
    const endpoint = `https://api.foursquare.com/v3/places/search`;
    const params = new URLSearchParams({
      query: 'hospital',
      ll: `${latitude},${longitude}`,
      radius: 5000, // Search within 5km
      limit: 10, // Max results
    });
  
    try {
      const response = await fetch(`${endpoint}?${params}`, {
        headers: {
          Authorization: foursquareApiKey,
        },
      });
  
      if (!response.ok) throw new Error("Failed to fetch data from Foursquare API");
  
      const data = await response.json();
      if (data.results.length === 0) {
        showAlert("No hospitals found nearby.", "danger");
        updateResourceDetails('hospital', null); // Update the webpage with "No Hospital found"
        return;
      }
  
      let nearestHospital = null;
      let minDistance = Infinity;
  
      data.results.forEach((place) => {
        const { geocodes, name, location, contact } = place;
        const hospitalLat = geocodes.main.latitude;
        const hospitalLon = geocodes.main.longitude;
  
        // Calculate the distance using the Haversine formula
        const distance = calculateDistance(latitude, longitude, hospitalLat, hospitalLon);
  
        if (distance < minDistance) {
          minDistance = distance;
          nearestHospital = {
            name,
            address: location.formatted_address,
            lat: hospitalLat,
            lon: hospitalLon,
            phone: contact && contact.formatted ? contact.formatted : "No contact info available",
          };
        }
      });
  
      if (nearestHospital) {
        // Update the webpage with the nearest hospital details
        updateResourceDetails('hospital', nearestHospital);
  
        // Add marker for the nearest hospital
        const hospitalIcon = L.icon({
          iconUrl: '/static/img/hospital.png', // Adjust path if needed
          iconSize: [32, 37],
          iconAnchor: [16, 37],
          popupAnchor: [0, -30],
        });
  
        const hospitalMarker = L.marker([nearestHospital.lat, nearestHospital.lon], { icon: hospitalIcon })
          .addTo(map)
          .bindPopup(
            `<b>${nearestHospital.name}</b><br>Address: ${nearestHospital.address || 'N/A'}<br>Contact: ${nearestHospital.phone}`
          )
          .openPopup();
  
        // Extend bounds to include the hospital
        bounds.extend(hospitalMarker.getLatLng());
  
        showAlert(`Nearest Hospital: ${nearestHospital.name}`, "success");
      }
    } catch (error) {
      console.error(error);
      showAlert("Error fetching hospital data.", "danger");
      updateResourceDetails('hospital', null); // Update the webpage in case of an error
    }
  };
  
  // Initialize the map
  const map = L.map('map').setView([37.7749, -122.4194], 13); // Default to San Francisco
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  
  const bounds = map.getBounds(); // Get initial map bounds
  
  // Get the user's current location
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;
  
      // Update map center to the user's location
      map.setView([latitude, longitude], 13);
  
      // Add marker for the current location
      addCurrentLocationMarker(latitude, longitude, map);
  
      // Fetch nearest police station and hospital using the user's location
      fetchNearestPoliceStation(latitude, longitude, bounds);
      fetchNearestHospital(latitude, longitude, bounds);
    },
    (error) => {
      console.error("Error getting location", error);
      showAlert("Unable to retrieve your location", "danger");
    }
  );