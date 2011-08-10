$(document).ready(function() {
        $(".loadA").click(function() {
                var toLoad = 'area.html #a'+$(this).attr('id');
                $('#area').load(toLoad, function(data, status, xhr) {
                        $(".loadC").click(function() {
                                var toLoad = 'contest.html #c'+$(this).attr('id');
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
                                return false;
                        });
                });
                return false;
        });
});
