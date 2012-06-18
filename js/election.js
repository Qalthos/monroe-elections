function contestLoad() {
    var toLoad = 'contest.html #c' + $(this).attr('id');
    $('#contest').load(toLoad, function(data){
        $(".DEM").children('span').progressBar({ barImage: 'images/progressbg_Democrat.png'} );
        $(".REP").children('span').progressBar({ barImage: 'images/progressbg_Republican.png'} );
        $(".GRN").children('span').progressBar({ barImage: 'images/progressbg_Green.png'} );
        $(".LBT").children('span').progressBar({ barImage: 'images/progressbg_Libertarian.png'} );
        $(".CON").children('span').progressBar({ barImage: 'images/progressbg_Conservative.png'} );
        $(".WOR").children('span').progressBar({ barImage: 'images/progressbg_WorkingFamily.png'} );
        $(".IND").children('span').progressBar({ barImage: 'images/progressbg_Independence.png'} );
        $(".OTHER").children('span').progressBar({ barImage: 'images/progressbg_Other.png'} );
    });
    clicked = $(this)
    if (interval != null) {
            clearInterval(interval);
    }
    interval = setInterval(function() {
            clicked.click()
    }, 60000);
    return false;
}

function areaLoad() {
    var toLoad = 'area.html #a'+$(this).attr('id');
    $('#area').load(toLoad, function(data) {
        $(".loadC").click(contestLoad);
    });
    return false;
}

function progress() {
    $('#progress').load('update.html');
    $('#list').load('area.html #list', function(data) {
        $(".loadA").click(areaLoad);
    });
}

$(document).ready(function() {
    progress();
    setInterval(progress, 60000);
    interval = null;
});
