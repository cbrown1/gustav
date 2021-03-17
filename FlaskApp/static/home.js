var getTests = function (){
    if ($("body>.usersPages>.experimentPage").length > 0){
        let serverResponse = $.post('homeapi', {'type': 'home'});
        serverResponse.done(function( data ) {
            var items = [];
            $.each( data.experiments, function( key, val ) {
                var btn = "";
                if (val.ready){
                    btn = '<a href="' + val.url + '" target="_blank" class="available">Start</a>';
                }else{
                    btn = '<button type="button" class="notAvailable">Not available</button>';
                }
                items.push('<div class="experimentArea"><div><h2>' + val.title + '</h2><span>' + val.description + '</span></div>' + btn + '</div>');
            });

            $("body>.usersPages>.experimentPage").html(items);
        });
    }
}

var userCheck = function (){
    if ($(".loginFormArea").length > 0){
        $(".loginFormArea form").on("submit",function (event){
            event.preventDefault();

            $.ajax({
                type: "POST",
                url: "/login",
                data: {
                    username: $(".loginFormArea form input[name='username']").val(),
                    password: $(".loginFormArea form input[name='password']").val()
                },
                success: function (data){
                    console.log(data);
                    if (data == "true"){
                        $(".loginFormArea").remove();
                        $(".observingPage, .observingBottom").css("display","flex");

                        getObservings();

                    }
                }
            });
        })
    }
}

var changePorts = function (){
    $("input[name='max-ports'],input[name='base-ports']").on("change",function (){
        $.ajax({
            type: "POST",
            url: "/change_ports",
            data: {
                max_ports: $("input[name='max-ports']").val(),
                base_port: $("input[name='base-ports']").val()
            }
        });
    });
}

var getObservings = function (){
    let serverResponse = $.post('setupapi', {'type': 'setup'});
    serverResponse.done(function( data ) {
        var items = [];
        $.each( data.experiments, function( key, val ) {

            subjects = "";
            $.each(val.subjects, function (i,item){
                subjects = subjects + '<div><span class="d-block"> ' + item.id + ' </span><span class="d-block"> ' + item.port + ' </span><span class="d-block">' + item.time + '</span></div>';

            })

            items.push('<div class="observingArea"><div><h2>' + val.title + '</h2><span>' + val.description + '</span><div class="subjects">' + subjects + '</div></div></div>');

        });

        $(".observingPage").html(items);

        $("input[name='max-ports']").val(data.max_ports);
        $("input[name='base-ports']").val(data.base_port);
        changePorts();
    });
}

$(document).ready(function (){
    getTests();
    userCheck();
});
