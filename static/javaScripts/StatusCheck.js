const FPS = 1
function statusCheck() {
    let begin = Date.now();
    $.ajax({
        type: "GET",
        url: "/ajaxStatusCheck",
        cache:false,
        dataType: "json",
        success: function(resp){
            console.log("resp: "+resp.Status);
            if(resp.Status === "Closed"){
                document.getElementById("markAttendanceBtn").disabled = true;
                document.getElementById("statusReport").innerHTML = "Attendance Not Available";
            }
            else if(resp.Status === "Present"){
                document.getElementById("markAttendanceBtn").disabled = true;
                document.getElementById("statusReport").innerHTML = "Attendance Already Marked";
            }
            else{
                document.getElementById("markAttendanceBtn").disabled = false;
                document.getElementById("statusReport").innerHTML = "Attendance Available";
            }
        }
    });
    
    // schedule next one.
    let delay = 1000/FPS - (Date.now() - begin);
    setTimeout(statusCheck, delay);
}
// schedule first one.
setTimeout(statusCheck, 0);