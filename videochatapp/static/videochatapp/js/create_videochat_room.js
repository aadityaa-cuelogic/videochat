function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') 
    { 
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function() {
    
    var csrftoken = getCookie('csrftoken');

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
    });

    $('#createconference').on('submit',function(event){
        event.preventDefault();
        var participants = {};
        $('.conference-table-data .participant-details').each(function(k,v){
            var tmpSelector = $(v);
            if(tmpSelector.find('.selected-participant').is(':checked')){
                var tempData = {
                    'id' : tmpSelector.find('.selected-participant').attr('name'),
                    'email' : tmpSelector.find('.selected-participant').val(),
                    'role' : tmpSelector.find('.selected-participant-role').val(),
                }
                participants[tmpSelector.find('.selected-participant').attr('name')] = tempData;
            }
            
        });
        var startime = $('#start-time').val();
        var endtime = $('#end-time').val();
        var data = {}
        participants['starttime']=startime
        participants['endtime']=endtime
        data = {'data': JSON.stringify(participants)}
        $.ajax({
            url: '/videochat/createvideochatroom/',
            data: data,
            dataType: 'json',
            type: 'post',
            success: function (result) {
                alert(result['message']);
                window.location.href = "/";
            }
        });
    });
});