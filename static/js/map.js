var map;

if (locations.length > 0) {
  var firstLocation = locations[0];
  map = L.map("map").setView([firstLocation.lat, firstLocation.lon], 13);
} else {
  map = L.map("map").setView([51.505, -0.09], 13);
}

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
}).addTo(map);

var latlngs = locations.map(function (location) {
  return [location.lat, location.lon];
});

// Debugging: Log latlngs to console to check
console.log(latlngs);

if (locations.length > 0) {
  var firstLocationMarker = L.marker([firstLocation.lat, firstLocation.lon])
    .addTo(map)
    .bindPopup("Latitude: " + firstLocation.lat + "<br>Longitude: " + firstLocation.lon)
    .openPopup();
}

if (locations.length > 1) {
  var lastLocation = locations[locations.length - 1];
  L.marker([lastLocation.lat, lastLocation.lon])
    .addTo(map)
    .bindPopup("Latitude: " + lastLocation.lat + "<br>Longitude: " + lastLocation.lon)
    .openPopup();
}

// Create a polyline for all locations
if (locations.length > 1) {
  var polyline = L.polyline(latlngs, { color: "blue", dashArray: "10, 10" }).addTo(map);
  map.fitBounds(polyline.getBounds());
}
