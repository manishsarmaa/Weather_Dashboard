let map;

function fetchWeather() {
    let city = document.getElementById("city").value;
    if (!city) {
        alert("Please enter a city name!");
        return;
    }

    fetch(`/weather?city=${city}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Display current weather
            document.getElementById("weather-info").innerHTML = `
                <h2>${data.city}</h2>
                <p>Temperature: ${data.temperature}°C</p>
                <p>Weather: ${data.weather}</p>
                <img src="http://openweathermap.org/img/wn/${data.icon}.png" />
            `;

            // Display 5-day forecast
            let forecastHTML = "<ul>";
            for (let day of data.forecast) {
                forecastHTML += `
                    <li>
                        <strong>${day.date}</strong>: ${day.temp}°C, ${day.weather} 
                        <img src="http://openweathermap.org/img/wn/${day.icon}.png" />
                    </li>
                `;
            }
            forecastHTML += "</ul>";
            document.getElementById("forecast-container").innerHTML = forecastHTML;
       
            // ✅ Corrected lat/lon reference
            updateMap(data.lat, data.lon, data.city);
        })
        .catch(error => console.error("Error fetching weather:", error));
}

function updateMap(lat, lon, city) {
    if (!map) {
        map = L.map('map').setView([lat, lon], 10);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
    } else {
        map.setView([lat, lon], 10);
    }

    // Remove existing markers before adding a new one
    map.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });

    L.marker([lat, lon]).addTo(map)
        .bindPopup(`<b>${city}</b>`)
        .openPopup();
}


