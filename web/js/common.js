// ************* Current temperature chart *************
google.charts.load('current', {'packages':['gauge', 'line']});
google.charts.setOnLoadCallback(drawChartGauge);

var chartLinesInterval;
var roastLogId;

//**************    Data access functions ********//
function getRoastTempMax( callback)  {
    $.getJSON('/getroasttempmax/', function( data ) {
            callback(data);
    });
}

function getCurrTemp(callback) {
    $.getJSON('/last/', function( data ) {
            callback( data );
    });
}

function getAllTemp(callback) {
    $.getJSON('/all/', function( data ) {
        callback( data );
    });
}

//**************    Gauge chart for temperature measurements ********//
function drawChartGauge() {
    var dataGauge = google.visualization.arrayToDataTable([
        ['Label', 'Value'],
        ['Temp', 20]
    ]);
    
    var optionsGauge = {
        width: 300, height: 300,
        redFrom: 230, redTo: 250,
        yellowFrom: 205, yellowTo: 230,
        minorTicks: 5,
        majorTicks: ['20', '100', '150', '200', '250'],
        min:20, max: 250
    };

    var chartGauge = new google.visualization.Gauge(document.getElementById('chart_div'));

    chartGauge.draw(dataGauge, optionsGauge);
  
    setInterval(function() {
        var currTime;
        getCurrTemp(function(data) {
            dataGauge.setValue(0, 1, data[0].toString());
            if (jsbutton_clicked>0) {
                $('#timer').html('<h2>' + data[1].toString() + '</h2>');
                if (jsbutton_clicked==2) {
                    $('#1st_crack_label').html('<h2>Since 1st crack</h2>');
                    $('#1st_crack_timer').html('<h2>' + data[5].toString() + '</h2>');
                };
            };

        });
        chartGauge.draw(dataGauge, optionsGauge);
    }, 1*1000);
}

//**************    Line chart for roasting stats ********//
function drawChartLines() {
  
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

    var chartLine = new google.charts.Line(document.getElementById('curve_chart'));

    //chartLine.draw(dataLine, materialOptions);
    
    chartLinesInterval = setInterval(function() {
        getAllTemp(function(data) {
            var tempData = new google.visualization.DataTable();
            tempData.addColumn('string', 'Time');
            tempData.addColumn('number', 'Heating');
            tempData.addColumn('number', 'Temperature');
            tempData.addColumn('number', 'Temperature Set');
            tempData.addRows( data );
            chartLine.draw(tempData, materialOptions);
        });
    }, 1*5000);
}


// ************* Roasting button ************* 
var myimgobj = document.images["jsbutton"];
var jsbutton_clicked = 0;

function roastBTNclicked()
{
    //Start roast clicked
    if ( jsbutton_clicked === 0 ) {
        var tempSet = $('#roastTempMaxInput').val();
        var coffeeName = $('#coffeeNameInput').val();
        var roastSize = $('#roastSizeInput').val();
        var beansSize = $('input[name=beansSize]:checked').val();
        var description = $('#descriptionInput').val();
        if (coffeeName!='') {
            $.ajax({
                type:'get',
                url:'/start/',
                data: { "description": description,
                        "tempset":tempSet,
                        "coffeeName":coffeeName,
                        "roastSize":roastSize,
                        "beansSize":beansSize
                      },
                cache:false,
                async:true,
                error: function(request, status, error) {
                    alert(error);
                },
                success: function (data) {
                    $("fieldset").attr('disabled', 'disabled');
                    jsbutton_clicked++;
                    document.images["jsbutton"].src = images[jsbutton_clicked].src;
                    $('#timer').html('<h1>00:00</h1>');
                }
            });
            google.charts.setOnLoadCallback(drawChartLines);
        } else {
            $( "span" ).text( "Provide roast details!" ).show().fadeOut( 3000 );
        }
        console.log(jsbutton_clicked);
    }
    // 1st crack encountered
    else if ( jsbutton_clicked === 1 )    {
        $.ajax({
            type:'get',
            url:'/firstcrack/',
            cache:false,
            async:true,
            error: function(request, status, error) {
                    alert(error);
                },
            success: function (data) {
                jsbutton_clicked++;
                document.images["jsbutton"].src = images[jsbutton_clicked].src;
                clearInterval(chartLinesInterval);
            }
        });
    }
    // Stop roast clicked
    else {
        $.ajax({
            type:'get',
            url:'/end/',
            cache:false,
            async:true,
            error: function(request, status, error) {
                    alert(error);
                },
            success: function (data) {
                jsbutton_clicked = 0;
                document.images["jsbutton"].src = images[jsbutton_clicked].src;
                $("#roastDetailsForm").trigger('reset');
                $("fieldset").removeAttr('disabled');
                $('#timer').html('<h1>00:00</h1>');
                clearInterval(chartLinesInterval);
            }
        });
        console.log(jsbutton_clicked);
    }
    return true;
}

function handleMUp()
{
    roastBTNclicked();
    return true;
}

function powerOffBtnUp() {
    $.ajax({
        type:'get',
        url:'/poweroff/',
        error: function(request, status, error) {
                alert(error);
            }
    });
}

var images = new Array()
function preload() {
    for (i = 0; i < preload.arguments.length; i++) {
        images[i] = new Image()
        images[i].src = preload.arguments[i]
    }
}



//***************   On page load *****************//
$('document').ready(function () {
    getRoastTempMax(function(data) {
        $('#roastTempMaxInput').val(data[0].toString());
    });
    $( "#roastTempMaxForm" ).submit(function( event ) {
        $.ajax({
            type:'get',
                url:'/setroasttempmax/',
                data: {"tempset":$('#roastTempMaxInput').val()},
                cache:false,
                async:true,
                error: function(request, status, error) {
                        alert(error);
                },
                success: function (data) {
                    $( "span" ).text( "Updated" ).show().fadeOut( 1500 );
                }
        });
        event.preventDefault();
    });
    preload(
        "btn_green.png",
        "btn_blue.png",
        "btn_red.png"
    );
    document.images["jsbutton"].src = images[0].src;
});