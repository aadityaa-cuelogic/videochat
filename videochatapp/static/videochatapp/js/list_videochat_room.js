$(document).ready(function(){
	console.log('list videochat js');
	// called on conference cancel button click
	$('.cancel-conference').on('click', function(e){
		var _this = $(this);
		var conf_room_id = _this.attr('id');
		var confirm = confirm("Are you sure, you want to cancel conference ?");
		if(confirm){
			$.ajax({
				url:'/videochat/cancelconference',
				type:'POST',
				headers:{
					'X-CSRFToken': $.cookie('csrftoken')
				},
				dataType:'json',
				beforeSend:function(){
					console.log("beforeSend");
				},
				data:{
					'conf_room_id':conf_room_id
				},
				success:function(response){
					console.log(response,'===success===');
					location.href = '/videochat/listconferences/';
				},
				error:function(response){
					console.log(response,'===error===');
				}
			});
		}
	});
	// called on conference edit button click
	$('.edit-conference').on('click', function(e){
		console.log("Edit conference click");
		var _this = $(this);
		var conf_room_id = _this.attr('id');
		var url = '/videochat/'+conf_room_id+'/editconference/';
		location.href = url;
		return false;
		// $.ajax({
		// 	url:'/videochat/editconference/',
		// 	type:'POST',
		// 	headers: {
  //             'X-CSRFToken': $.cookie('csrftoken')
  //           },
		// 	dataType:'json',
		// 	beforeSend:function(){
		// 		console.log("beforeSend");
		// 	},
		// 	data: {
		// 		'conf_room_id':conf_room_id
		// 	},
		// 	success:function(response){
		// 		console.log("response success");
		// 	},
		// 	error:function(response){
		// 		console.log("response error");
		// 	}
		// });
	});
});