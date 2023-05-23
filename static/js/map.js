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
  icon.biking = new ol.style.Style({
    image: new ol.style.Icon({
      opacity: 1,
      scale: 0.20,
      src: '/images/GreenBullet.png'
    })
  })
  icon.missing = new ol.style.Style({
    image: new ol.style.Icon({
      opacity: 1,
      scale: 0.15,
      src: '/images/GrayBullet.png'
    })
  })
  return icon;
}

function processHikeData(json,map,lang) {
  points = []
  icon = createIcons();
  console.log(map);

  for (const hike_data of json) {
    console.log(hike_data.name)
    if (hike_data.start || hike_data.peak || hike_data.center) {
      var loc = hike_data.multipath ? hike_data.start : hike_data.peak
      loc ||= hike_data.center || hike_data.start
      if (!loc) {
        continue;
      }
      var latlon = loc.split(',')
      point = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([latlon[1],latlon[0]])),
              });

      if (hike_data.type == 'biking') {
        point.title = hike_data.title['en'];
        point.url   = "/en/biking/" + hike_data.name.toLowerCase();
        point.icon  = icon.biking;
      } else {
        point.title = hike_data.title[lang || 'sl'];
        point.url   = (lang && lang != "sl" ? "/" + lang : "") + "/hikes/" + hike_data.name.toLowerCase();
        point.icon  = hike_data.multipath ? icon.start : icon.peak;
      }
      if (!hike_data.description[lang]) {
        point.icon = icon.missing;
      }
      if (point.title) {
        points.push(point)
      }
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
  console.log(map);
  map.addLayer(layer);
  enableFeatureClicks(map);
}

function createRegionMap(divname,lat,lon,zoom,lang) {
  v = new ol.View({
    center: ol.proj.fromLonLat([parseFloat(lon),parseFloat(lat)]),
    zoom: zoom});

  region_map = new ol.Map({
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
    processHikeData(data,region_map,lang)
  });
}

function loadGPXLayer(gpx,color) {
  console.log('creating '+color+' track from '+gpx);
  var gpx_layer = new ol.layer.Vector({
    source: new ol.source.Vector({
      url: gpx,
      format: new ol.format.GPX(),
    }),
    style: new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: color,
        width: 2
      })
    })
  });
  return gpx_layer;
}

function createGPXMap(divname,lat,lon,zoom,gpx) {
  v = new ol.View({
    center: ol.proj.fromLonLat([parseFloat(lon),parseFloat(lat)]),
    zoom: zoom});

  console.log("gpx= "+gpx);
  layers = [ 
    new ol.layer.Tile({
      source: new ol.source.OSM() }) ]
  layers.push(loadGPXLayer(gpx,"red"));

  if (typeof _track === 'object') {
    for (t in _track) {
      tdata = _track[t]
      console.log('track: '+tdata)
      layers.push(loadGPXLayer(tdata.file,tdata.color));
    }
  }

  gpx_map = new ol.Map({
    layers: layers,
    target: divname,
    view: new ol.View({
      center: ol.proj.fromLonLat([parseFloat(lon),parseFloat(lat)]),
      zoom: zoom})
  });
  gpx_map.on("singleclick",function(event) {
    LonLat = ol.proj.toLonLat(event.coordinate)
    console.log(LonLat[1].toFixed(6)+","+LonLat[0].toFixed(6));
  });
}


$(function() {
  map = $("#mapdiv")
  if (map.length) {
    createRegionMap("mapdiv",map.attr("data-lat"),map.attr("data-lon"),map.attr("data-zoom"),map.attr("data-lang"))
  }
  map = $("#mapgpx")
  if (map.length) {
    createGPXMap("mapgpx",map.attr("data-lat"),map.attr("data-lon"),map.attr("data-zoom"),map.attr("data-gpx"))
  }
});
