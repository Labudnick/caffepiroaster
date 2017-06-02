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
            //console.log(data[1].toString());
            if (jsbutton_clicked==1) {
                $('#timer').html('<h1>' + data[1].toString() + '</h1>');
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
    if ( jsbutton_clicked == 0 ) {
        var tempSet = $('#roastTempMaxInput').val();
        var coffeeName = $('#coffeeNameInput').val();
        var roastSize = $('#roastSizeInput').val();
        var beansSize = $('input[name=beansSize]:checked').val();
        var description = $('#descriptionInput').val();
        if (coffeeName!='') {
            document.images["jsbutton"].src= "btn_red.png";
            jsbutton_clicked = 1;
            $('#timer').html('<h1>00:00</h1>');

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
                }
            });
            google.charts.setOnLoadCallback(drawChartLines);
        } else {
            document.images["jsbutton"].src = "btn_green.png";
            $( "span" ).text( "Provide roast details. At least coffee name!" ).show().fadeOut( 3000 );
        }
    }
    else {
        document.images["jsbutton"].src= "btn_green.png";
        jsbutton_clicked = 0;
        $.ajax({
            type:'get',
            url:'/end/',
            cache:false,
            async:true,
            error: function(request, status, error) {
                    alert(error);
                },
            success: function (data) {
                $("#roastDetailsForm").trigger('reset');
                $("fieldset").removeAttr('disabled');
            }
        });
        clearInterval(chartLinesInterval);
    }
    return true;
}

function handleMDown()
{
    document.images["jsbutton"].src = "btn_red.png";
    return true;
}

function handleMUp()
{
    roastBTNclicked();
    return true;
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
});