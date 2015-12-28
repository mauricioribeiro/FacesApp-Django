var FacesApp = {

	status : "ready",
	webcamId : "webcam",

	form : null,
	canvas : null,
	frame : null,

	options: {
	    "audio": false,
	    "video": true,

	    el: "webcam",

	    width: 320,
	    height: 320,

	    mode: "callback",
	    swffile: "fallback/jscam_canvas_only.swf",

	    quality: 85,

	    // callback for capturing the fallback stream
	    onCapture: function () {
	        window.webcam.save();
	    },

	    // callback for saving the stream, useful for
	    // relaying data further.
	    onSave: function (data) {},
	    onLoad: function () {},
	},

	setup : function(formId){
		this.form = $('#'+formId);
		this.form.append('<canvas id="'+formId+'_canvas" style="display:none"></canvas><input id="'+formId+'_frame" name="'+formId+'_frame" type="hidden"/>');
		this.frame = $('#'+formId+'_frame');
		this.canvas = $('#'+formId+'_canvas')[0];
	},

	run : function(){
		getUserMedia(this.options, this.success, this.error);
		window.webcam = this.options;
		this.status = "running";
		console.log('FacesApp is working...');
	},

	webcam2canvas : function(){
		var webcam = $('#'+this.webcamId+' > video')[0];
		this.canvas.width = webcam.videoWidth;
		this.canvas.height = webcam.videoHeight;
		this.ctx = this.canvas.getContext("2d").drawImage(webcam, 0, 0);
	},

	success: function(stream) {
        if (FacesApp.options.context === 'webrtc') {

            var video = FacesApp.options.videoEl;
            var vendorURL = window.URL || window.webkitURL;
            video.src = vendorURL ? vendorURL.createObjectURL(stream) : stream;

            video.onerror = function () {
                stream.getVideoTracks90[0].stop();
                streamError();
            };
            this.status = "running";
        }
    },

    error: function (error) {
		this.status = "unavailable";
		console.error('An error occurred: [CODE ' + error.code + ']');
	},

	get: function () {
		if (FacesApp.options.context === 'webrtc') {
			this.webcam2canvas();
			return this.canvas.toDataURL('image/jpeg');
		} else {
			alert('No context was supplied to FaceApp::get()');
		}
	},

	sendAJAX: function() {
		$.ajax({
	      url: "login",
	      data : { "frame" : this.get() },
	      method : "POST",
	      headers: { "X-CSRFToken": getCookie("csrftoken") }
	    });
	    /*.done(function(nome) {
	      $('#ajax-cliente-nome').val(nome);
	    });*/
		console.log('Sent by AJAX!');
	},

	send: function() {
		this.frame.val(this.get());
		this.form.submit();
	},

	printStatus : function() {
		console.log('[FacesApp status: ' + this.status + ']');
	}

}

$(document).ready(function(){

	FacesApp.setup('loginUsingFacesApp');
	FacesApp.run();

});