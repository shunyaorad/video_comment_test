var urlTemplate = "https://www.youtube.com/embed/URL?controls=1&autoplay=1&showinfo=0&rel=0&&loop=1&rel=0";
var player;
var videoID;
var allComments = {};  // {time_tamp : array_of_comments}
var lastPlayingTime = -1;
var lastUpdateTime = '0';

window.onload = initialize();


function initialize() {
    videoID = youtube_parser(videoURL);
    console.log("initializing");
    getNewComments();
}

function fetchData() {
    getNewComments();
    showComments();
    // console.log(allComments);
}

//************************************************
//******** Youtube functions ***********************
//************************************************
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '360',
        width: '640',
        videoId: videoID,
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    window.setInterval(fetchData, 500);
}

// 5. The API calls this function when the player's state changes.
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
var done = false;

function onPlayerStateChange(event) {
    // console.log(player.getCurrentTime());
    // TODO: erase displayed comments, display comments at the new playTime
}

function stopVideo() {
    player.stopVideo();
}

//************************************************
//************************************************

/**
 * Update room asychronusly
 */
$('#update_room').on('submit', function (event) {
    event.preventDefault();
    updateRoom(roomPK);
});

/**
 * Ajax to update room info
 */
function updateRoom(roomPK) {
    $.ajax({
            url: url_to_update_room,
            type: 'POST',
            data: {
                room_pk: roomPK,
                name: $('input#id_name').val(),
                video_url: $('input#id_video_url').val(),
                csrfmiddlewaretoken: getCSRFToken()
            },
            success: function (json) {
                $('.breadcrumb-item.active').first().text(json['name']);
                player.cueVideoById(youtube_parser(json['video_url']));
            },
            error: function (xhr, errmsg, err) {
            }
        }
    )
}


$('#invitation_form').on('submit', function (event) {
    event.preventDefault();
    invite(roomPK);
});

/**
 * Ajax to update room info
 */
function invite(roomPK) {
    var invited_username = $('input#id_username').val();
    $('input#id_username').val("");
    $.ajax({
            url: url_to_invite,
            type: 'POST',
            data: {
                room_pk: roomPK,
                username: invited_username,
                csrfmiddlewaretoken: getCSRFToken()
            },
            success: function (json) {
                alert("Invited " + invited_username);
            },
            error: function (xhr, errmsg, err) {
                alert("Failed to invite " + invited_username);
            }
        }
    )
}

/**
 * Post comment
 */
$('#post_comment').on('submit', function (event) {
    event.preventDefault();
    postComment();
});

/**
 * Ajax to post comment to server
 */
function postComment() {
    var commentField = $('input#id_message');
    var message = commentField.val();
    commentField.val("");
    var currentTime = Math.round(player.getCurrentTime());  // TODO: round is too rough. get more specific time
    // var textBox = $(".text-box").first(); // TODO: select with comment ID
    // var newCommentHTML = "<p>" + message + "</p>";
    // $(newCommentHTML).hide().appendTo(textBox).fadeIn(10, function () {
    //     $(this).delay(3000).fadeOut(1000, function () {
    //         $(this).remove();
    //     });
    // });
    $.ajax({
            url: url_to_post_comment,
            type: 'POST',
            data: {
                room_pk: roomPK,
                message: message,
                time_stamp: currentTime,
                csrfmiddlewaretoken: getCSRFToken()
            },
            success: function (json) {
            },
            error: function (xhr, errmsg, err) {
            }
        }
    )
}

/**
 * get new comments from database
 */
function getNewComments() {
    $.ajax({
        url: url_to_get_comment,  // defined in room.html
        type: 'GET',
        datatype: 'json',
        data: {
            last_comment_update_time: lastUpdateTime,
            roomPK: roomPK
        },
        success: function (comments) {
            for (var i = 0; i < comments.length; i++) {
                lastUpdateTime = getNewUpdateTime(lastUpdateTime, comments[i]);
            }
            updateComments(comments);
        }
    })
}

/**
 * Update comments to show in the post
 * @param comments
 */
function updateComments(comments) {
    for (var i = 0; i < comments.length; i++) {
        allComments[comments[i]['time_stamp']] = comments[i];
    }
}

/**
 * Get new update time based on the Item's created time
 */
function getNewUpdateTime(lastUpdateTime, Item) {
    if (new Date(lastUpdateTime).getTime() < new Date(Item['created_at']).getTime()) {
        return Item['created_at'];
    } else {
        return lastUpdateTime;
    }
}

// TODO: only what to show certain amount of time. Fade away the comments.
function showComments() {
    var currentTime = Math.round(player.getCurrentTime());  // TODO: replace round with something better
    if (lastPlayingTime != currentTime) {
        var commentsToShow = allComments[currentTime];
        if (typeof commentsToShow != 'undefined') {
            console.log(commentsToShow);
            displayCommentsOnScreen(commentsToShow);
            lastPlayingTime = currentTime;
        }
    }
}

// TODO: parse the list of comments. Instead of changing whole textContent.
function displayCommentsOnScreen(commentToShow) {
    // var videoScreen = document.getElementsByClassName("vidtop-content")[0];
    var videoScreen = $("#video-content");
    // console.log(videoScreen);
    var newCommentHTML = "<div class='vid-comment'><p>" +
        commentToShow['message'] + "</p><p>" + commentToShow['created_by'] + "</p></div>";
    videoScreen.append(newCommentHTML);
    $(function () {
        setTimeout('flow()');
    });
}


function flow() {
    $(".vid-comment").animate({
        left: "-100px" // end position TODO: change end position based on the length of comment
    }, 6000, function () {
        $(this).remove();
    })
}

$("#shareable-link-button").on('click', function () {
    copyToClipBoard();
});

function copyToClipBoard() {
    var copyText = document.getElementById("shareable-link");
    copyText.select();
    document.execCommand("Copy");
    alert("Link copied to clipboard!");
}

/**
 * Jump video to specified time
 */
document.getElementById("playback-time")
    .addEventListener("keyup", function (event) {
        if (event.keyCode === 13) {
            jumpTo();
        }
    });


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


/**
 * Get csrf token
 */
function getCSRFToken() {
    var csrftoken = getCookie('csrftoken');
    return csrftoken;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

