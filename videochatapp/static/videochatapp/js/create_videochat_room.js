function setDefaultPrivilegeOp(_this){
    var default_privileges = _this.find('option:selected').attr('defaultprivileges');
    default_privileges = eval(default_privileges);
    _this.closest('.participant-details').find('.selected-participant-privilege option').prop('disabled', false);
    default_privileges.forEach(function(key,value){
        _this.closest('.participant-details').find('.selected-participant-privilege option[value="'+key+'"]').prop('disabled', true);
    });
};

function setDefaultPrivilege(){
    $('.selected-participant-role').each(function(k,v){
        setDefaultPrivilegeOp($(v));
    });
};

$(document).ready(function() {
    
    // called to set for default selction
    // setDefaultPrivilege();

    $('.selected-participant-role').on('change', function(e){
        var _this = $(this);
        setDefaultPrivilegeOp(_this);
    });

    // called on edit conference form submit
    $('#editconference').on('submit',function(event){
        event.preventDefault();
        var _this = $(this);
        var confereceroomid = _this.find('#create-bt').attr('rel');
        if (confereceroomid){
            var participants = {};
            participants['confereceroomid'] = confereceroomid;
            if(_this.find('#create-bt').data('user_listing_privilege') == 'True'){
                // check if user_add_remove_privilege
                $('.conference-table-data .participant-details').each(function(k,v){
                    var tmpSelector = $(this);
                    if(tmpSelector.find('.selected-participant').is(':checked')){
                        var tempData = {
                            'id' : tmpSelector.find('.selected-participant').attr('name'),
                            'email' : tmpSelector.find('.selected-participant').val(),
                            'role' : tmpSelector.find('.selected-participant-role').val(),
                            'special_privilege' : tmpSelector.find('.selected-participant-privilege').val()
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
            }
            if(_this.find('#create-bt').data('event_schedule_privilege') == 'True'){
                // check if event_schedule_privilege
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
                participants['title'] = _this.find('.conf-title').val();
                participants['starttime']=startime
                participants['endtime']=endtime
            }
            var data = {}
            data = {'data': JSON.stringify(participants)}
            $.ajax({
                url: '/videochat/'+confereceroomid+'/editconference/',
                type: 'POST',
                headers: {
                  'X-CSRFToken': $.cookie('csrftoken')
                },
                dataType:'json',
                beforeSend:function(){
                    console.log("beforeSend=>",data);
                },
                data: data,
                success: function (response) {
                    console.log(response,'===sucess response===');
                    location.href = '/videochat/listconferences/';
                },
                error:function(response){
                    console.log(response,'===error response===');
                }
            });
        }
    });

    // called on create conference form submit
    $('#createconference').on('submit',function(event){
        event.preventDefault();
        var _this = $(this);
        var participants = {};
        $('.conference-table-data .participant-details').each(function(k,v){
            var tmpSelector = $(v);
            if(tmpSelector.find('.selected-participant').is(':checked')){
                var tempData = {
                    'id' : tmpSelector.find('.selected-participant').attr('name'),
                    'email' : tmpSelector.find('.selected-participant').val(),
                    'role' : tmpSelector.find('.selected-participant-role').val(),
                    'special_privilege' : tmpSelector.find('.selected-participant-privilege').val()
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
        participants['title'] = _this.find('.conf-title').val();
        participants['starttime'] = startime
        participants['endtime'] = endtime
        data = {'data': JSON.stringify(participants)}
        $.ajax({
            url: '/videochat/createvideochatroom/',
            type: 'POST',
            headers: {
              'X-CSRFToken': $.cookie('csrftoken')
            },
            dataType:'json',
            beforeSend:function(){
                console.log("beforeSend=>",data);
            },
            data: data,
            success: function (response) {
                console.log(response,'===sucess response===');
                alert(response['message']);
                location.href = '/videochat/listconferences/';
            },
            error:function(response){
                console.log(response,'===error response===');
            }
        });
    });
    
    validate_date_time = function(input){
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