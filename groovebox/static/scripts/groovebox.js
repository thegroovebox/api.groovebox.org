var playSong;
(function () {
  'use strict';
  var baseurl = "https://archive.org/download/"

  /*
  @media all and (max-width: 900px) {}
  if (document.documentElement.clientWidth < 900) {}
  */

  playSong = function(concertId, fileId, title, artist) {
    var url = baseurl + concertId + "/" + fileId;
    var src = $('#resultsbox .coverart img').attr('src');
    $('#nowplaying .album-cover img').attr("src", src);
    $('#nowplaying .song-title').text(title);
    $('#nowplaying .song-artist').text(artist);
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
    // Some songs, like mp3, are already in duration of minutes.
    if (seconds.indexOf(':') != -1) {
      return seconds;
    }
    return (Math.floor(seconds / 60) + ((seconds % 60) / 100))
      .toFixed(2).toString().replace('.', ':');
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
    var artist = $this.attr('artist')
    var concertId = $this.attr('concert');
    var songId = $this.attr('song');
    var title = $this.attr('title')
    playSong(concertId, songId, title, artist);
  });

  var getConcert = function(artist, concert, callback) {
    var url = 'api/artists/' + artist + '/concerts/' + concert;
    $.get(url, function(results) {
      callback(results);
    });
  }

  var populateResultsTable = function(results, callback) {
    $("#resultsbox table tbody").empty();
    $("#resultsbox header h1").text(results.creator);
    $("#resultsbox header h2").text(results.title);
    $("#resultsbox .coverart img").attr('src', results.artist.coverArt);
    
    for (var t in results.tracks) {
      var track = results.tracks[t];
      $('#resultsbox table tbody').append(
        '<tr artist="' + results.creator + '" concert="' + results.identifier
          + '" song="' + track.name +'" title="' + track.title + '">'
          +'<td>' + track.track + '</td>'
          +'<td>' + track.title + '</td>'
          +'<td>' + toMinutes(track.length) + '</td>'
          + '</tr>'
      );
    }

    if (!$('#resultsbox').is(':visible')) {
      toggleResultsbox();
    }
  }

  $('#searchbox-header form').submit(function(event) {
    event.preventDefault();
    setTimeout(function () {
      // for demo (until search is done)
      getConcert("ExplosionsInTheSky", "eits2008-03-21.m300.flac16", function(results) {
        populateResultsTable(results);
      });
    }, 300);
    toggleSearchbox();
    if (!$('#resultsbox').is(':visible')) {
      toggleResultsbox();
    }
  });

  /* If album cover is clicked, load its tracks in resultsbox */
  $('.album-cover').on('click', 'button', function() {    
    var $this = $(this);
    setTimeout(function () {
      var artist = $this.attr('artist');
      var concert = $this.attr('concert');
      getConcert(artist, concert, function(results) {
        populateResultsTable(results);
      });
    }, 300);
  });
}());
