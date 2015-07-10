var playSong;
var tracks = [{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t11.shn",
  "track": "11",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Deal",
  "length": 211.2,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t04.shn",
  "track": "4",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Me & My Uncle",
  "length": 109.57,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd3t07.shn",
  "track": "21",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Shakedown Street",
  "length": 414.72,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd2t03.shn",
  "track": "14",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Looks Like Rain",
  "length": 293.11,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd3t04.shn",
  "track": "18",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Space",
  "length": 258.93,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd2t02.shn",
  "track": "13",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "I Know You Rider",
  "length": 247.46,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd3t06.shn",
  "track": "20",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Around & Around",
  "length": 315.54,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t06.shn",
  "track": "6",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Candyman",
  "length": 234.24,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t03.shn",
  "track": "3",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Banter",
  "length": 25.77,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t01.shn",
  "track": "1",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Jack Straw",
  "length": 229.82,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t10.shn",
  "track": "10",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Saint of Circumstance",
  "length": 230.29,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd3t03.shn",
  "track": "17",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Drums",
  "length": 456.18,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd2t01.shn",
  "track": "12",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "China Cat Sunflower",
  "length": 329.15,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t09.shn",
  "track": "9",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Lost Sailor",
  "length": 262.36,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd3t01.shn",
  "track": "15",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "He's Gone",
  "length": 405.57
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t07.shn",
  "track": "7",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Minglewood Blues",
  "length": 274.1,},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t02.shn",
  "track": "2",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Sugaree",
  "length": 479.72,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd3t05.shn",
  "track": "19",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Wharf Rat",
  "length": 419.89,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd3t02.shn",
  "track": "16",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Jam",
  "length": 312.6,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t08.shn",
  "track": "8",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Tennessee Jed",
  "length": 329.6,
},
{
  "item": "gd79-09-04.sbd.clugston.9452.sbeok.shnf",
  "id": "gd79-09-04Sbdd1t05.shn",
  "track": "5",
  "creator": "Grateful Dead",
  "album": "1979-09-04 - Madison Square Garden",
  "title": "Big River",
  "length": 22.84,
}];

(function () {
  'use strict';
  var baseurl = "https://archive.org/download/"

  /*
  @media all and (max-width: 900px) {}
  if (document.documentElement.clientWidth < 900) {}
  */

  playSong = function(concertId, fileId) {
    $('#audio-player source').attr("src", baseurl + concertId + "/" + fileId);
    $('#audio-player')[0].pause();
    $('#audio-player')[0].load();
    $('#audio-player')[0].play();
  }

  var toggleSearchbox = function() {
    $('#blur-search').fadeToggle(500);
    $('#searchbox').toggle(function() {
      $('#searchbox').height(1000);
      $('#searchbox').animate({'left': '80px'}, function() {
        // $('#searchbox').offset().left
        $('#searchbox input').focus();
      });
    });
  };

  var toggleResultsbox = function() {
    $('#blur-results').fadeToggle(500);
    $('#resultsbox').toggle(function() {
      var left = $('#resultsbox').offset().left;
      $('#resultsbox').animate({'right': '250px'});
    });
  };

  $('.groovy-blur').click(function () {
    if ($('#resultsbox').is(':visible')) {
      toggleResultsbox();
    }
    if($('#searchbox').is(':visible')) {
      toggleSearchbox();
    }
  });

  $('#search').click(function() { 
    toggleSearchbox();
  });

  $('#searchbox-header form').submit(function(event) {
    event.preventDefault();
    toggleSearchbox();
    if (!$('#resultsbox').is(':visible')) {
      toggleResultsbox();
    }
  });
}());
