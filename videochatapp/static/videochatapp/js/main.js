// ......................................................
// ..................RTCMultiConnection Code.............
// ......................................................
var connection = new RTCMultiConnection();
var recordRTC;
var initiator_stream ;
// socket.io server
connection.socketURL = 'https://rtcmulticonnection.herokuapp.com:443/';

connection.session = {
    'audio':true,
    'video':true
}

connection.sdpConstraints.mandatory = {
    OfferToReceiveAudio:true,
    OfferToReceiveVideo:true
}

// ......................................................
// ......................Handling Room-ID................
// ......................................................
// TODO : Manage from backend
var room_id = document.getElementById('roomid');
// if (localStorage.getItem('room_id')) {
//     room_id.value = localStorage.getItem('room_id');
// } else {
    // room_id.value = connection.token();
    // localStorage.setItem('room_id', room_id.value);
// }

// ......................................................
// ......................Global Variables................
// ......................................................
// TDOD : Try to remove these HTML variables
var common_button =`<button class="btn-mute btn-success"><img class="img-icon" src="/static/videochatapp/images/mute.png"></button>
                <button class="btn-plus btn-success"><img class="img-icon" src="/static/videochatapp/images/plus.png"></button>
                <button class="btn-minus btn-success"><img class="img-icon" src="/static/videochatapp/images/minus.png"></button>
                <button class="btn-full btn-success"><img class="img-icon" src="/static/videochatapp/images/fullscreen.png"></button>
            `
var owner_button =`<button class="btn-share btn-success"><img class="img-icon" src="/static/videochatapp/images/share.png"></button>
                    <button class="btn-exit btn-success"><img class="img-icon" src="/static/videochatapp/images/exit.png"></button>`

var recording_button = `<a class="btn btn-success btn-recording">Start Recording</a>
                        <a class="btn btn-success btn-stop-recodring">Stop Recording</a>`

var streamid;
var localVideo = document.getElementById('local-video-container');
var remoteVideo = document.getElementById('remote-video-container');
var openButton= document.getElementById('btn-open-or-join');

connection.onstream = function(event){
    if(connection.isInitiator==false){
        var recording_container = $('#recording-container');
        recording_container.html(recording_button);
        addRecordingEvent(recording_container);
        $(recording_container).find('.btn-stop-recodring').hide();
    }
    if(event.stream.isScreen === true && connection.isInitiator==true) {
        // width = connection.videosContainer.clientWidth - 120;
        //     var share=document.getElementById('screen-local');
        //     //share.appendChild(event.mediaElement);
        //     var mediaElement = getMediaElement(event.mediaElement, {
        //         title: event.userid,
        //         buttons: ['full-screen'],
        //         width: width,
        //         showOnMouseEnter: false
        //     });
        //     share.appendChild(mediaElement);
        //     mediaElement.id = event.streamid;
        return; 
    }
     if(event.stream.isScreen== true && event.type=="remote" && connection.isInitiator == false){
            width = connection.videosContainer.clientWidth - 120;
            var remote_share=document.getElementById('screen-remote');
            var mediaElement = getMediaElement(event.mediaElement, {
                title: event.userid,
                buttons: ['full-screen','mute-audio',
                          'take-snapshot',
                           'record-audio',
                           'record-video','volume-slider','stop'],
                width: width,
                showOnMouseEnter: false
            });
            remote_share.appendChild(mediaElement);
            //remote_share.appendChild(event.mediaElement);
            return;

    }

    if(event.stream.isScreen==true && connection.isInitiator==false && event.type=='local'){
        return;
    }

    var video = event.mediaElement;
    if(event.type === 'local'){
        var i;
        var html_video = document.createElement("div");
        html_video.classList.add("full-width");
        localVideo.appendChild(html_video);


        var elementdiv = document.createElement("div");
        elementdiv.classList.add("btnPanel");
        html_video.appendChild(elementdiv);
        var selector = $(localVideo).find('.btnPanel');
        selector.html(common_button+owner_button);
        html_video.appendChild(video);
        var localStream = connection.attachStreams[0];
        localStream.mute('audio');
        addButtonEvent(selector);
    }
    else if(event.type === 'remote'){
        var i;
        var html_video = document.createElement("div");
        html_video.classList.add("full-width");
        remoteVideo.appendChild(html_video);
        // it will create nave bar control append to nav bar
        var elementdiv = document.createElement("div");
        elementdiv.classList.add("btnPanel");
        html_video.appendChild(elementdiv);
        var selector = $(remoteVideo).find('.btnPanel'); 
        selector.html(common_button);
        // append video div 
        html_video.appendChild(video);
        var localStream = connection.attachStreams[0];
        localStream.unmute('audio');
        addButtonEvent(selector);
        $('html, body').animate({
            scrollTop: $(remoteVideo).offset().top
        },2000);
    }
    streamid = event.streamid; 
}


// ......................................................
// ......................Handling Events................
// ......................................................
document.getElementById('btn-open-or-join').onclick = function(){
    this.disabled = true;
    $('#roomid').prop('disabled',true);
    connection.openOrJoin(room_id.value || 'predefined-roomid');
}

connection.onEntireSessionClosed = function(event) {
    connection.attachStreams.forEach(function(stream) {
        stream.stop();
    });
};

connection.onstreamended = function(e) {
    if (!e.mediaElement) {
        e.mediaElement = document.getElementById(e.streamid);
    }
    if (!e.mediaElement || !e.mediaElement.parentNode) {
        return;
    }
    e.mediaElement.parentNode.remove();
};

connection.getScreenConstraints = function(callback) {
    getScreenConstraints(function(error, screen_constraints) {
        if (!error) {
            screen_constraints = connection.modifyScreenConstraints(screen_constraints);
            callback(error, screen_constraints);
            return;
        }
        throw error;
    });
};

// ......................................................
// ......................Custom Functions................
// ......................................................
function addButtonEvent(selector){    
    selector.find(".btn-exit").off("click");    
    selector.find(".btn-exit").on("click",exit_fun);
    selector.find(".btn-mute").off("click");
    selector.find(".btn-mute").on("click",mute_fun);
    selector.find(".btn-plus").off("click");
    selector.find(".btn-plus").on("click",plus_fun);
    selector.find(".btn-minus").off("click");
    selector.find(".btn-minus").on("click",minus_fun);
    selector.find(".btn-full").off("click");
    selector.find(".btn-full").on("click",full_fun);
    selector.find(".btn-share").off("click");
    selector.find(".btn-share").on("click",share_fun);
    selector.find(".btn-recording").off("click");
    selector.find(".btn-recording").on("click",record_fun);
    selector.find(".btn-stop-recodring").off("click");
    selector.find(".btn-stop-recodring").on("click",stop_record_fun);

}

function addRecordingEvent(selector){
    selector.find('.btn-recording').off("click");
    selector.find('.btn-recording').on("click",record_fun);
    selector.find(".btn-stop-recodring").off("click");
    selector.find(".btn-stop-recodring").on("click",stop_record_fun);
}

function mute_fun(){
    video = this.parentNode.nextElementSibling;
    connection.streamEvents[video.id].stream.mute('audio');
}

function full_fun(){
    video = this.parentNode.nextElementSibling; 
    if (video.webkitRequestFullScreen) {
        video.webkitRequestFullScreen();
    } else if (video.webkitexitFullscreen) {
        video.webkitexitFullscreen();
    }
}

function plus_fun(){
    video = this.parentNode.nextElementSibling;
    media_stream = connection.streamEvents[video.id].stream
    audiotrack  = media_stream.getAudioTracks()[0]

    if(audiotrack["enabled"] == false){
        connection.streamEvents[video.id].stream.unmute('audio');
        video.volume = 0.0
    }
    if((video.volume+0.1)<=1.0 ){
        video.volume= video.volume + 0.1;
    }
    if((video.volume+0.1)>1.0 ){
        video.volume= 1.0;
    }
}

function minus_fun(){    
    video = this.parentNode.nextElementSibling;
    if((video.volume-0.1)>=0.0 ){
        video.volume= video.volume - 0.1;
    }
    if((video.volume-0.1)<0.0 ){
        connection.streamEvents[video.id].stream.mute('audio'); 
    }
}

function exit_fun() {
    if (connection.isInitiator) {
        connection.closeEntireSession(function() {
            // TODO : Correct this code line for remove
            $('.btnPanel').remove();
        });
    } else {
        connection.leave();
        connection.attachStreams.forEach(function(stream) {
            stream.stop();
        });
        $('#recording-container').remove();
    }
}

function share_fun(){
    this.disabled = true;
    connection.addStream({
        screen: true,
        oneway: true
    });
}

// document.getElementsByClassName('btn-share')[0].onclick = function() {
//     connection.session['screen']=true
//     this.disabled = true;
//     connection.addStream({
//         screen: true,
//         oneway: true
//     });
// };

function record_fun(){
    // video = this.parentNode.nextElementSibling;
    // id = connection.streamEvents[video.id].stream.id
    // stream = connection.streamEvents[video.id].stream
    
    var recording_container = $('#recording-container');
    $(recording_container).find('.btn-recording').hide();
    recording_container.find('.btn-stop-recodring').show();
    alert("Recording Of Conference Is Started");
    var i;
    stream = connection.peers[connection.sessionid].streams[0]
    for(i=0;i<connection.getRemoteStreams().length;i++){
        if(stream == connection.getRemoteStreams()[i]){
            stream = connection.getRemoteStreams()[i];
            break;
        }
    }


    if(stream == undefined){
        console.log("stream is undefined")
    }

    var options = {
        mimeType: 'video/webm', // or video/webm\;codecs=h264 or video/webm\;codecs=vp9
        // audioBitsPerSecond: 128000,
        // videoBitsPerSecond: 128000,
        bitsPerSecond: 128000 // if this line is provided, skip above two
    };

    recordRTC = RecordRTC(stream, options);
    recordRTC.startRecording();
}

function postFiles(){
    var recordedBlob = recordRTC.getBlob();
    console.log(recordedBlob);
    var fileName = generateRandomString() + '.webm';
    var file = new File([recordedBlob], fileName, {
                    type: 'video/webm'
                });
    xhr('videoconverter/', file, function(responseText) {
        alert(responseText);
    });
}

function xhr(url, data, callback) {
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            callback(request.responseText);
        }
    };
    request.open('POST', url);
    var formData = new FormData();
    formData.append('file', data);
    request.send(formData);
}

function generateRandomString() {
    if (window.crypto) {
        var a = window.crypto.getRandomValues(new Uint32Array(3));
        var token = '';
        for (var i = 0, l = a.length; i < l; i++) token += a[i].toString(36);
        return token;
    } else {
        return (Math.random() * new Date().getTime()).toString(36).replace( /\./g , '');
    }
}

function stop_record_fun(){    
    var recording_container = $('#recording-container');
    $(recording_container).find('.btn-stop-recodring').hide();
    $(recording_container).find('.btn-recording').show();
    alert("Recording Of Conference Is Stop.");
    var video =  document.getElementById('recording');
    var recordedBlob;
    // recordRTC.stopRecording(function () {
        
    //     recordedBlob = recordRTC.getBlob();
        //var url = URL.createObjectURL(recordedBlob);
        // video.src = url;
        //convertStreams(recordedBlob);

        //window.open(url);
    //});
    recordRTC.stopRecording(postFiles)
}
