function debounce(fn, delay) {
  var timer = null;
  return function () {
    var context = this, args = arguments;
    clearTimeout(timer);
    timer = setTimeout(function () {
      fn.apply(context, args);
    }, delay);
  };
}

var throttle = function(fn, threshhold, scope) {
  threshhold || (threshhold = 250);
  var last,
  deferTimer;
  return function () {
    var context = scope || this;

    var now = +new Date,
    args = arguments;
    if (last && now < last + threshhold) {
      // hold on to it
      clearTimeout(deferTimer);
      deferTimer = setTimeout(function () {
        last = now;
        fn.apply(context, args);
      }, threshhold);
    } else {
      last = now;
      fn.apply(context, args);
    }
  };
}


var playSong;
(function () {
  'use strict';
  var baseurl = "https://archive.org/download/"

  /*
  @media all and (max-width: 900px) {}
  if (document.documentElement.clientWidth < 900) {}
  */

  var queueSong = function(concertId, fileId, title, artist) {
    $('#playbox #history ul.queue').append(
      '<li artist="' + artist + '" concert="' + concertId
        + '" song="' + fileId +'" title="' + title + '">'
        + '<span class="track-remove"><i class="fa fa-times-circle"></i></span>'
        + '<span class="track-play">' + title + '</span>'
        + '</li>'
    );
  }

  playSong = function(concertId, fileId, title, artist) {
    var url = baseurl + concertId + "/" + fileId;

    //XXX use /api to get metadata coverart
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
    $('#searchbox input').focus();
    if ($('#searchbox').hasClass('open')) {
      $('#searchbox').removeClass('open');
    } else {
      $('#searchbox').addClass('open');
    }
  };

  var toggleResultsbox = function() {
    $('#blur-results').fadeToggle(500);
    if ($('#resultsbox').hasClass('open')) {
      $('#resultsbox').removeClass('open');
    } else {
      $('#resultsbox').addClass('open');
    }
  };

  var toMinutes = function(seconds) {
    // Some songs, like mp3, are already in duration of minutes.
    if (seconds.indexOf(':') != -1) {
      return seconds;
    }
    return (Math.floor(seconds / 60) + ((seconds % 60) / 100))
      .toFixed(2).toString().replace('.', ':');
  }

  var search = function(query, callback) {
    var url = 'api/search?q=' + query;
    $.get(url, function(results) {
    }).done(function(data) {
      if (callback) { callback(data); }
    });
  }

  var getConcert = function(artist, concert, callback) {
    var url = 'api/artists/' + artist + '/concerts/' + concert;
    $.get(url, function(results) {
    }).done(function(data) {
      if (callback) { callback(data); }
    });
  }

  var populateSearchMatches = function(results, callback) {
    $("#searchbox-results ul").empty();
    for (var result in results) {
      for (var artist in results[result]) {
        for (var trackid in results[result][artist]) {
          var track = results[result][artist][trackid];
          $('#searchbox-results ul').append(
            '<li artist="' + artist + '" concert="' + track.concert
              + '" song="' + track.name +'" title="' + track.title + '">'
              + '<h2 class="result-track">' + track.title + '</h2>'
              + '<h3 class="result-artist">' + artist + '</h3>'
              + '</li>'
          );
        }
      }
    }
    if (callback) { callback(); }
  }  

  var populateResultsTable = function(results, callback) {
    $("#resultsbox table tbody").empty();
    $("#resultsbox header h1").text(results.creator);
    $("#resultsbox header h2").text(results.title);
    $("#resultsbox .coverart img").attr('src', results.metadata.coverArt);
    
    for (var t in results.tracks) {
      var track = results.tracks[t];
      $('#resultsbox table tbody').append(
        '<tr artist="' + results.creator + '" concert="' + results.identifier
          + '" song="' + track.name +'" title="' + track.title + '">'
          +'<td class="playable">' + track.track + '</td>'
          +'<td class="playable">' + track.title + '</td>'
          +'<td class="playable">' + toMinutes(track.length) + '</td>'
          +'<td class="track-queue"><i class="fa fa-plus-circle"></i></td>'
          + '</tr>'
      );
    }

    if (!$('#resultsbox').hasClass('open')) {
      toggleResultsbox();
    }
  }

  // On Search
  $('#searchbox-header form').submit(function(event) { event.preventDefault(); });
  $('#searchbox-header form').keyup(debounce(function(event) {
    throttle(function(event) {
      search($('#search-query').val(), function(results) {
        populateSearchMatches(results);
      });
      
      //toggleSearchbox();
      //if (!$('#resultsbox').hasClass('open')) {
      //  toggleResultsbox();
      //}
    }, 400)();
  }, 250));

  $('#blur-search').click(function() {
    if($('#searchbox').hasClass('open')) {
      toggleSearchbox();
    }
  });

  $('#blur-results').click(function() {
    if ($('#resultsbox').hasClass('open')) {
      toggleResultsbox();
    }
  });

  $('#search').click(function() { 
    toggleSearchbox();
  });

  $('#resultsbox').on('click', 'tr td.playable', function() {
    var $this = $(this).closest('tr');
    var artist = $this.attr('artist')
    var concertId = $this.attr('concert');
    var songId = $this.attr('song');
    var title = $this.attr('title')
    playSong(concertId, songId, title, artist);
  });

  /* Play song from queue */
  $('#playbox #history ul.queue')
    .on('click', 'li span.track-play', function() {
      var $this = $(this).closest('li');
      var artist = $this.attr('artist')
      var concertId = $this.attr('concert');
      var songId = $this.attr('song');
      var title = $this.attr('title')
      playSong(concertId, songId, title, artist);
    });

  /* dequeue song*/
  $('#playbox #history ul.queue').on('click', 'li span.track-remove', function() {
      $(this).closest('li').remove();
    });
  
  /* If track '+' clicked in resultsbox, add to queue */
  $('#resultsbox table tbody').on('click', 'tr td.track-queue', function() {
    var $this = $(this).closest('tr');
    var artist = $this.attr('artist')
    var concertId = $this.attr('concert');
    var songId = $this.attr('song');
    var title = $this.attr('title');
    queueSong(concertId, songId, title, artist);
  });

  /* If search result is clicked, play song and/or load concert tracks in resultsbox */
  $('#searchbox-results ul').on('click', 'li', function() {
    var $this = $(this);
    setTimeout(function () {
      var artist = $this.attr('artist');
      var concert = $this.attr('concert');
      getConcert(artist, concert, function(results) {
        toggleSearchbox();
        populateResultsTable(results);
      });
    }, 300);
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
