function contestLoad() {
    var toLoad = loadPrefix + '/contest.html #c' + $(this).attr('id');
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
    if(contestInterval != null) {
            clearInterval(contestInterval);
    }
    contestInterval = setInterval(function() {
            clicked.click()
    }, 60000);
    return false;
}

function areaLoad() {
    var toLoad = loadPrefix + '/area.html #a'+$(this).attr('id');
    $('#area').load(toLoad, function(data) {
        clickLoad(".loadC", contestLoad);
    });
    return false;
}

function electionLoad() {
    loadPrefix = 'html/' + $(this).attr('id');
    function progress() {
        $('#progress').load(loadPrefix + '/update.html');
        $('#list').load(loadPrefix + '/area.html #list', function(data) {
            clickLoad(".loadA", areaLoad);
        });
    }
    if(electionInterval != null) {
        clearInterval(electionInterval);
    }
    electionInterval = setInterval(progress, 60000);
    progress();

    if(activeTab != null) {
        activeTab.removeClass('active');
    }
    activeTab = $(this).parent();
    activeTab.addClass('active');

    // Don't reload another county's results
    clearInterval(contestInterval);
    contestInterval = null;
    $('#area').empty();
    $('#contest').empty();
    return false;
}

function clickLoad(element, fn) {
    $(element).click(fn);
    if($(element).length == 1) {
        $(element).click();
    }
}

$(document).ready(function() {
    $('#tabs').load('html/tabs.html', function(data) {
        clickLoad(".loadE", electionLoad);
    });
    activeTab = null;
    contestInterval = null;
    electionInterval = null;
});
