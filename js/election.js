$(function() {
    // Populate the tab bar
    $('#tabs').load('html/tabs.html', function(data) {
        clickLoad(".loadE", electionLoad);
    });

    // Set up global variables to help with state
    activeTab = null;
    activeContest = null;
    electionInterval = null;
});

function clickLoad(element, fn) {
    // Set the cick function for all the subelements, then click the firstr
    // one.
    $(element).click(fn);
    $(element)[0].click();
}

function intervalHandler() {
    if(clicked != null) {
        var toLoad = loadPrefix + '/contest.html #c' + $(clicked).attr('id');
    } else {
        collection = $('#area').find('a');
        randomIndex = Math.round(Math.random() * $(collection).length);
        randomEl = $(collection).eq(randomIndex);
        var toLoad = loadPrefix + '/contest.html #c' + $(randomEl).attr('id')
    }
    $('#contest').load(toLoad);
    $('#progress').load(loadPrefix + '/update.html');
}

function electionLoad() {
    // Don't reload another county's results
    $('#area').empty();
    $('#contest').empty();
    clicked = null;

    loadPrefix = 'html/' + $(this).attr('id');
    $('#list').load(loadPrefix + '/area.html', function(data) {
        clickLoad(".loadC", contestLoad);
    });
    if(electionInterval != null) {
        clearInterval(electionInterval);
    }
    electionInterval = setInterval(intervalHandler, 60000);

    //Switch active tabs
    if(activeTab != null) {
        activeTab.removeClass('active');
    }
    activeTab = $(this).parent();
    activeTab.addClass('active');

    return false;
}

function contestLoad() {
    // Save the current element to a global variable for use in intervalHandler
    clicked = $(this);
    // This will actually load the data into the div.
    intervalHandler();

    if(activeContest != null) {
        activeContest.removeClass('active');
    }
    activeContest = $(this).parent();
    activeContest.addClass('active');

    return false;
}
