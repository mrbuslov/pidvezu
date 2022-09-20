// var jQueryScript = document.createElement('script');  
// jQueryScript.setAttribute('src','https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js');
// document.head.appendChild(jQueryScript);
flatpickr('#id_departure_time', {
    enableTime:true,
    dateFormat: "d-m-Y H:i",
    disableMobile: true,
    "locale": "ru",
    "minDate": new Date().fp_incr(0)
});
// ----------------------------- Устанавливаем первоначальный вид карты --------------------------------------
var map1 = L.map('map1').setView([49,32], 6);
var map2 = L.map('map2').setView([49,32], 6);
data={};
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map1);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map2);
var gcs = L.esri.Geocoding.geocodeService();

// ----------------------------- Отправляем запрос на поиск города --------------------------------------
$('#search_address_btn1').click(function(e) {
    e.preventDefault();
    address_search('map1');
});
$('#search_address_btn2').click(function(e) {
    e.preventDefault();
    address_search('map2');
});

function address_search(which_map){
    var search_address;
    var search_results;
    if(which_map === 'map1'){
        search_address = document.getElementById("addr_input_1");
        search_results = '#results1';
    }
    else if(which_map === 'map2'){
        search_address = document.getElementById("addr_input_2");
        search_results = '#results2';
    }

    $.getJSON('https://nominatim.openstreetmap.org/search?format=json&limit=5&accept-language=ua&countrycodes=ua&q=' + search_address.value, function(data) { // &accept-language=ru
        var items = [];

        $.each(data, function(key, val) {
            items.push(
                "<li><p class='address_result'>" +
                    "<input type='hidden' value='" + val.lat + ";" + val.lon + ";" + val.type + "'>" +
                val.display_name + "</p></li>"
            );
        });
        $(search_results).empty(); // очищаем старые результаты
        if (items.length != 0) {
            $('<ul/>', {'class': 'address_all_results',html: items.join('')}).appendTo(search_results);
            if(which_map === 'map1'){
                $('#results1').show();
            }
            else if(which_map === 'map2'){
                $('#results2').show();
            }
            $('.leaflet-top').hide();
        } 
        else {
            $('<p>', { html: "Результатов не найдено" }).appendTo(search_results);
            if(which_map === 'map1'){
                $('#results1').show();
            }
            else if(which_map === 'map2'){
                $('#results2').show();
            }
            $('.leaflet-top').hide();
        }
    });
}

var marker1;
var marker2;
map1.on('click', (e)=>{
    gcs.reverse().latlng(e.latlng).run((err, res)=>{
        if(marker1 !== undefined){ // убираем прошлый маркер, если хотим поставить новый
            map1.removeLayer(marker1);
        }
        if(err) return;
        marker1 = new L.marker(res.latlng); // , {draggable:true}
        map1.addLayer(marker1);
        marker1.bindPopup(res['address']['LongLabel']).openPopup();

        data['lat']=res.latlng['lat'];
        data['lon']=res.latlng['lng'];
        
        $('#departure_point').val(res.latlng['lat'] + ',' + res.latlng['lng'])
        var write_address = ''
        if(res['address']['Address'] === ''){
            write_address = res['address']['City'] + ',' + res['address']['Region'];
        }
        else{
            write_address = res['address']['Address'] + ',' + res['address']['City'] + ',' + res['address']['Region'];
        }
        $('#departure_address').val(write_address)
        
        $('#results1').hide();
        $('.leaflet-top').show();
    });
});
map2.on('click', (e)=>{
    gcs.reverse().latlng(e.latlng).run((err, res)=>{
        if(marker2 !== undefined){ // убираем прошлый маркер, если хотим поставить новый
            map2.removeLayer(marker2);
        }
        if(err) return;
        marker2 = new L.marker(res.latlng); // , {draggable:true}
        map2.addLayer(marker2);
        marker2.bindPopup(res['address']['Match_addr']).openPopup();

        data['lat']=res.latlng['lat'];
        data['lon']=res.latlng['lng'];
        
        $('#arrival_point').val(res.latlng['lat'] + ',' + res.latlng['lng'])
        var write_address = ''
        if(res['address']['Address'] === ''){
            write_address = res['address']['City'] + ',' + res['address']['Region'];
        }
        else{
            write_address = res['address']['Address'] + ',' + res['address']['City'] + ',' + res['address']['Region'];
        }
        $('#arrival_address').val(write_address)
        
        $('#results2').hide();
        $('.leaflet-top').show();
    });
});


$(document).ready(function () {
    $(document).on("click", ".address_result", function () {
        if($(this).parent().parent().parent().prop('id') === 'results1'){
            $('#results1').hide();
            $('.leaflet-top').show();

            data = $(this).find('input').val();
            data = data.replace(' ','').split(';')
            chooseAddr(data[0], data[1], data[2], map1)
            chooseAddr(data[0], data[1], data[2], map1) // вызвал второй раз функцию, потому что первый раз одна отправляет Бог знает куда
            marker1 = new L.marker([data[0], data[1]]); // , {draggable:true}
            map1.addLayer(marker1);
            $('#departure_point').val(data[0] + ',' + data[1])
            gcs.reverse().latlng({'lat':data[0],'lng':data[1]}).run((err, res)=>{
                var write_address = ''
                if(res['address']['Address'] === ''){
                    write_address = res['address']['City'] + ',' + res['address']['Region'];
                }
                else{
                    write_address = res['address']['Address'] + ',' + res['address']['City'] + ',' + res['address']['Region'];
                }
                $('#departure_address').val(write_address)
            });
        }
        else{
            $('#results2').hide();
            $('.leaflet-top').show();
            
            data = $(this).find('input').val();
            data = data.replace(' ','').split(';')
            chooseAddr(data[0], data[1], data[2], map2)
            chooseAddr(data[0], data[1], data[2], map2)
            marker2 = new L.marker([data[0], data[1]]); // , {draggable:true}
            map2.addLayer(marker2);
            $('#arrival_point').val(data[0] + ',' + data[1])
            gcs.reverse().latlng({'lat':data[0],'lng':data[1]}).run((err, res)=>{
                var write_address = ''
                if(res['address']['Address'] === ''){
                    write_address = res['address']['City'] + ',' + res['address']['Region'];
                }
                else{
                    write_address = res['address']['Address'] + ',' + res['address']['City'] + ',' + res['address']['Region'];
                }
                $('#arrival_address').val(write_address)
            });
        }
    });
});

function chooseAddr(lat, lng, type, map) {
    var location = new L.LatLng(lat, lng);
    map.panTo(location);
    if (type === 'city' || type === 'administrative') { // https://github.com/osm-search/Nominatim/blob/80df4d3b560f5b1fd550dcf8cdc09a992b69fee0/settings/partitionedtags.def
        map.setZoom(10);
    } else {
        map.setZoom(20); // 13
    }
}

// $('#my_location').click(function() {
//     map1.locate({
//         setView: true,
//         enableHighAccuracy: true
//     })
//     .on('locationfound', function(e) {
//         var marker = new L.marker(e.latlng);
//         marker.addTo(map1);
//         map1.setZoom(30);
//     });
// })

// *-------------------------------- Кликаем вне контейнера с результатами ----------------------
$(document).mouseup(function(e) 
{
    var results1 = $("#results1");
    var results2 = $("#results2");
    if (!results1.is(e.target) && results1.has(e.target).length === 0){
        results1.hide();
        $('.leaflet-top').show();
    }
    if (!results2.is(e.target) && results2.has(e.target).length === 0){
        results2.hide();
        $('.leaflet-top').show();
    }
});

// *-------------------------------- Проверка полей формы добавления ----------------------


function check_add_fields(e){
    if(document.getElementById('id_departure_time')){
        if(document.getElementById('id_departure_time').value == ''){
            e.preventDefault();
            if(window.location.pathname.includes('/ru/')){
                document.getElementById('fields_are_empty_span').textContent = 'времени отправления';
            }
            else{
                document.getElementById('fields_are_empty_span').textContent = 'часу відправлення';
            }
            document.getElementById('fields_are_empty').style.opacity = '1';
            window.setTimeout(function(){document.getElementById('fields_are_empty').style.opacity = '0'}, 1500);
        }
    }
    if(document.getElementById('id_seats_left')){
        if(document.getElementById('id_seats_left').value == ''){
            e.preventDefault();
            if(window.location.pathname.includes('/ru/')){
                document.getElementById('fields_are_empty_span').textContent = 'оставшихся мест';
            }
            else{
                document.getElementById('fields_are_empty_span').textContent = 'решти місць';
            }
            document.getElementById('fields_are_empty').style.opacity = '1';
            window.setTimeout(function(){document.getElementById('fields_are_empty').style.opacity = '0'}, 1500);
        }
    }
    if(document.getElementById('id_content')){
        if(document.getElementById('id_content').value == ''){
            e.preventDefault();
            if(window.location.pathname.includes('/ru/')){
                document.getElementById('fields_are_empty_span').textContent = 'описания';
            }
            else{
                document.getElementById('fields_are_empty_span').textContent = 'опису';
            }
            document.getElementById('fields_are_empty').style.opacity = '1';
            window.setTimeout(function(){document.getElementById('fields_are_empty').style.opacity = '0'}, 1500);
        }
    }
    if(document.getElementById('departure_point')){
        if(document.getElementById('departure_address').value == ''){
            e.preventDefault();
            if(window.location.pathname.includes('/ru/')){document.getElementById('fields_are_empty_span').textContent = 'Отправления';}
            else{document.getElementById('fields_are_empty_span').textContent = 'Відправлення';}
            document.getElementById('fields_are_empty').style.opacity = '1';
            window.setTimeout(function(){document.getElementById('fields_are_empty').style.opacity = '0'}, 1500);
        }
        if(document.getElementById('arrival_address').value == ''){
            e.preventDefault();
            if(window.location.pathname.includes('/ru/')){document.getElementById('fields_are_empty_span').textContent = 'Прибытия';}
            else{document.getElementById('fields_are_empty_span').textContent = 'Прибуття';}
            document.getElementById('fields_are_empty').style.opacity = '1';
            window.setTimeout(function(){document.getElementById('fields_are_empty').style.opacity = '0'}, 1500);
        }
    }
    if(document.getElementById('id_comment')){ // apply
        if(document.getElementById('id_comment').value == ''){
            e.preventDefault();
            if(window.location.pathname.includes('/ru/')){
                document.getElementById('fields_are_empty_span').textContent = 'комментария';
            }
            else{
                document.getElementById('fields_are_empty_span').textContent = 'комментаря';
            }
            document.getElementById('fields_are_empty').style.opacity = '1';
            window.setTimeout(function(){document.getElementById('fields_are_empty').style.opacity = '0'}, 1500);
        }
    }
}

// *-------------------------------- Вешаем обработчик "Enter", ибо мы убрали submit с кнопок ----------------------

var addr_input_1 = document.getElementById('addr_input_1');
var addr_input_2 = document.getElementById('addr_input_2');

addr_input_1.addEventListener("keyup", function(event) {
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) {
        try{
        event.preventDefault();
        $('#search_address_btn1').click();
        return false;
        }
        catch (e) {
            alert(e)
        }
    }
});
addr_input_2.addEventListener("keyup", function(event) {
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) {
        event.preventDefault();
        $('#search_address_btn2').click();
        return false;
    }
});
// *-------------------------------- И смотрим, человек подтвержает форму или же ищет адрес, потому что, нажимая Enter срабатывает submit формы ----------------------
function check_map_inputs(e, which_form){
    if(which_form === 'addForm'){
        if(addr_input_1 === document.activeElement){
            e.preventDefault();
        }
        else if(addr_input_2 === document.activeElement){
            e.preventDefault();
        }
        else{
            check_add_fields(e);
        }
    }
    else if(which_form === 'applyForm'){
        if(addr_input_1 === document.activeElement){
            e.preventDefault();
        }
        else if(addr_input_2 === document.activeElement){
            e.preventDefault();
        }
        else{
            check_add_fields(e);
        }
    }
    else if(which_form === 'passenger_addForm'){
        if(addr_input_1 === document.activeElement){
            e.preventDefault();
        }
        else if(addr_input_2 === document.activeElement){
            e.preventDefault();
        }
        else{
            check_add_fields(e);
        }
    }
}

if(document.getElementById('addForm')){
    document.getElementById('addForm').addEventListener('submit', function(e) {
        check_map_inputs(e,'addForm');
    });
}
if(document.getElementById('passenger_addForm')){
    document.getElementById('passenger_addForm').addEventListener('submit', function(e) {
        check_map_inputs(e,'passenger_addForm');
    });
}
// *-------------------------------- Проверка полей формы подачи заявки ----------------------
if(document.getElementById('applyForm')){
    document.getElementById('applyForm').addEventListener('submit', function(e) {
        check_map_inputs(e,'applyForm');
    });
}
