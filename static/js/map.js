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

function enableFeatureClicks(map) {
  map.on("singleclick",function(event) {
    removeMapPopup();
    flist = map.getFeaturesAtPixel(event.pixel);
    if (flist.length) {
      marker = flist[0];
      evt = event.originalEvent;
      popup = $("<div class='map__popup'>"+
                "<a href='"+marker.url+"'>"+
                marker.title+
                "</a></div>")
      popup.css({ top: evt.clientY+window.scrollY, left: evt.clientX+window.scrollX, position: "absolute","z-index": 9999 });
      popup.appendTo(document.body);
      if (evt.clientX > window.innerWidth / 2) {
        popup.css("left",evt.clientX+window.scrollX - popup.width() - 12);
      }
    }
  });
}

/*  icon.red = new OpenLayers.Icon('/images/RedBullet.png',size,offset);
  icon.green = new OpenLayers.Icon('/images/GreenBullet.png',size,offset);
  icon.purple = new OpenLayers.Icon('/images/PurpleBullet.png',size,offset); */

function createIcons() {
  icon = {}
  icon.peak = new ol.style.Style({
    image: new ol.style.Icon({
      opacity: 1,
      scale: 0.20,
      src: '/images/RedBullet.png'
    })
  })
  icon.start = new ol.style.Style({
    image: new ol.style.Icon({
      opacity: 1,
      scale: 0.15,
      src: '/images/RedBullet.png'
    })
  })
  return icon;
}

function processHikeData(json,map,lang) {
  points = []
  icon = createIcons();

  for (const hike_data of json) {
    if (hike_data.start || hike_data.peak) {
      var loc = hike_data.multipath ? hike_data.start : hike_data.peak
      loc ||= hike_data.peak
      var latlon = loc.split(',')
      point = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([latlon[1],latlon[0]])),
              });
      point.title = hike_data.title[lang || 'sl'];
      point.url   = (lang ? "/" + lang : "") + "/hikes/" + hike_data.name.toLowerCase();
      point.icon  = hike_data.multipath ? icon.start : icon.peak;
      points.push(point)
    }
  }
  var layer = new ol.layer.Vector({
                source: new ol.source.Vector({
                  features: points
                }),
                style: function(feature,resolution) {
                  return feature.icon
                }
              });
  map.addLayer(layer);
  enableFeatureClicks(map);
}

function createMap(divname,lat,lon,zoom,lang) {
  v = new ol.View({
    center: ol.proj.fromLonLat([parseFloat(lon),parseFloat(lat)]),
    zoom: zoom});

  map = new ol.Map({
    layers: [
    new ol.layer.Tile({
      source: new ol.source.OSM(),
    }) ],
  target: divname,
  view: new ol.View({
    center: ol.proj.fromLonLat([parseFloat(lon),parseFloat(lat)]),
    zoom: zoom})
  });

  $.getJSON('/data/hikes.json',function(data) {
    processHikeData(data,map,lang)
  });
  return;

  map.addLayer(layer);
  var markers = new OpenLayers.Layer.Markers( "Markers" );
  map.addLayer(markers);

  map.setCenter (getLonLat(lon,lat,map), zoom);
  map.events.register('move',map,removeMapPopup);
}

$(function() {
  map = $("#mapdiv")
  if (map.length) {
    createMap("mapdiv",map.attr("data-lat"),map.attr("data-lon"),map.attr("data-zoom"),map.attr("data-lang"))
  }
});
