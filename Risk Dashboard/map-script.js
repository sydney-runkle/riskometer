var userLoc, userCoords, userState, myMap;
var userLocInput = window.prompt('Please enter your location', 'San Francisco')
if (userLocInput == null || userLocInput == "") {
  console.log("User cancelled the prompt.")
} else {
    userLoc = userLocInput;
}

//locRequest = fetch(
//    `https://api.opencagedata.com/geocode/v1/json?q=${userLoc}&key=679bf5d7a07e424f9cf7d1649ec8037d`
//).then(
//    data=>data.json()
//).then(inf => {
//    userCoords = inf.results[0].geometry
//    userState = inf.results[0].annotations.FIPS.state
//});

locRequest = async () => {
    var response = await fetch(`https://api.opencagedata.com/geocode/v1/json?q=${userLoc}&key=679bf5d7a07e424f9cf7d1649ec8037d`)
    var info = await response.json()
    userCoords = info.results[0].geometry
    userState = info.results[0].annotations.FIPS.state
    createMap();
}

locRequest();

function createMap() {
    //var myMap = L.map('map').setView([35.739337,-79.241896], 7);
    var myMap = L.map('map').setView([userCoords['lat'],userCoords['lng']], 7);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/light_nolabels/{z}/{x}/{y}.png', {
        maxZoom: 18,
        tileSize: 512,
        zoomOffset: -1,
    }).addTo(myMap);
    
    fetch(
        proxyURL+USCountyLines
    ).then(
        res => res.json()
    ).then(
        data => L.geoJSON(data, {
            style: function(feature) {
                return {color: '#01579b', weight: 2};
            },
            onEachFeature: onEachFeature
        }).addTo(myMap).on('click', Clicker)
    ).catch(
        error => console.log(error)
    )

}


var proxyURL = 'https://cors-anywhere.herokuapp.com/'
var USCountyLines = 'https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_050_00_5m.json'


function onEachFeature(feature, layer) {
    // does this feature have a property named popupContent?
    if (feature.properties && feature.properties.NAME && feature.properties.STATE && feature.properties.COUNTY) {
        var popupContent = '<p>County Name: ' + feature.properties.NAME + ' County' + '<br></br>' + 'FIPS: ' + feature.properties.STATE + feature.properties.COUNTY + '</p>'
        layer.bindPopup(popupContent);
        
        if(feature.properties.STATE === userState) {
            layer.options.fillColor = '#b51238'
        }
    }
}

var FIPS;
var covid_data;
function Clicker(e) {
    console.log(e)
    var popup = e.layer._popup
    var content = popup.getContent()
    console.log(content)
    FIPS = e.layer.feature.properties.STATE + e.layer.feature.properties.COUNTY;
    fetch(
        proxyURL+`https://sheltered-savannah-24023.herokuapp.com/FIPS/${FIPS}`
    ).then(
        res=>res.json()
    ).then(info=> {
        covid_data=info
        console.log(covid_data)
        content = content + `Deaths: ${covid_data['deaths']} <br></br> Cases: ${covid_data['total cases']}`
        popup.setContent(content)
    }
    )
}


// OLD CODE

/*var NCcountyLines = 'https://opendata.arcgis.com/datasets/d192da4d0ac249fa9584109b1d626286_0.geojson'*/

/*fetch(
    NCcountyLines
).then(
    res => res.json()
).then(
    data => L.geoJSON(data).addTo(myMap)
)*/
