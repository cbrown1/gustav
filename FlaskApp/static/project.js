// Todo::Change Main Colors On API
var mainColors = function (){
    $.getJSON( "static/colors.json", function( data ) {
        $.each( data, function( key, val ) {
            document.documentElement.style.setProperty(key, val);
        });
    });
}
var checkWelcomeButtons = function (btn = false){
    var changeArea = function (){
        $("body>section#welcome").removeClass("active");
        $("body>section#testArea").addClass("active");

        testArea();
    }

    if (btn){
        changeArea();
    }else{
        $("#startTest").on("click",function (){
            changeArea();
        });
    }
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
}
var testArea = function (){
    var item = $("body>section#testArea.active");
    if (item.length > 0){
        getJsonApi();
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
    var el = $(elem);
    if (notListened()){
        $.ajax({
            type: "POST",
            url: "post.html",
            data: {val:el.data("id")},
            success: function (data){
                console.log(data)
            }
        });
    }else{
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
            el.addClass("listened");
            el.parent().find("span").css("width","0%");
            activeAllPlayButtons();
        }, false);
    }


}
var getJsonApi = function (){
    $.getJSON( "api.json", function( data ) {
        var items = [];
        $.each( data.items, function( key, val ) {
            items.push('<div><button type="button" onclick="playBtn(this);" data-id="' + val.id + '" data-sound="' + val.file + '">' + val.name + '</button><span></span></div>');
        });

        $("body>section#testArea").html(items);
    });
}


$(document).ready(function (){
    mainColors();
    startPage();
});
