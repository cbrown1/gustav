var apiUrl = "/api";
var abortBtn = function (){
    $('.top-right').on("click",function() {
        var confirm = window.confirm("Are you sure you want to cancel the test?");

        if (confirm){
            getJsonApi({'type': 'abort', 'id': getID()});
        }
    });
}
// Get styling information from the server
var mainColors = function (){
    let serverResponse = $.post(apiUrl, {'type': 'style'});
    serverResponse.done(function( data ) {
        $(".logoArea img").attr("src",data.logo);
        $("#welcome .contextArea p").html(data.message);
        $("#agreeBtn").html(data.accept_btn);
        $.each( serverResponse.responseJSON, function(key, val ) {
            if (key == "loading_bars"){
                $("body").addClass("loading_bars-"+val);
            }else{
                document.documentElement.style.setProperty(key, val);
            }
        });
    });
}
// Get session id
var getID = function(){
    if (!sessionStorage.getItem("userid")){
        var currentTime = new Date().getTime();
        sessionStorage.setItem("userid", currentTime + parseInt(Math.random(1111,999999) * 10000));
    }
    return sessionStorage.getItem("userid")
}
var checkWelcomeButtons = function (btn = false){
    var changeArea = function (){
        $("body>section#welcome").removeClass("active");
        $("body>section#kvkk").addClass("active");
    }

    if (btn){
        changeArea();
    }else{
        $("#startTest").on("click",function (){
            changeArea();
        });
    }
}
var checkKVKKButtons = function (btn = false){
    var changeArea = function (){
        $("body>section#kvkk").removeClass("active");
        $("body>section#info").addClass("active");
    }

    changeArea();
    infoArea();

    setTimeout(function (){
        $("body>section#kvkk").remove();
    },500);
}
var checkInfoButton = function (btn = false){
    var changeArea = function (){
        $("body>section#info").removeClass("active");
        $("body>section#testArea").addClass("active");
    }

    changeArea();
    // Remove the info part after user clicks ok
    setTimeout(function (){
        $("body>section#info").remove();
    }, 500);
    testArea();
}
var startPage = function (){
    var section = $("body>section#welcome");
    if (section.hasClass("active")){
        $('body').keyup(function(e){
            if(e.keyCode == 32){
                checkWelcomeButtons(true);
            }
        });
        checkWelcomeButtons();
    }

    section = $("body>section#testArea");
    if (section.hasClass("active")){
        $('body').keyup(function(e){
            if(e.keyCode == 32){
                var find = section.find("div button:not(.listened)");
                var playing = section.find("div button.playing");

                if (playing.length < 1){
                    if (find.length > 0){
                        console.log(find.eq(0).trigger('click'));
                    }
                }
            }else if (e.key == 1 || e.key == 2 || e.key == 3 || e.key == 4 || e.key == 5 || e.key == 6 || e.key == 7 || e.key == 8 || e.key == 9){
                var find = section.find("div button:not(.listened)");
                var playing = section.find("div button.playing");

                if (playing.length < 1){
                    if (find.length < 1){
                        var finder = section.find("div button");
                        var myKey = parseInt(e.key)-1;
                        finder.eq(myKey).trigger("click");
                        console.log("seçimi yaptık", e.key);
                      }
                }
            }else if(e.keyCode == 27){
                $(".top-right").click();
            }
        });
    }
}
var testArea = function (){
    var item = $("body>section#testArea.active");
    if (item.length > 0){
        startPage();
        getJsonApi();
    }
}
var infoArea = function (){
    var item = $("body>section#info.active");
    if (item.length > 0){
        getJsonApi({'type': 'info', 'id': getID()});
    }
}
var diasbleAllPlayButtons = function (){
    var item = $("body>section#testArea.active");
    item.find("button").addClass("disabled");
}
var activeAllPlayButtons = function (){
    var item = $("body>section#testArea.active");
    item.find("button").removeClass("disabled");
}
var notListened = function (){
    var count = $("body > section#testArea div button").length;
    var count1 = $("body > section#testArea div button.listened").length;
    if (count == count1){
        return true;
    }else{
        return false;
    }
}
var playBtn = function (elem){
    var testArea = $("#testArea");
    var el = $(elem);

    function ifAllListened(){
        var item = $("body>section#testArea.active");
        var buttons = item.find("button").length;
        var listenedButtons = item.find("button.listened").length;

        if (buttons == listenedButtons){
            var section = $("body>section#testArea")
            section.find("p").html(section.data("prompt2"));
        }
    }
    // Butun ses dosyalari oynadiktan sonra
    if (notListened()){

        el.addClass("selectedBtn");

        if (el.data("id") == testArea.data("answer")){
            testArea.find("p.w-100.text-center").html("correct answer");
        }else{
            testArea.find("p.w-100.text-center").html("wrong answer");
        }


        diasbleAllPlayButtons();
        testArea.find("button").each(function (){
            if ($(this).data("id") == testArea.data("answer")){
                $(this).addClass("success");
                console.log("correct answer", testArea.data("answer"), $(this).data("id"));
            }else{
                $(this).addClass("error");
                console.log("wrong answer", testArea.data("answer"), $(this).data("id"));
            }
        })
        // Send user selection
        setTimeout(function (){
            getJsonApi({'type': 'answer', 'id': getID(), answer:testArea.data("answer")});
        },testArea.data("next-delay"));
    }else{
        el.addClass("playing");

        testArea.find("p.w-100.text-center").html("Playing " + el.data("eq"));

        diasbleAllPlayButtons();
        const audio = new Audio(el.data("sound"));

        audio.addEventListener("canplay",function(){
            var max = audio.duration;
        });

        audio.play();

        audio.addEventListener('timeupdate', onLoadProgress);
        function onLoadProgress () {
            var progress = parseInt(((audio.currentTime / audio.duration) * 100), 10);
            el.parent().find("span").css("width",progress+"%");
        }

        audio.addEventListener('ended', function() {
            var tArea = $("#testArea").find("p.w-100.text-center");
            tArea.html(tArea.data("default"));
            el.addClass("listened");
            ifAllListened();
            el.removeClass("playing");
            el.parent().find("span").css("width","0%");
            activeAllPlayButtons();

            var testArea = $("body>section#testArea");

            if (testArea.find("button:not(.listened)")){
                setTimeout(function (){
                    testArea.find("button:not(.listened)").eq(0).click()
                },testArea.data("delay"));
            }

        }, false);
    }
}
var getJsonApi = function (formdata = {'type': 'trial', 'id': getID()}){
    // POST ---------------------------------------------------
    let serverResponse = $.post(apiUrl, formdata);
    serverResponse.done(function( data ) {
        switch (data.type) {
            case "start":
                alert("test");
                break;
            case "trial":
                var items = [];
                items.push('<p class="w-100 text-center" data-default="' + data.prompt1 + '">' + data.prompt1 + '</p>');
                items.push('<span class="top-left">' + data.upper_left_text + '</span>');
                items.push('<span class="bottom-left">' + data.lower_left_text + '</span>');
                items.push('<span class="bottom-right">' + data.lower_right_text + '</span>');
                items.push('<span class="top-right"><img src="static/close.svg" /></span>');
                // Add audio play buttons here
                $.each( data.items, function( key, val ) {
                    var i = parseInt(key) +1;
                    items.push('<div><button type="button" onclick="playBtn(this);" data-eq="' + i + '" data-id="' + val.id + '" data-sound="' + val.file + '">' + val.name + '</button><span></span></div>');
                });

                $("body>section#testArea")
                    .html(items).attr("data-prompt2",data.prompt2)
                    .attr("data-delay",data.delay)
                    .attr("data-next-delay",data.next_delay)
                    .attr("data-answer",data.answer);
                abortBtn();

                break;
            case "stop":
                var changeArea = function (){
                    $("body>section#testArea").removeClass("active");
                    $("body>section#stop").addClass("active");
                }

                changeArea();
                $("#stop").html('<p>' + data.message + '</p>');
                break;
            case "abort":
                var changeArea = function (){
                    $("body>section#testArea").removeClass("active");
                    $("body>section#stop").addClass("active");
                }

                changeArea();
                $("#stop").html('<p>' + data.message + '</p>');
                break;
            case "info":
                var items = [];
                items.push('<p>' + data.message + '</p>');
                items.push("<button id='infoBtn' onclick='infoBtnCheck()'>OK</button>")
                $("#info").html(items);
                break;
            default:
                break;
        }
    });
}
var kvkkAreaCheck = function (){
    var btn = $("#agreeBtn");
    var check = $("#agreeCheck");

    check.on("change",function (){
        $(this).toggleClass("checked");

        if ($(this).hasClass("checked")){
            btn.removeAttr("disabled");
        }else{
            btn.attr("disabled","disabled");
        }
    });

    btn.on("click",function (){
        if (check.hasClass("checked")){
            checkKVKKButtons();
        }
    })
}

// TO DO: remove this function and just call checkInfoButton
var infoBtnCheck=function (){
    checkInfoButton();
}

$(document).ready(function (){
    mainColors();
    startPage();
    kvkkAreaCheck();
});
