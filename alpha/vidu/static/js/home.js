/**
 *  Respond invitation
 */
$('.invitation-response').on('click', function (event) {
    event.preventDefault();
    var response = $(this).attr('value');  // Accept or Decline
    var response_room_pk = $(this).attr('name');
    respond(response_room_pk, response);
});

/**
 * Ajax to send invitation
 */
function respond(responseRoomPK, response) {
    $.ajax({
            url: url_to_respond,
            type: 'POST',
            data: {
                room_pk: responseRoomPK,
                response: response,
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