$(document).ready(function () {
    $("#create_account").hide();

    $("#show_create_account_form").click(function () {
        console.log("clicked-create an account")
        $("#login_form").hide();
        $("#create_account").show();
    });

    
    $("#cancel_to_login").click(function () {
        console.log("clicked-create an account")
        $("#login_form").show();
        $("#create_account").hide();
    });
});