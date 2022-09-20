var all_markers = [];
var map;
var gcs;
var this_marker;
var map_loader = '<div id="map_loader">'+
  '<svg viewBox="0 0 100 100">'+
    '<defs>'+
    '<filter id="shadow">'+
      '<feDropShadow dx="0" dy="0" stdDeviation="1.5" '+
        'flood-color="#fc6767"/>'+
    '</filter>'+
    '</defs>'+
    '<circle id="spinner" style="fill:transparent;stroke: #247dc9;stroke-width: 5px;stroke-linecap: round;filter:url(#shadow);" cx="50" cy="50" r="45"/>'+
  '</svg>'+
'</div>';

// ----------------------------------- Функция перевоначального вида карты -------------------------------------------------------

function start_loading_main_map(map, departure_points, slugs_list){
  if($('.leaflet-marker-pane')){
    $('.leaflet-marker-pane').html(""); // убираем предыдущие метки
    $('.leaflet-shadow-pane').html("");
  }; 
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
  try{
    gcs = L.esri.Geocoding.geocodeService();  
  }
  catch(e){
    console.log('gsc error')
    document.location.reload();

    // var s = document.createElement("script");
    // s.type = "text/javascript";
    // s.src = "https://unpkg.com/leaflet@1.7.1/dist/leaflet.js";
    // $("head").append(s);
    // //$('head').append('<link rel="stylesheet" href="https://unpkg.com/esri-leaflet-geocoder@2.3.3/dist/esri-leaflet-geocoder.css"integrity="sha512-IM3Hs+feyi40yZhDH6kV8vQMg4Fh20s9OzInIIAc4nx7aMYMfo+IenRUekoYsHZqGkREUgx0VvlEsgm7nCDW9g=="crossorigin="">')

  }
  
  for(var i=0; i<departure_points.length; i++){
    var this_point_locations = departure_points[i].split(',') 
    marker1 = new L.marker([this_point_locations[0], this_point_locations[1]]); // , {draggable:true}
    map.addLayer(marker1);
    
    all_markers.push(marker1)
    
    $('.leaflet-marker-pane').append('<input type="hidden" value="'+ slugs_list[i] +'">')
    $('.leaflet-marker-pane').append('<input type="hidden" value="'+ this_point_locations[0]+ ','+  this_point_locations[1] +'">')
    $('.leaflet-marker-pane').append('<input type="hidden" value="'+ i +'">')
  }
}
// ----------------------------------- Прокладываем маршрут при клике на метку -------------------------------------------------------

$('body').on('click', '.leaflet-marker-icon', function() {
  $('#main_map').children(":not(#map_loader)").css('opacity', '0.4');
  $('#main_map').append(map_loader);
  $('#map_loader').css('display','block');

  var slug = $(this).next().val();
  var loctns = $(this).next().next().val().split(',');
  var marker_num = $(this).next().next().next().val();

  $.ajax({
    url: '/load_main_map_marker_info/',
    type: 'GET',
    data: {
      'slug':slug,
    },
    dataType: 'json',
    async:true,
    success: function(data){
      $('#main_map').children().css('opacity', '1');
      $('#map_loader').css('display','none');
      // строим карту
      $('#main_map').remove();
      $('.watch_points_map_field').append('<div id="main_map"></div>')
      $('#main_map').append('<span></span>');
      $('head title').after(data['map_header']);
      $('#main_map').html(data['map_html']);
      try{  
        $.globalEval(data['map_script']);
      }
      catch(e){
        console.log(e);
      }

      // $('link[href*="/bootstrap.min.css"]').remove();    // bootstrap портит весь css-стиль, но без него никак, поэтому не убираю 

      // меняем всплывающую подсказку
      $('.awesome-marker-icon-green').click();

      if(data['what_search'] === 'passengers'){
        $('.leaflet-popup-content').html(
          '<div class="marker_popup_text">'+
            '<span class="marker_popup_author">'+
              data['person_name']+
            '</span>'+
            '<a href="'+data['link_to_passenger_ad']+'" class="marker_popup_apply"><img src="/static/img/map_show_route.svg"></a>'+
            '<a href="tel:'+data['phone_number']+'" class="marker_popup_call"><img src="/static/img/map_phone.svg"></a>'+
          '</div>'
        )
      }
      else if(data['what_search'] === 'drivers'){
        $('.leaflet-popup-content').html(
          '<div class="marker_popup_text">'+
            '<span class="marker_popup_author">'+
              data['person_name']+
            '</span>'+
            '<a href="'+data['link_to_apply']+'" class="marker_popup_apply"><img src="/static/img/map_tick.svg"></a>'+
            '<a href="tel:'+data['phone_number']+'" class="marker_popup_call"><img src="/static/img/map_phone.svg"></a>'+
          '</div>'
        )
      }
      // добавляем input hidden после каждой метки
      var departure_points = data['points_list'];
      var slugs_list = data['slugs_list'];
      var i = 0;
      $(".leaflet-marker-icon").each(function() {
        // в обратном порядке, ведь мы добавляем к метке, а не к каждому инпуту метки
        $(this).after('<input type="hidden" value="'+ i +'">');
        $(this).after('<input type="hidden" value="'+ departure_points[i].split(',')[0]+ ','+  departure_points[i].split(',')[1] +'">');
        $(this).after('<input type="hidden" value="'+ slugs_list[i] +'">');
        i++;
      });
    },
    error: function(){
      // document.location.reload();
    }
  });
});


// ----------------------------------- Загружаем карту при нажатии на водителя/пассажира -------------------------------------------------------

$('.watch_points_map_field p').click(function(e) {
  $('.watch_points_map_field').addClass('show_main_map');
  $('#main_map').children(":not(#map_loader)").css('opacity', '0.4');
  $('#main_map').append(map_loader);
  $('#map_loader').css('display','block');
  var what_search_on_map = $(this).parent().children('.what_search_on_map').val();

  $.ajax({
    url: '/load_main_map/',
    type: 'GET',
    data: {
      'what_search_on_map':what_search_on_map,
    },
    dataType: 'json',
    async:true,
    success: function(data){
      $('#main_map').children().css('opacity', '1');
      $('#map_loader').css('display','none');

      if(map == undefined){
        map = L.map('main_map').setView([49,32], 6);
      }
      var departure_points = data['points_list'];
      var slugs_list = data['slugs_list'];
      start_loading_main_map(map, departure_points, slugs_list);
    },
    error: function(){
      document.location.reload();
    }
  });
});
