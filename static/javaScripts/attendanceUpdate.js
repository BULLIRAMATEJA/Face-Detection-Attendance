const FPS = 0.2;
var Length = 0;

function attendanceUpdate() {
    let begin = Date.now();
    $.ajax({
        type: "GET",
        url: "/ajaxAttendanceUpdate",
        cache:false,
        dataType: "json",
        success: function(resp){
            Length = resp.length;
            for(var itr = 0; itr<resp.length; itr++){
                if(resp[itr] === "Present"){
                    var sel = document.getElementById('sel'+itr.toString());
                    sel.selectedIndex = 1;
                }
            }
            document.getElementById("QRimage").src = "data:image/png;base64,"+resp["contents"];
            // schedule next one.
            let delay = 1000/FPS - (Date.now() - begin);
            setTimeout(attendanceUpdate, delay);
        }
    });
    
    
}
// schedule first one.
setTimeout(attendanceUpdate, 0);

function beforeSubmit(){
    var headCount = 0;
    
    for(var itr = 0; itr<Length; itr++){
        if(document.getElementById('sel'+itr.toString()).selectedIndex === 1){
            headCount += 1;
        }
    }
    var givenCount = document.getElementById("Count").value;
    if(parseInt(givenCount, 10) !== headCount){
        alert("Count Mismatch!! \n Check head count again");
        return false;
    }
    document.getElementById('submit').disabled = true;
} 