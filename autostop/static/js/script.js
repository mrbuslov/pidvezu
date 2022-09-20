/*------------------------------------------------ВЫПАДАЮЩИЙ СЛАЙДЕР ----------------------------------------------------------------------*/

var elem = document.querySelector(".top_slider");
var elem_mobile = document.querySelector(".top_slider_mobile");
var bottom_nav = document.querySelector(".bottom_navigation");
var arr = [0];

window.addEventListener('scroll', ()=>{
    let scrolled = window.scrollY;
    arr.push(scrolled);

    for(let i=arr.length-1; i<=arr.length; i++){
      if(arr[i-1] > arr[i]){
        if(elem){
          elem.classList.remove("hide");
        }
        if(elem_mobile){
          elem_mobile.style.transform = 'translateY(0%)';
        }
        if(bottom_nav){
          bottom_nav.classList.remove('hide_bottom')
        }
      }
      if(arr[i-1] < arr[i]){
        if(elem){
          elem.classList.add("hide");
        }
        if(elem_mobile){
          elem_mobile.style.transform = 'translateY(-100%)';
        }
        if(bottom_nav){
          bottom_nav.classList.add('hide_bottom')
        }
        if(document.querySelector('.locations_search')){
          document.querySelector('.locations_search').style.top = '-60px';
        }
      }        
    }
})

$(document).ready(function () {
  $(document).on("click", "#bottom_search_btn", function () {
    if(document.querySelector('.locations_search').style.top === '0px'){
      document.querySelector('.locations_search').style.top = '-60px';
    }
    else{
      document.querySelector('.locations_search').style.top = '0px';
    }
  });
});

/*------------------------------------------------ route замена маршрута ----------------------------------------------------------------------*/

function getCookie(name) {
  var matches = document.cookie.match(new RegExp(
      "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}


function sortable(rootEl, onUpdate){
  var dragEl;
  
  // Делаем всех детей перетаскиваемыми
  [].slice.call(rootEl.children).forEach(function (itemEl){
      itemEl.draggable = true;
  });
  
  // Функция отвечающая за сортировку
  function _onDragOver(evt){
      evt.preventDefault();
      evt.dataTransfer.dropEffect = 'move';
      
      var target = evt.target;
      if( target && target !== dragEl && target.nodeName == 'LI' ){
          // Сортируем
          rootEl.insertBefore(dragEl, target.nextSibling || target);
      }
  }
  
  // Окончание сортировки
  function _onDragEnd(evt){
      evt.preventDefault();
      
      dragEl.classList.remove('translucent');
      rootEl.removeEventListener('dragover', _onDragOver, false);
      rootEl.removeEventListener('dragend', _onDragEnd, false);

      // Сообщаем об окончании сортировки
      onUpdate(dragEl);
  }
  
  // Начало сортировки
  rootEl.addEventListener('dragstart', function (evt){
      dragEl = evt.target; // Запоминаем элемент который будет перемещать
      
      // Ограничиваем тип перетаскивания
      evt.dataTransfer.effectAllowed = 'move';
      evt.dataTransfer.setData('Text', dragEl.textContent);

      // Пописываемся на события при dnd
      rootEl.addEventListener('dragover', _onDragOver, false);
      rootEl.addEventListener('dragend', _onDragEnd, false);

      setTimeout(function (){
          // Если выполнить данное действие без setTimeout, то перетаскиваемый объект, будет иметь этот класс.
          dragEl.classList.add('translucent');
      }, 0)
  }, false);
}
               
if(document.getElementById('addresses_list')){
  sortable( document.getElementById('addresses_list'), function (item){change_address()});
}
// ---------------------------------- для brief_intro ---------------------
if(document.getElementById('addresses_list_brief_info')){ 
  sortable( document.getElementById('addresses_list_brief_info'), function (item){});
}

// console.log($('.route_addresses li').first().text())
// console.log($('.route_addresses li').last().text())



function change_address(){
  $('.map').css('opacity','0.4')
  $('.route_addresses').css('opacity','0.4')

  var addresses = []; 
  var locations = [];

  $('.addresses_list_li').each(function(){
    addresses.push($(this).children('span').text())
    locations.push($(this).children('input').val())
  })
  
  var li_counter = 0;
  $('.route_addresses li').each(function() {
    console.log(li_counter)
    console.log(addresses[li_counter])
    $(this).children('span').text(addresses[li_counter]);
    li_counter ++;
    if(li_counter === addresses.length){
      li_counter = 0;
    }
  })

  $.ajax({
    url: '/update_addresses_info/',
    type: 'POST',
    headers: { "X-CSRFToken": getCookie("csrftoken") },
    data: {
        'addresses':addresses,
        'locations':locations,
        'slug':$('#route_slug').val()
    },
    dataType: 'json',
    success: function(data){
        $('.map span').html(data['map_html']);
        $('#map_script').html(data['map_script']);
        $.globalEval(data['map_script']);
        $('.map').css('opacity','1')
        $('.route_addresses').css('opacity','1')
    },
    error: function(){
        document.location.reload();
    }
  });
}

// ---------------------------------- profile ---------------------
$(document).ready(function () {
  $(document).on("change", "#id_telegram", function () {
    if (document.getElementById('id_telegram').checked) {
      document.querySelector('.go_to_tel_popup').style.opacity = '1';
      window.setTimeout(function(){document.querySelector('.go_to_tel_popup').style.opacity = '0'}, 2000);
    }
  });
});



/*---------------------- Проверка на то, есть ли запрос на фильтрацию или смена страницы -------------------------------------- */
$(document).ready(function() {
  var url = window.location.href;
  // url.includes('locations_search') || 
  if(url.includes('page=') && !url.includes('page=1')){ 
    document.querySelector('.locations_search').style.display = "none";
    document.querySelector('.index_page_explan').style.display = "none";
  }
});


// ----------------------------------------- Registration --------------------------------------------------

if(document.getElementById('registrationForm')){
  document.getElementById('registrationForm').addEventListener('submit', function(e) { 
    // Проверка телефона
    var phone_number = $( "#phone_number" ).val();
    if(!/^\+?3?8?(0\d{9})$/.exec(phone_number)){
      e.preventDefault();
      if(window.location.pathname.includes('/ru/')){
        $('#phone_error_text').text('Проверьте правильность телефона')
      }
      else{
        $('#phone_error_text').text('Перевірте правильність телефону')
      }
    }
    // Проверка email
    e.preventDefault();
    $.ajax({
      url: '/registration/',
      type: 'GET',
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      data: {
        'email_check':$('#email').val(),
      },
      dataType: 'json',
      success: function(data){
        if(data === 'email_exists'){
          console.log(data)
          if(window.location.pathname.includes('/ru/')){
            $('#email_error_text').text('Такой email уже существует')
          }
          else{
            $('#email_error_text').text('Такий email вже існує')
          }
        }
        else{
          document.getElementById('registrationForm').submit();
        }
      },
      error: function(){
        document.location.reload();
      }
    });
  });
}