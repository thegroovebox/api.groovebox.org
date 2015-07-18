
var debounce = function (func, threshold, execAsap) {
  var timeout;

  return function debounced () {
    var obj = this, args = arguments;
    function delayed () {
      if (!execAsap)
        func.apply(obj, args);
      timeout = null;
    };

    if (timeout)
      clearTimeout(timeout);
    else if (execAsap)
      func.apply(obj, args);

    timeout = setTimeout(delayed, threshold || 100);
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

var playSong, stopSong, nextSong, toggleRepeat, queueSong, queueClear;
(function () {
  'use strict';
  var baseurl = "https://archive.org/download/"
  var extractTrack = function($this) {
    return {
      artist: $this.attr('artist'),
      concert: $this.attr('concert'),
      song: $this.attr('song'),
      title: $this.attr('title')
    }
  }

  var req;
  toggleRepeat = function() { queue.repeat = !queue.repeat; }
  var setPosition = function(pos) {
    queue.pos = pos
    $('#playbox #history ul.queue li.selected').removeClass('selected');
    $('#playbox #history ul.queue li').eq(queue.pos).addClass('selected');
  }
  var queue = {
    pos: 0, // the index of the queue
    pop: true, // remove after playing
    repeat: false,
    shuffle: false,
    startover: false,
    length: function() { return $('#playbox #history ul.queue li').length },
    select: setPosition
  };

  /* Returns the track at index within the play queue */
  var getQueueSong = function(index) {
    var $this = $('#playbox #history ul.queue li').eq(index);
    return extractTrack($this);
  }

  nextSong = function() {
    if (queue.repeat) {
      playSong(getQueueSong(queue.pos));      
    }
    queue.select((queue.pos + 1) % queue.length());
    if (queue.pos > 0 || (queue.pos === 0 && queue.startover)) {
      playSong(getQueueSong(queue.pos));
    } else {
      $('#playbox #history ul.queue li.selected').removeClass('selected');
    }
  }

  queueSong = function(track) {
    console.log(track);
    $('#playbox #history ul.queue').append(
      '<li artist="' + track.artist + '" concert="' + track.concert
        + '" song="' + track.song +'" title="' + track.title + '">'
        + '<span class="track-play">' + track.title + '</span>'
        + '<span class="track-remove"><i class="fa fa-times-circle"></i></span>'
        + '</li>'
    );
    return queue.length()-1;
  }

  queueClear = function() {
    stopSong();
    queue.pos = 0;
    $('#playbox #history ul.queue li.selected').removeClass('selected');
    $('#playbox #history ul.queue').empty();
  }

  playSong = function(track) {
    //XXX use /api to get metadata coverart -- open issue    
    var src = $('#resultsbox .coverart img').attr('src');
    var url = baseurl + track.concert + "/" + track.song;
    $('#nowplaying .album-cover img').attr("src", src);
    $('#nowplaying .song-title').text(track.name);
    $('#nowplaying .song-artist').text(track.artist);
    $('#audio-player source').attr("src", url);
    $('#audio-player')[0].pause();
    $('#audio-player')[0].load();
    $('#audio-player')[0].play();
  }

  stopSong = function() {
    $('#audio-player')[0].pause();
    $('#audio-player source').attr("src", "");    
    $('#audio-player')[0].load();
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
    if (isNaN || seconds.indexOf(':') != -1) {
      return seconds;
    }
    return (Math.floor(seconds / 60) + ((seconds % 60) / 100))
      .toFixed(2).toString().replace('.', ':');
  }

  var search = function(query, callback) {
    var url = 'api/search?q=' + query;
    req = $.get(url, function(results) {
    }).done(function(data) {
      if (callback) { callback(data); }
    });
  }

  var getArtist = function(artist, callback) {
    var url = 'api/artists/' + artist;
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
    var artists = results.artists;
    var tracks = results.tracks;
    for (var t in tracks) {
      var track = tracks[t];
      $('#searchbox-results ul').append(
        '<li artist="' + track.artist_id + '" concert="' + track.item_id
          + '" song="' + track.file_id +'" title="' + track.name + '">'
          + '<h2 class="result-track">' + track.name + '</h2>'
          + '<h3 class="result-artist">' + track.artist + '</h3>'
          + '</li>'
      );
    }
    if (callback) { callback(); }
  }

  var populateResultsTable = function(item, callback) {
    $("#resultsbox table tbody").empty();
    $("#resultsbox header h1").text(item.artist);
    $("#resultsbox header h2").text(item.name);
    $("#resultsbox .coverart img").attr('src', item.metadata.coverArt);
    
    for (var t in item.tracks) {
      var track = item.tracks[t];
      $('#resultsbox table tbody').append(
        '<tr artist="' + track.artist + '" concert="' + track.item_id
          + '" song="' + track.file_id +'" title="' + track.name + '">'
          +'<td class="playable">' + track.number + '</td>'
          +'<td class="playable">' + track.name + '</td>'
          +'<td class="playable">' + toMinutes(track.length) + '</td>'
          +'<td class="track-queue"><i class="fa fa-plus-circle"></i></td>'
          + '</tr>'
      );
    }

    if (!$('#resultsbox').hasClass('open')) {
      toggleResultsbox();
    }
  }

  // On search typing
  $('#searchbox-header form').submit(function(event) { event.preventDefault(); });
  $('#searchbox-header form').keyup(debounce(function(event) {
    //if (req) { req.abort(); } 
    search($('#search-query').val(), function(results) {
      populateSearchMatches(results);
    });
  }, 200, true));

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
    var track = extractTrack($this);          
    queue.select(queueSong(track));
    playSong(track);
  });

  /* Play song from queue */
  $('#playbox #history ul.queue')  
    .on('click', 'li span.track-play', function() {
      var $this = $(this).closest('li');
      queue.select($this.index('#playbox #history ul.queue li'));
      playSong(extractTrack($this));
    });

  /* dequeue song*/
  $('#playbox #history ul.queue').on('click', 'li span.track-remove', function() {
    var $this = $(this).closest('li');
    var index = $this.index('#playbox #history ul.queue li');
    $this.remove()

    if (queue.pos === index) {      
      stopSong();
      if(queue.pos === (queue.length()-1)) {
        queue.select(queue.pos % (queue.length()-1));
      }
    } else {
      // if the song is before current queue.pos, update pos
      if (index < queue.pos) {
        queue.select(queue.pos - 1);
      }
    }
  });
 
  /* If track '+' clicked in resultsbox, add to queue */
  $('#resultsbox table tbody').on('click', 'tr td.track-queue', function() {
    var $this = $(this).closest('tr');
    var track = {
      artist: $this.attr('artist'),
      concert: $this.attr('concert'),
      song: $this.attr('song'),
      title: $this.attr('title')
    }
    queueSong(track);
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
