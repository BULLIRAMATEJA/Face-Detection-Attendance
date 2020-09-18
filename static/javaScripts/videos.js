// camera stream video element
let videoElm = document.querySelector('#video');
// flip button element
let flipBtn = document.querySelector('#flip-btn');

let canvasJQ = document.querySelector('#canvasInput');

// default user media options
let defaultsOpts = { audio: false, video: true }
let shouldFaceUser = true;

// check whether we can use facingMode
let supports = navigator.mediaDevices.getSupportedConstraints();


let stream = null;

function capture() {
  defaultsOpts.video = { facingMode: shouldFaceUser ? 'user' : 'environment' }
  navigator.mediaDevices.getUserMedia(defaultsOpts)
    .then(function(_stream) {
      stream  = _stream;
      videoElm.srcObject = stream;
      videoElm.play();
    })
    .catch(function(err) {
      console.log(err)
    });
}

function adjustCanvas(){
    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if(isMobile){
        canvasJQ.width = 420;
        canvasJQ.height = 615;
        $(".booth").width(420);
        $(".booth").height(615);
        flipBtn.disabled = false;
    }
    else{
        canvasJQ.width = 640;
        canvasJQ.height = 480;
        $(".booth").width(640);
        $(".booth").height(480);
          flipBtn.disabled = true;
    }
}

function flipCam(){
  console.log("Fliped");
  if( stream == null ) return
  // we need to flip, stop everything
  stream.getTracks().forEach(t => {
    t.stop();
  });
  // toggle / flip
  shouldFaceUser = !shouldFaceUser;
  capture();
}

capture();
adjustCanvas();