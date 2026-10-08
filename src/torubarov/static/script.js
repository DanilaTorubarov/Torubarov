$(document).ready(function(){
    $('#67').on('submit',function(e){
        e.preventDefault();
        err = 0;
        if ($('#fullname').val().trim() === '' || $('#password').val().trim() != $('#confirm_password').val().trim()){
            err = 1;
        }else{
            err = 0;
        }
        if (err == 0){
            $.ajax({
                url: '/user_register',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    name: $('#fullname').val(),
                    password: $('#password').val(),
                    email: $('#email').val()
                })
            })
        }
    })
    $('#login-form').on('submit', function (e) {
        e.preventDefault();
        $.ajax({
            url: '/user_login',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                email: $('#login-email').val(),
                password: $('#login-password').val()
            })
        })
        .done(function (res) {
            if (res.status === 'ok') {
                window.location.href = res.redirect; // → /lk
            }
        })
        .fail(function (xhr) {
            let msg = 'Ошибка входа';
            try { msg = JSON.parse(xhr.responseText).message; } catch (e) {}
            alert(msg);
        });
    });
})