// ************* Current temperature chart *************
// google.charts.load('current', {'packages':['gauge']});
google.charts.load('current', {'packages':['gauge', 'line']});  //'corechart'
google.charts.setOnLoadCallback(drawChartGauge);

function getCurrTemp() {
    $.getJSON('/last/', function( data ) {
        if (typeof data != 'undefined') {
            currtemp=data[0].toString()       
        }
    });
    return currtemp;
}

function getAllTemp() {
    $.getJSON('/all/', function( jsondata ) {
        if (typeof jsondata != 'undefined') {
            data = new google.visualization.DataTable();
            data.addColumn('string', 'Time');
            data.addColumn('number', 'Temperature');
            data.addColumn('number', 'Heating');
            data.addRows( jsondata );
        }
    });
    return data;
}

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
        dataGauge.setValue(0, 1, getCurrTemp());
        chartGauge.draw(dataGauge, optionsGauge);
        RoastTempMax = getRoastTempMax();
        arg = getRoastTempMax();
        $("roasttempmaxfield").html(arg)
    }, 1*1000);
    
}

function drawChartLines() {
  
    var dataLine = google.visualization.arrayToDataTable([
          ['Time', 'Temperature', 'Heating'],
          ['0:00', 20, 0]
        ]);

//     var optionsLine = {
//         title: 'Roast temperature chart',
//         curveType: 'function',
//         legend: { position: 'bottom' }
//     };

    var materialOptions = {
        chart: {
          title: 'Roast temperature and heating chart'
        },
        width: 900,
        height: 300,
        series: {
          // Gives each series an axis name that matches the Y-axis below.
          0: {axis: 'Temperature'},
          1: {axis: 'Heating'}
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

    chartLine.draw(dataLine, materialOptions);
    
    setInterval(function() {
        chartLine.draw(getAllTemp(), materialOptions);
    }, 1*1000);
        
}


// ************* Roasting button ************* 
var myimgobj = document.images["jsbutton"];
var jsbutton_clicked = 0;

function roastBTNclicked()
{
    if ( jsbutton_clicked == 0 ) {
        document.images["jsbutton"].src= "btn_red.png";
        jsbutton_clicked = 1;
        $.ajax({
            type:'get',
            url:'/start/',
            cache:false,
            async:true,
            error: function(request, status, error) {
                alert(error);
            }
        })
	google.charts.setOnLoadCallback(drawChartLines);
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
            }
        });

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

function getRoastTempMax()
{
    $getJSON('/roasttempmax/', function( data ) {
        if (typeof data != 'undefined') {
            roastTempMax = data[0]
        }
    });
    return roastTempMax;
}
