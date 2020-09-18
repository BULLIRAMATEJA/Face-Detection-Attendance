function beforeSubmit() {
    console.log("Enter");
    var passwd = document.getElementById("password").value;
    var repasswd = document.getElementById("repassword").value;
    if(passwd !== repasswd){
        alert("Password didn't Match");
        return false;
    }
    if(passwd.length < 6){
        alert("Password is too weak!!");
        return false;
    }
    var email = document.getElementById("email").value;
    var status = false;
    $.ajax({
        url: '/ajaxCheckEmail',
        async: false,
        data: {
          'Email': email
        },
        dataType: 'json',
        success: function (data) {
          if (data.Exist == "True") {
            status = true;
          }
        }
      });
    if(status){
        alert("Email already exists");
        return false;
    }
    document.getElementById("submit").disabled = true;
}