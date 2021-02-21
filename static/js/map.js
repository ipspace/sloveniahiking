function getLonLat(lon,lat,map) {
  return new OpenLayers.LonLat(lon,lat)
      .transform(
        new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
        map.getProjectionObject() // to Spherical Mercator Projection
      );
}

function removeMapPopup() {
  $(".map__popup").remove();
}

function processHikeData(json,map,l_marker,icon,lang) {
  for (const hike_data of json) {
    if (hike_data.start || hike_data.peak) {
      var loc = hike_data.multipath ? hike_data.start : hike_data.peak
      loc ||= hike_data.peak
      var latlon = loc.split(',')

      var hikeicon = hike_data.multipath ? icon.purple : icon.red;
      var hike = new OpenLayers.Marker(getLonLat(latlon[1],latlon[0],map),hikeicon.clone());
      hike.title = hike_data.title[lang || 'sl'];
      hike.url = (lang ? "/" + lang : "") + "/hikes/" + hike_data.name.toLowerCase()
      hike.events.register('mousedown', hike, function(evt) {
        removeMapPopup();
        popup = $("<div class='map__popup'>"+
                  "<a href='"+this.url+"'>"+
                  this.title+
                  "</a></div>")
        popup.css({ top: evt.clientY+window.scrollY, left: evt.clientX+window.scrollX, position: "absolute","z-index": 9999 });
        popup.appendTo(document.body);
        if (evt.clientX > window.innerWidth / 2) {
          popup.css("left",evt.clientX+window.scrollX - popup.width() - 12);
        }
        OpenLayers.Event.stop(evt); });
      l_marker.addMarker(hike);
    }
  }
}

function createMap(divname,lat,lon,zoom,lang) {
  map = new OpenLayers.Map(divname);
  map.addLayer(new OpenLayers.Layer.OSM());

  var markers = new OpenLayers.Layer.Markers( "Markers" );
  map.addLayer(markers);
  var size = new OpenLayers.Size(12,12);
  var offset = new OpenLayers.Pixel(-(size.w/2), -size.h/2);
  var icon = {};
  icon.red = new OpenLayers.Icon('/images/RedBullet.png',size,offset);
  icon.green = new OpenLayers.Icon('/images/GreenBullet.png',size,offset);
  icon.purple = new OpenLayers.Icon('/images/PurpleBullet.png',size,offset);
  $.getJSON('/data/hikes.json',function(data) {
    processHikeData(data,map,markers,icon,lang)
  });

  map.setCenter (getLonLat(lon,lat,map), zoom);
  map.events.register('move',map,removeMapPopup);
}

$(function() {
  map = $("#mapdiv")
  if (map.length) {
    createMap("mapdiv",map.attr("data-lat"),map.attr("data-lon"),map.attr("data-zoom"),map.attr("data-lang"))
  }
});
