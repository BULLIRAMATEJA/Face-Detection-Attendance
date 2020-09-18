var canvas = document.getElementById('canvasInput');
var ctx    = canvas.getContext('2d');
var video  = document.getElementById('video');

video.addEventListener('play', function () {
    var $this = this; //cache
    (function loop() {
        if (!$this.paused && !$this.ended) {
            ctx.drawImage($this, 0, 0);
            setTimeout(loop, 1000 / 30); // drawing at 30fps
        }
    })();
}, 0);