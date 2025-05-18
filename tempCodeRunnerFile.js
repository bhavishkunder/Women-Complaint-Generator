const fetch = require('node-fetch');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function geocode(address) {
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`;
  const response = await fetch(url);
  const data = await response.json();
  if (data.length === 0) throw new Error('Location not found');
  return {
    latitude: parseFloat(data[0].lat),
    longitude: parseFloat(data[0].lon),
    display_name: data[0].display_name
  };
}

async function findNearbyPoliceStations(lat, lon) {
  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="police"](around:5000,${lat},${lon});
      way["amenity"="police"](around:5000,${lat},${lon});
      relation["amenity"="police"](around:5000,${lat},${lon});
    );
    out body;
    >;
    out skel qt;
  `;

  const response = await fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query
  });
  const data = await response.json();
  return data.elements.filter(element => element.type === 'node');
}

function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radius of the Earth in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const distance = R * c;
  return distance * 1000; // Convert to meters
}

async function main() {
  try {
    const address = await new Promise(resolve => {
      rl.question('Enter your location (e.g., "New York City" or "London, UK"): ', resolve);
    });

    console.log("Geocoding your location...");
    const location = await geocode(address);
    console.log(`Your location: ${location.display_name}`);
    console.log(`Coordinates: ${location.latitude}, ${location.longitude}\n`);

    console.log("Searching for nearby police stations...");
    const stations = await findNearbyPoliceStations(location.latitude, location.longitude);

    if (stations.length > 0) {
      console.log("Nearby police stations:");
      stations.forEach((station, index) => {
        const distance = calculateDistance(location.latitude, location.longitude, station.lat, station.lon);
        console.log(`${index + 1}. ${station.tags.name || 'Unnamed Police Station'}`);
        console.log(`   Coordinates: ${station.lat}, ${station.lon}`);
        console.log(`   Distance: ${distance.toFixed(0)} meters`);
        console.log('---');
      });
    } else {
      console.log("No police stations found within 5km of the specified location.");
    }
  } catch (error) {
    console.error('An error occurred:', error.message);
  } finally {
    rl.close();
  }
}

main();