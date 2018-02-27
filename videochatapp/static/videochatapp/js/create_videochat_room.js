$(document).ready(function() {

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
        participants['title'] = $(this).find('.conf-title').val();
        participants['starttime']=startime
        participants['endtime']=endtime
        data = {'data': JSON.stringify(participants)}
        $.ajax({
            url: '/videochat/createvideochatroom/',
            type: 'POST',
            headers: {
              'X-CSRFToken': $.cookie('csrftoken')
            },
            dataType:'json',
            processData: false,
            contentType: false,
            beforeSend:function(){
                console.log("beforeSend=>",data);
            },
            data: data,
            success: function (result) {
                console.log(response,'===error response===');
                alert(result['message']);
                window.location.href = "/";
            }
        });
    });
});