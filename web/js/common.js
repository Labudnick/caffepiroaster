//************* Current temperature chart *************//
google.charts.load('current', {'packages':['gauge', 'line']});
google.charts.setOnLoadCallback(drawChartGauge);

var chartLinesInterval;
var roastLogId;
var pastRoastData;
var roastStep = 0;
var roastTempMax;

//**************    Data access functions ********//
function getRoastTempMax( callback)  {
    $.getJSON('/getroasttempmax/', function( data ) {
        callback(data);
    });
};

function getCurrTemp(callback) {
    $.getJSON('/last/', function( data ) {
        callback( data );
    });
};

function getAllTemp(_roastLogId, callback) {
    $.getJSON('/all/', {'roastLogId': _roastLogId}, function( data ) {
        callback( data );
    });
};

function getInnitialState(callback) {
    $.getJSON('/init/', function( data )  {
        callback(data);
    });
};

//**************    Google gauge chart for temperature measurements ********//
function drawChartGauge() {
    var dataGauge = google.visualization.arrayToDataTable([
        ['Label', 'Value'],
        ['Temp', 0]
    ]);
    
    var optionsGauge = {
        //width: 315, height: 315,
        redFrom: 230, redTo: 250,
        yellowFrom: 205, yellowTo: 230,
        minorTicks: 5,
        majorTicks: ['0','50','100','150','200','250'],
        min:0, max: 250,
        animation: {
            easing:'inAndOut',
        }
    };

    var chartGauge = new google.visualization.Gauge(document.getElementById('chart_div'));

    chartGauge.draw(dataGauge, optionsGauge);
  
    setInterval(function() {
        getCurrTemp(function(data) {
            dataGauge.setValue(0, 1, data[0]);
            roastLogId = data[4];
            roastStep = data[2];
            document.images["jsbutton"].src = images[roastStep].src;
            $('#fire_button').prop('disabled', false).css('opacity',1);
            $('#toFirstCrackTime').val(data[5]);
            //if (roastStep > 1) {
                $('#fromFirstCrackTime').val(data[6]);
            //};
            if (data[1] != null) {
                $('#overallRoastTime').val(data[1]+':00');
            }
            else {
                $('#overallRoastTime').val('');
            };
        });
        chartGauge.draw(dataGauge, optionsGauge);
    }, 1*2000);
}

//**************    Line chart for roasting stats ********//
function drawChartLines(pRoastLogId, pChartId, pInterval) {
  
    var dataLine = google.visualization.arrayToDataTable([
          ['Time', 'Heating', 'Temperature', 'Temperature Set']
        ]);

    var materialOptions = {
        chart: {
          title: 'Roast temperature and heating chart'
        },
        width: 900,
        height: 300,
        series: {
          // Gives each series an axis name that matches the Y-axis below.
          0: {axis: 'Heating'},
          1: {axis: 'Temperature'},
          2: {axis: 'Temperature Set'}
        },
        axes: {
          // Adds labels to each axis; they don't have to match the axis names.
          y: {
            Temperature: {label: 'Temperature (Celsius)'},
            Heating: {label: 'Heating'}
          }
        }
      };

    var chartLine = new google.charts.Line(document.getElementById(pChartId));

    if (pInterval > 0) {
        chartLinesInterval = setInterval(function() {
            getAllTemp(pRoastLogId, function(data) {
                var tempData = new google.visualization.DataTable();
                tempData.addColumn('string', 'Time');
                tempData.addColumn('number', 'Heating');
                tempData.addColumn('number', 'Temperature');
                tempData.addColumn('number', 'Temperature Set');
                tempData.addRows( data );
                if ( data.length > 0 ) {
                    chartLine.draw(tempData, materialOptions);
                }
            });
        }, 1*5000);
    } else {
        getAllTemp(pRoastLogId, function(data) {
            var tempData = new google.visualization.DataTable();
            tempData.addColumn('string', 'Time');
            tempData.addColumn('number', 'Heating');
            tempData.addColumn('number', 'Temperature');
            tempData.addColumn('number', 'Temperature Set');
            tempData.addRows( data );
            if ( data.length > 0 ) {
                chartLine.draw(tempData, materialOptions);
            }
        });
        clearInterval(chartLinesInterval);
    }
}

// ************* Roasting button ************* 
var myimgobj = document.images["jsbutton"];


//function roastBTNclicked()
$('#fire_button').click( function() {
    $('#fire_button').prop('disabled', true).css('opacity',0.5);
    //Start roast clicked
    if ( roastStep === 0 ) {
        var tempSet = $('#roastMaxTempInput').val();
        var coffeeName = $('#coffeeNameInput').val();
        var roastSize = $('#roastSizeInput').val();
        var beansSize = $('input[name=beansSizeInput]:checked').val();
        var description = $('#descrInput').val();
        var after1stCrackTime = $('#roastTimeSetInput').val();
        if (coffeeName!='' && after1stCrackTime != '') {
            $.ajax({
                type:'get',
                url:'/start/',
                data: { "description": description,
                        "tempset":tempSet,
                        "coffeeName":coffeeName,
                        "roastSize":roastSize,
                        "beansSize":beansSize,
                        "after1stCrackTime":after1stCrackTime
                      },
                cache:false,
                async:true,
                error: function(request, status, error) {
                    alert(error);

                },
                success: function (data) {
                    disableForms();
                    /*roastStep++;
                    document.images["jsbutton"].src = images[roastStep].src;*/
                    roastLogId = data;
                    google.charts.setOnLoadCallback(drawChartLines(roastLogId, 'curve_chart', 5000));
                }
            });

        } else {
            $( "#messages_field" ).text( "Provide roast details!" ).show().fadeOut( 3000 );
        }
    }
    // 1st crack encountered
    else if ( roastStep === 1 )    {
        $.ajax({
            type:'get',
            url:'/firstcrack/',
            cache:false,
            async:true,
            error: function(request, status, error) {
                    alert(error);
                },
            success: function (data) {
                /*roastStep++;
                document.images["jsbutton"].src = images[roastStep].src;*/
            }
        });
    }
    else {
        $.ajax({
            type:'get',
            url:'/end/',
            data: {"roast_log_id" : roastLogId},
            cache:false,
            async:true,
            error: function(request, status, error) {
                    alert(error);
                },
            success: function (data) {
                $('#fire_button').prop('disabled', false).css('opacity',1);
                /*roastStep = 0;
                document.images["jsbutton"].src = images[roastStep].src;*/
                //$('#RoastTableContainer').jtable('load');
                //google.charts.setOnLoadCallback(drawChartLines(roastLogId, 'curve_chart', 0));
                drawChartLines(roastLogId, 'curve_chart', 0)
                enableForms();
                //$('#LoadRecordsButton').click();
                $('#pastRoastsNameFilter').val('');
                $('#pastRoastsFilterForm').keyup();
            }
        });
    }
    return true;
});

function handleMUp()
{
    roastBTNclicked();
    return true;
}

function disableForms() {
    $('#coffeeNameInput').attr('disabled', 'disabled');
    $('#roastSizeInput').attr('disabled', 'disabled');
    $('#beansSizeInput').attr('disabled', 'disabled');
    $("input[type='radio']").checkboxradio('disable');
    $('#descrInput').attr('disabled', 'disabled');
    $('#roastTimeSetInput').attr('disabled', 'disabled');
    //$(".ml-make-grey").css("color", "grey");
};

function enableForms() {
    $('#coffeeNameInput').attr('disabled', false);
    $('#roastSizeInput').attr('disabled', false);
    $('#beansSizeInput').attr('disabled', false);
    $("input[type='radio']").checkboxradio('enable');
    $('#descrInput').attr('disabled', false);
    $('#roastTimeSetInput').attr('disabled', false);
    $(".ml-make-grey").css("color", "black");
};

var images = new Array()
function preload() {
    for (i = 0; i < preload.arguments.length; i++) {
        images[i] = new Image()
        images[i].src = preload.arguments[i]
    }
}

//***************   On page load *****************//
$('document').ready(function () {
    preload(
        "btn_green.png",
        "btn_blue.png",
        "btn_red.png"
    );

    getInnitialState(function(data) {
        //0 s.roast_log_id,
        //1 s.roast_time,
        //2 s.temp_set,
        //3 s.status,
        //4 s.first_crack_time,
        //5 s.from_1crack_time,
        //6 l.coffee_name,
        //7 l.roast_size,
        //8 l.beans_size,
        //9 l.description,
        //10 s.after_1crack_set
        roastStep = data[3];
        document.images["jsbutton"].src = images[roastStep].src;
        $('#fire_button').prop('disabled', false).css('opacity',1);
        //all but initial state
        if (roastStep > 0) {
            disableForms();
            $('#roastMaxTempInput').val(data[2]);
            $('#coffeeNameInput').val(data[6]);
            $('#roastSizeInput').val(data[7]);
            var zm = function(_data) {
                if (_data==='large')
                    return 1;
                else return 0;
            };
            $("input[type='radio']:eq("+zm(data[8])+")").attr("checked", "checked");
			$("input[type='radio']").checkboxradio("refresh");
            $('#descrInput').val(data[9]);
            $('#roastTimeSetInput').val(data[10]);
            roastLogId = data[0];
            //google.charts.setOnLoadCallback(drawChartLines(roastLogId, 'curve_chart', 5000));
            drawChartLines(roastLogId, 'curve_chart', 5000)
        }
        else {
            // Initial maximum roasting temp from dictionary
            getRoastTempMax(function(data) {
                roastTempMax = data[0].toString();
                $('#roastMaxTempInput').val(data[0].toString());
            });
        }
    });

    // On submit event of max temperature Input field
    //$( '#roastMaxTempInput' ).keyup(function( event ) {
    $('#roastMaxTempInput').on('change', function() { //keyup
        $.ajax({
            type:'get',
                url:'/setroasttempmax/',
                data: {"tempset":$('#roastMaxTempInput').val()},
                cache:false,
                async:true,
                error: function(request, status, error) {
                        alert(error);
                },
                success: function (data) {
                    $( "#messages_field" ).text( "Max temp updated" ).show().fadeOut( 1500 );
                }
        });
        event.preventDefault();
    });

    // On submit event of Roast data <to be modified>
    $( '#pastRoastsFilterForm' ).submit(function( event ) {
        $('#coffeeNameInput').val(pastRoastData.coffee_name);
        $('#roastSizeInput').val(pastRoastData.roast_size);
        var zm = function(_data) {
            if (_data==='large')
                return 1;
            else return 0;
        };
        $("input[type='radio']:eq("+zm(pastRoastData.beans_size)+")").attr("checked", "checked");
        $("input[type='radio']").checkboxradio("refresh");
        $('#descrInput').val(pastRoastData.description);


            //$('#roastMaxTempInput').val(data[2]);
            //$('#roastTimeSetInput').val(data[10]);

        $( "#collapsible_roast_input" ).collapsible( "option", "collapsed", false );

        event.preventDefault();
    });

    $('#RoastTableContainer').jtable({
        title: 'Roasts list',
        actions: {
            listAction: '/roastslist/',
            updateAction: '/updatepastroast/',
            //createAction: '#',
            deleteAction: '/deleteroast/'
        },
        selecting: true,
        sorting: true,
        multiSorting: true,
        defaultSorting : 'date_time DESC',
        paging : true,
        fields: {
            id: {
                key: true,
                list: false
            },
            coffee_name: {
                title: 'Name',
                width: '35%'
            },
            date_time: {
                title: 'Date',
                width: '15%',
                edit : false//,
//                type:  'date',
//                displayFormat : 'yy-mm-dd H:i'
            },
            roast_size: {
                title: 'Size[g]',
                width: '10%'
            },
            beans_size: {
                title: 'Beans',
                width: '10%',
                options : { 'small':'Small', 'large':'Large'},
                type : 'radiobutton'
            },
            first_crack_time: {
                title: '1st crack',
                width: '10%',
                edit : false
            },
            crack_to_end: {
                title: 'From crack',
                width: '10%',
                edit : false
            },
            start_to_end: {
                title: 'Start to end',
                width: '10%',
                edit : false
            },
            description: {
                title: 'Description',
                sorting : false,
                type : 'textarea',
                list : false
            }
        },
        selectionChanged: function (event, data) {
            var $selectedRows = $('#RoastTableContainer').jtable('selectedRows');
            if ($selectedRows.length > 0) {
                //Show selected rows
                $selectedRows.each(function () {
                    var record = $(this).data('record');
                    google.charts.setOnLoadCallback(drawChartLines(record.id, 'curve_chart_past', 0));
                    pastRoastData = record;
                    $('#btnCopyRoast').button('enable');
                });
            } else {
                $('#curve_chart_past').html('');
                $('#btnCopyRoast').button('disable');
            }
        }
    });


    //Re-load records when user click 'load records' button.
    $('#pastRoastsFilterForm').keyup(function (e) { //bylo submit
//	console.log($('#pastRoastsNameFilter').val());
        e.preventDefault();
        $('#RoastTableContainer').jtable('load', {
            jtNameFilter: $('#pastRoastsNameFilter').val()
        });
    });

    $('#btnTurnOff').click(function(e) {
        $.ajax({
            type:'get',
            url:'/poweroff/',
            error: function(request, status, error) {
                    alert(error);
                }
            });
    });

    //Load all records when page is first shown
//    $('#LoadRecordsButton').click();

    $('#RoastTableContainer').jtable('load');
    // Innitial parameters loading after page refresh

});
