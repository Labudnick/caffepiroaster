var myimgobj = document.images["jsbutton"];
var jsbutton_clicked = 0;
// -----------  get data result  ----------- 
function getLastTempResult() {
    $.getJSON('/last/', function( data ) {
        if (typeof data != 'undefined') {
            ar=data[0].toString().split(".");
            $("#sens_temp").html(  ar[0]  );
            $("#sens_temp_decimal").html(  ar[1]  );
        }
    });
}

// ----------- charts  ----------- 
google.load('visualization', '1', {packages: ['corechart', 'line']});
google.setOnLoadCallback(drawCurveTypes);

function drawCurveTypes() {
    $.getJSON('/all/', function( jsondata ) {
        if (typeof jsondata != 'undefined') {
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Hour');
            data.addColumn('number', 'Temperature');
            data.addColumn('number', 'Heating');
            data.addRows( jsondata );

            var options = {
                backgroundColor: { fill:'transparent' },
              colors: ['#55f', '#5f5'],

              curveType: 'function',
              hAxis: {
                  title: 'Process time',
              },
              vAxis: {
                  title: 'Celsius Degrees',
                  format:'##.#',
              },
            };

            var chart = new google.visualization.LineChart(document.getElementById('chartdiv'));
            chart.draw(data, options);
        }
    });
}

// ----------- auto refresh  ----------- 
ChartCounterDelay=0;
setInterval(function() {
    getLastTempResult();
    ChartCounterDelay++;
    if ( ChartCounterDelay == 5  ) {
        ChartCounterDelay=0;
        drawCurveTypes();
    }
}, 1 * 1000); // n * 1000 milsec

$( window ).load(function() {
    getLastTempResult();
});

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
   	});
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
function changeImageBack()
{
    document.images["jsbutton"].src = "btn_green.png";
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
