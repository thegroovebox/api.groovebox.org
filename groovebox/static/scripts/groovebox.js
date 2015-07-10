var playSong;
var tracks = [
  {
    "id": "eits2008-03-21d1t01.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "intro",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "01",
    "length": 36.38
  },
  {
    "id": "eits2008-03-21d1t02.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "First Breath After Coma",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "02",
    "length": 657.53
  },
  {
    "id": "eits2008-03-21d1t03.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "Catastrophe And The Cure",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "03",
    "length": 489.88,
  },
  {
    "id": "eits2008-03-21d1t04.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "The Birth And Death Of The Day",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "04",
    "length": 473.44,
  },
  {
    "id": "eits2008-03-21d1t05.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "Six Days At The Bottom Of The Ocean",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "05",
    "length": 597.36,
  },
  {
    "id": "eits2008-03-21d1t06.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "Greet Death",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "06",
    "length": 588.04
  },
  {
    "id": "eits2008-03-21d1t07.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "It's Natural To Be Afraid",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "07",
    "length": 788.9
  },
  {
    "id": "eits2008-03-21d2t01.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "Your Hand In Mine",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "08",
    "length": 525.48
  },
  {
    "id": "eits2008-03-21d2t02.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "The Only Moment We Were Alone",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "09",
    "length": 669.17
  },
  {
    "id": "eits2008-03-21d2t03.mp3",
    "concert": "eits2008-03-21.m300.flac16",
    "title": "outro",
    "creator": "Explosions in the Sky",
    "album": "2008-03-21 - Great American Music Hall",
    "number": "10",
    "length": 150.84
  }
];

(function () {
  'use strict';
  var baseurl = "https://archive.org/download/"

  /*
  @media all and (max-width: 900px) {}
  if (document.documentElement.clientWidth < 900) {}
  */

  playSong = function(concertId, fileId, uuid) {
    var url = baseurl + concertId + "/" + fileId;
    var src = $('#resultsbox .coverart img').attr('src');
    var track = tracks[uuid];
    $('#nowplaying .album-cover img').attr("src", src);
    $('#nowplaying .song-title').text(track.title);
    $('#nowplaying .song-artist').text(track.creator);
    $('#audio-player source').attr("src", url);
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

  var toMinutes = function(seconds) {
    return (Math.floor(seconds / 60) + ((seconds % 60) / 100)).toFixed(2);
  }

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

  $('#resultsbox').on('click', 'tr td', function() {
    var $this = $(this).closest('tr');
    var song = $this.attr("song");
    var concert = $this.attr("concert");
    var uuid = $this.attr("uuid");
    playSong(concert, song, uuid);
  });

  $('#searchbox-header form').submit(function(event) {
    event.preventDefault();

    setTimeout(function () {
      for (var t in tracks) {
        var track = tracks[t];
        $('#resultsbox table tbody').append(
          '<tr concert="' + track.concert + '" song="' + track.id +'" uuid="' + t + '">'
            +'<td>' + track.number + '</td>'
            +'<td>' + track.title + '</td>'
            +'<td>' + toMinutes(track.length) + '</td>'
            + '</tr>'
        );
      }
    }, 300);

    toggleSearchbox();
    if (!$('#resultsbox').is(':visible')) {
      toggleResultsbox();
    }
  });
}());
