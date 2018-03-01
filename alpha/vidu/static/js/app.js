var urlTemplate = "https://www.youtube.com/embed/URL?controls=1&autoplay=1&showinfo=0&rel=0&&loop=1&rel=0";
var player;
var videoID;

window.onload = initialize();

function initialize() {
    videoID = youtube_parser(videoURL);
}

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '360',
        width: '640',
        videoId: videoID,
        events: {
            // 'onReady': onPlayerReady,
            // 'onStateChange': onPlayerStateChange
        }
    });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    event.target.playVideo();
}

// 5. The API calls this function when the player's state changes.
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
var done = false;
function onPlayerStateChange(event) {
    // console.log(player.getCurrentTime());
}

function stopVideo() {
    player.stopVideo();
}

document.getElementById("url")
    .addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            submitURL();
        }
    });

document.getElementById("comment")
    .addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            submitComment();
        }
    });

document.getElementById("playback-time")
    .addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            jumpTo();
        }
    });

function submitComment() {
    var comment = document.getElementById("comment").value;
    document.getElementById("comment").value = "";
    var textBox = document.getElementById("text-box");
    var currentTime = formatTime(player.getCurrentTime());
    textBox.textContent = comment + " - " + currentTime;
}


function submitURL() {
    var url = document.getElementById("url").value;
    url = youtube_parser(url);
    document.getElementById("url").value = "";
    var ytplayer = document.getElementById("player");
    var newURL = urlTemplate.replace(/URL/, url);
    ytplayer.setAttribute("src", newURL);
}

function youtube_parser(url) {
    var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
    var match = url.match(regExp);
    return (match && match[7].length == 11) ? match[7] : false;
}

function formatTime(time) {
    time = Math.round(time);

    var minutes = Math.floor(time / 60),
        seconds = time - minutes * 60;

    seconds = seconds < 10 ? '0' + seconds : seconds;

    return minutes + ":" + seconds;
}

function jumpTo() {
    var newTime = document.getElementById("playback-time").value;
    document.getElementById("playback-time").value = "";
    if (isNaN(newTime)) {
        return;
    }
    // Skip video to new time.
    player.seekTo(newTime);
}