// Initialising Map
mapboxgl.accessToken = "pk.eyJ1Ijoic2Fpa2h1cmFuYSIsImEiOiJja28zZWwwY3QwMTJ3MnhteThjbG5sYjgyIn0.i85hqRoHATrcR6mv8_SAgw";
let map = new mapboxgl.Map({
    container: "map",
    style: "mapbox://styles/mapbox/streets-v11",
    center: [103.8231710722673,1.3044487772620454],
    zoom: 7.5
});


map.on('load', () => {
    map.addControl(new mapboxgl.NavigationControl());
    map.addControl(new mapboxgl.FullscreenControl());
    map.loadImage('https://docs.mapbox.com/mapbox-gl-js/assets/custom_marker.png',
        (error, image) => {
            if (error) throw error;
            map.addImage('custom-marker', image);
        },
    )

    addMapSource([...singapore.ratings,...singapore.polarity]);
    addMapSource([...klumpur.ratings,...klumpur.polarity]);
    addMapSource([...bangkok.ratings,...bangkok.polarity]);

});


// Navbar Controls
const singaporeId = document.getElementById("nav-singapore");
const klumpurId = document.getElementById("nav-klumpur");
const bangkokId = document.getElementById("nav-bangkok");

/* <a href="#" class="list-group-item list-group-item-action flex-column align-items-start">
    <div class="d-flex w-100 justify-content-between">
        <h5 class="mb-1">List group item heading</h5>
    </div>
    <small class="text-muted">Donec id elit non mi porta.</small>
    </a> */

const hotelList = document.getElementById("hotel-list");
const hotels = document.getElementsByClassName("hotel");
const ratingCheck = document.getElementById("rating-check");
const polarityCheck = document.getElementById("polarity-check");

let selected_hotel_element;
let selected_city_code = "singapore";

const addHotelListClickListeners = () => {
    for (const hotel of hotels) {
        // console.log(hotel);
        hotel.addEventListener("click", (event) => {
            // console.log(hotels);
            $(selected_hotel_element).removeClass("active")
            $(event.target).addClass("active");
            selected_hotel_element = event.target
            flyToMap([event.target.getAttribute("data-lang"), event.target.getAttribute("data-lit")],16)
        });
    }
}


const onScoringMechanismChange = async () => {
    if (ratingCheck.checked) {
        await updateHotelList(selected_city_code, eval(selected_city_code).ratings)
    } else {
        await updateHotelList(selected_city_code, eval(selected_city_code).polarity)

    }
    addHotelListClickListeners();
}

ratingCheck.addEventListener("click",onScoringMechanismChange)
polarityCheck.addEventListener("click",onScoringMechanismChange)






const updateHotelList = (city_name, hotel_array) => {

    return new Promise((resolve, reject) => {
        
        try {
            hotelList.innerHTML = "";
            for (const i in hotel_array) {
                hotelList.innerHTML += `
                <a data-hotel="${i}" data-lang="${hotel_array[i].coordinates[0]}" data-lit="${hotel_array[i].coordinates[1]}" data-location="${city_name}" href="#" class="hotel list-group-item list-group-item-action flex-column align-items-start">
                    <div data-hotel="${i}" data-lang="${hotel_array[i].coordinates[0]}" data-lit="${hotel_array[i].coordinates[1]}" data-location="${city_name}" class="d-flex w-100 justify-content-between">
                        <h5 data-hotel="${i}" data-lang="${hotel_array[i].coordinates[0]}" data-lit="${hotel_array[i].coordinates[1]}" data-location="${city_name}" class="mb-1">${hotel_array[i].hotel_name}</h5>
                    </div>
                    <small data-hotel="${i}" data-lang="${hotel_array[i].coordinates[0]}" data-lit="${hotel_array[i].coordinates[1]}" data-location="${city_name}" class=""> Rating: ${hotel_array[i].hotel_rating}/10 &emsp; Polarity: ${hotel_array[i].scaled_polarity.toFixed(2)}/10 </small>
                </a>`;
            }
            resolve()
        } catch (error) {
            reject(error)
        }
    })
}




const flyToMap = (coordinates,_zoom) => {
    map.flyTo({
        // These options control the ending camera position: centered at
        // the target, at zoom level 9, and north up.
        center: coordinates,
        zoom: _zoom,
        bearing: 0,

        // These options control the flight curve, making it move
        // slowly and zoom out almost completely before starting
        // to pan.
        speed: 1.5, // make the flying slow
        curve: 1, // change the speed at which it zooms out

        // This can be any easing function: it takes a number between
        // 0 and 1 and returns another number between 0 and 1.
        easing: function (t) {
            return t;
        },

        // this animation is considered essential with respect to prefers-reduced-motion
        essential: true
    });

}
const flyToCity = (city_code) => {

    const cityCoordinates = {
        "singapore":[103.8231710722673,1.3044487772620454],
        "klumpur":[101.7113406511777,3.1566490021471934],
        "bangkok":[100.56497759539877,13.73488495334769]
    }

    flyToMap(cityCoordinates[city_code],10);
}



const addMapSource = (hotelList) => {

    let features = []
    hotelList.forEach(hotel => {
        features.push({
            // feature for Mapbox DC
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': hotel.coordinates
            },
            'properties': {
                'title': hotel.hotel_name
            }
        })
    });


    const randomString = Math.random().toString(36).substring(5);


    map.addSource(randomString, {
        'type': 'geojson',
        'data': {
            'type': 'FeatureCollection',
            'features': features
        }
    });


    try {
        map.addLayer({
            'id': randomString,
            'type': 'symbol',
            'source': randomString,
            'layout': {
                'icon-image': 'custom-marker',
                // get the title name from the source's "title" property
                'text-field': ['get', 'title'],
                'text-font': [
                    'Open Sans Semibold',
                    'Arial Unicode MS Bold'
                ],
                'text-offset': [0, 1.25],
                'text-anchor': 'top'
            }
        })
    } catch (error) {
    }

}
const titleHeading = document.getElementById("list-heading")

singaporeId.addEventListener("click", async () => {
    selected_city_code = "singapore"
    flyToCity(selected_city_code);
    if (ratingCheck.checked) {
        titleHeading.innerText = "Top 10 Hotels in Singapore: (bassed on eCommerce Website Rating)";  
        await updateHotelList("singapore", singapore.ratings)
    } else {
        titleHeading.innerText = "Top 10 Hotels in Singapore: (bassed on Polarity Score)";  
        await updateHotelList("singapore", singapore.polarity)
    }
    addHotelListClickListeners();
});

klumpurId.addEventListener("click", async () => {
    selected_city_code = "klumpur"
    flyToCity(selected_city_code)
    if (ratingCheck.checked) {
        titleHeading.innerText = "Top 10 Hotels in Kuala Lumpur: (bassed on eCommerce Website Rating)";  
        await updateHotelList("klumpur", klumpur.ratings)
    } else {
        titleHeading.innerText = "Top 10 Hotels in Kuala Lumpur: (bassed on Polarity Score)";  
        await updateHotelList("klumpur", klumpur.polarity)
    }
    addHotelListClickListeners();
});

bangkokId.addEventListener("click", async () => {
    selected_city_code = "bangkok"
    flyToCity(selected_city_code)
    if (ratingCheck.checked) {
        titleHeading.innerText = "Top 10 Hotels in Bangkok: (bassed on eCommerce Website Rating)";  
        await updateHotelList("bangkok", bangkok.ratings)
    } else {
        titleHeading.innerText = "Top 10 Hotels in Bangkok: (bassed on Polarity Score)";  
        await updateHotelList("bangkok", bangkok.polarity)
    }
    addHotelListClickListeners();
});

singaporeId.click();