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
        var checkboxes = [];
        $(':checkbox:checked').each(function(i){
            checkboxes[i] = $(this).val();
        });
        if(checkboxes.length === 0){
            alert("please select atleast one checkbox..");
            return false;
        }
        var startime = $('#start-time').val();
        var endtime = $('#end-time').val();
        var validation1 = validate_date_time(startime);
        if(validation1==false){
            return false;
        }
        var validation2 = validate_date_time(endtime);
        if(validation2==false ){
            return false;
        }
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
    validate_date_time = function(input){
        debugger;
        input=input.split(" ");
        time=input[1].split(":");
        hours=time[0];
        minutes=time[1];
        input_date=input[0].split("/");
        input_date=new Date(input_date[0],input_date[1]-1,input_date[2]);
        now=new Date();
        now1=new Date();
        now1.setHours(0,0,0,0)
        getime=now.toLocaleString('en-GB');
        current_hours=now.getHours();
        current_minutes=now.getMinutes();
        if(input_date.valueOf()==now1.valueOf()){
            if(hours<current_hours){
                alert("Enter Future Date and Time.");
                return false;
            }
            if(hours==current_hours){
                if(minutes<current_minutes){
                    alert("Please Select Future Date And Time.");    
                    return false;
                }
            }                      
        }
        else{
            if(input_date<now){
                alert("Please Select Future Date And Time.");
                return false;
            }
        }
        return true;
    }
});