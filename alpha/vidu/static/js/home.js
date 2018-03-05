var lastUpdateTime = '0';

window.onload = initialize();
window.setInterval(fetchData, 500);

function initialize() {
    console.log("initializing");
    getNewInvitation();
}

function fetchData() {
    console.log("lastUpdateTime: " + lastUpdateTime);
    getNewInvitation();
}

/**
 * get new invitations from database
 */
function getNewInvitation() {
    $.ajax({
        url: url_to_get_invitations,  // defined in room.html
        type: 'GET',
        datatype: 'json',
        data: {
            last_update_time: lastUpdateTime
        },
        success: function (invitations) {
            for (var i = 0; i < invitations.length; i++) {
                lastUpdateTime = getNewUpdateTime(lastUpdateTime, invitations[i]);
                showInvitation(invitations[i]);
            }
            var invitationTable = $("#invitation-table");
            var csrfTokenHTML = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf_token + "'/>"
            invitationTable.append(csrfTokenHTML);

        }
    })
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

function showInvitation(invitation) {
    var invitationTable = $("#invitation-table");
    var newInvitationHTML = "<tr><td><a>" + invitation['name'] + "</a></td>" +
        "<td class='align-middle'>" + invitation['owner'] + "</td>" + "<td class='align-middle'>" +
        "<input onClick='respond_invitation(event)' type='submit' class='btn btn-primary invitation-response' value='Accept' name=" + invitation['room_pk'] + ">" +
        "<input onClick='respond_invitation(event)' type='submit' class='btn btn-danger invitation-response' value='Decline' name=" + invitation['room_pk'] + ">" +
        "" + "</td></tr>";
    invitationTable.append(newInvitationHTML);
}

function respond_invitation(event) {
    event.preventDefault();
    var srcElement = event.srcElement;
    var response = srcElement.value;  // Accept or Decline
    var response_room_pk = srcElement.name;
    respond(response_room_pk, response, srcElement);
}

/**
 * Ajax to send invitation
 */
function respond(responseRoomPK, response, srcElement) {
    $.ajax({
            url: url_to_respond,
            type: 'POST',
            data: {
                room_pk: responseRoomPK,
                response: response,
                csrfmiddlewaretoken: getCSRFToken()
            },
            success: function (json) {
                $(srcElement).closest("tr").remove();
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