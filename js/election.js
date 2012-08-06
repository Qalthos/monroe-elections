function contestLoad() {
    var toLoad = loadPrefix + '/contest.html #c' + $(this).attr('id');
    $('#contest').load(toLoad);
    clicked = $(this)
    if(contestInterval != null) {
            clearInterval(contestInterval);
    }
    contestInterval = setInterval(clicked.click, 60000);
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

    //Switch active tabs
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
    // Populate the tab bar
    $('#tabs').load('html/tabs.html', function(data) {
        clickLoad(".loadE", electionLoad);
    });

    // Set up global variables to help with state
    activeTab = null;
    contestInterval = null;
    electionInterval = null;
});
