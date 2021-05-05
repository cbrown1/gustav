var apiUrl = "/api";
let trialPause = false;
let trialPauseDuration = 1000;
let performanceFeedback = true;
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
    $("#welcome .contextArea p").html('Please wait, initializing the experiment...');
    let serverResponse = $.post(apiUrl, {'type': 'style'});
    serverResponse.done(function( data ) {
        if (data.type != 'style') {
          $("#welcome").html(data.message);
        } else {
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
          // Display correct/wrong answer after user input
          performanceFeedback = data.performance_feedback;
          // Pause between trials to wait for user input
          trialPause = data.trial_pause;
          trialPauseDuration = data.trial_pause_dur;
        }
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

    section = $("body>section#info");
    if (section.hasClass("active")){
        $('body').keyup(function(e){
            if (section.hasClass("active")){
                if (e.keyCode == 32){
                    checkInfoButton();
                }
            }
        });
    }
}
var testArea = function (){
    var item = $("body>section#testArea.active");
    if (item.length > 0){
        startPage();
        getJsonApi({'type': 'trial', 'id': getID()}, "/speechapi");
    }
}
var infoArea = function (){
    var item = $("body>section#info.active");
    if (item.length > 0){
        getJsonApi({'type': 'setup', 'id': getID()}, "/speechapi");
    }
}
var disableAllPlayButtons = function (){
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
var playBtn = function (){
    const audio = new Audio($("body").attr("audio"));

    audio.addEventListener("canplay",function(){
        var max = audio.duration;
    });

    audio.play();

    audio.addEventListener('ended', function() {
        setTimeout(function (){
            var items = [];
            items.push("<p class='w-100 text-center'>" + $("body").attr("sentence_prompt") + "</p><br /><br>");
            items.push('<input type="text" name="q">');
            items.push('<button type="submit" onclick="sendAnswer()">Send</button>');
            $("body>section#testArea > section").html(items);
        },$("body").attr("audio_delay"))
    }, false);
}

function calibrationLoop(btn) {
    if ($("body #testArea").attr("loop") == undefined){
        $("body #testArea").attr("loop",true);
        calibrationPlay();
    }else{
        $("body #testArea").attr("loop",false);
    }
}

var calibrationPlay = function (){
    const audio = new Audio($("body").attr("calibration-audio"));
    audio.play();

    audio.addEventListener('ended', function() {
        if ($("body #testArea").attr("loop") != undefined){
            calibrationPlay();
        }
    }, false);
}

var getJsonApi = function (formdata = {'type': 'trial', 'id': getID()},u = apiUrl){
    // POST ---------------------------------------------------
    let serverResponse = $.post(u, formdata);
    serverResponse.done(function( data ) {
        switch (data.type) {
            case "start":
                alert("test");
                break;
            case "trial":
                var bb = $("body");
                if (data.audio){
                    bb.attr("audio",data.audio);
                    playBtn();
                }

                if (data.sentence){
                    bb.attr("sentence",data.sentence);
                }
                if (data.sentence_prompt){
                    bb.attr("sentence_prompt",data.sentence_prompt);
                }
                if (data.answer_prompt){
                    bb.attr("answer_prompt",data.answer_prompt);
                }
                if (data.start_prompt){
                    bb.attr("start_prompt",data.start_prompt);
                }
                if (data.play_prompt){
                    bb.attr("play_prompt",data.play_prompt);
                }
                if (data.sentence_text){
                    bb.attr("sentence_text",data.sentence_text);
                }
                if (data.answer_text){
                    bb.attr("answer_text",data.answer_text);
                }
                if (data.audio_delay){
                    bb.attr("audio_delay",data.audio_delay);
                }
                if (data.next_trial_delay){
                    bb.attr("next_trial_delay",data.next_trial_delay);
                }


                var items = [];
                items.push("<p>" + bb.attr("play_prompt") + "</p>")
                $("body>section#testArea > section").html(items);

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
            case "setup":
                $("body").attr("answer_prompt",data.answer_prompt)
                    .attr("start_prompt",data.start_prompt)
                    .attr("play_prompt",data.play_prompt)
                    .attr("sentence_prompt",data.sentence_prompt)
                    .attr("sentence_text",data.sentence_text)
                    .attr("answer_text",data.answer_text)
                    .attr("next_trial_delay",data.next_trial_delay)
                    .attr("audio_delay",data.audio_delay);

                    var items = [];
                    items.push('<p class="w-100 text-center">' + data.start_prompt + '</p>');
                    $("#info").html(items);
                    startPage();

                        $("body").on("click",function (){
                            if ($("#info.active").length > 0){
                            checkInfoButton()
                            }
                        });

                break;
            case "level_calibration":
                $("body > section").removeClass("active");
                var testArea = $("body #testArea");
                testArea.addClass("active");
                var content = "";
                content += '<p class="w-100 text-center">' + data.prompt + '</p><div class="d-flex">';

                if (data.loop_button){
                    content += "<div><button onclick='calibrationLoop(this)' id='loopBtn'>Loop</button></div>";
                }

                if (data.retry_button){
                    var jsonData = "{'type': 'calibration_retry', 'id': getID()}";
                    content += '<div><button onclick="getJsonApi('+ jsonData +');">Retry</button></div>';
                }

                if (data.done_button){
                    var jsonData = "{'type': 'calibration_done', 'id': getID()}";
                    content += '<div><button onclick="getJsonApi('+ jsonData +');">Done</button></div>';
                }
                content += "</div>";

                testArea.find("section").html(content);

                $("body").attr("calibration-audio",data.audio);
                calibrationPlay();

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
var sendAnswer = function (){
    var answer = $("input[name='q']").val();

    var items = [];
    items.push("<p class='w-100 text-center'>" + $("body").attr("sentence_text") + "</p><br /><br>");
    items.push('<input type="text" disabled value="' + $("body").attr("sentence") + '" id="disabledSentence">');
    items.push("<br /><br><br /><br><p class='w-100 text-center'>" + $("body").attr("answer_text") + "</p><br /><br>");
    items.push('<input type="text" disabled value="' + answer + '" id="disabledAnswer">');
    items.push("<br /><br><p class='w-100 split-line'></p><br /><br>");
    items.push("<p class='w-100 text-center'>" + $("body").attr("answer_prompt") + "</p><br /><br>");
    items.push('<input type="number" id="howManyCorrect">');
    items.push('<button type="submit" onclick="sendAnswerToApi()">Send</button>');

    $("body>section#testArea > section").html(items);

}
var sendAnswerToApi = function (){
    var answer = $("#howManyCorrect").val();
    setTimeout(function (){
        getJsonApi({'type': 'answer', 'value': answer}, '/speechapi');
    },$("body").attr("next_trial_delay"));
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
