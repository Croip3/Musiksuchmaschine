var results
var resultsLength

function retrieveResults(search){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        if (this.responseText.trim() != ""){
            results = JSON.parse(this.responseText)
            console.log(results)
            resultsLength = results.length;
            var retDiv = $('<div></div>')
            for (var i = 0; i < results.length; ++i){
                retDiv.append(renderCard(results[i]))
            }
            $(".results").html(retDiv)
        } else {
            $(".results").html("Keine Ergebnisse gefunden!")
        }
      }
    };
    xmlhttp.open("GET", "search.php?search=" + search, true);
    xmlhttp.send();
}


function renderCard(obj) {
    console.log(obj.Tonart);
    function GetFilename(url){
        if (url)
        {
            var m = url.toString().match(/.*\/(.+?)\./);
            if (m && m.length > 1)
            {
                return m[1];
            }
        }
        return "";
    }

    var container = $("<a></a>").attr({id : obj.id, class : 'result-card', href: obj.Url})
    console.log(obj.Titel.trim())    
    if (String(obj.Titel).trim() == "") {
        titleString = GetFilename(obj.url)
    } else {
        titleString = obj.Titel
    }
    var title = $('<h3></h3>').html(titleString)
    var url = $('<div></div>').html(obj.Url).addClass("div-url")
    var key = $('<div></div>').html(obj.Tonart)
    var tempo = $('<div></div>').html("BPM "+obj.Tempo)
    var time = new Date(parseInt(obj.Laenge) * 1000).toISOString().substr(11, 8)
    var timediv = $('<div></div>').html(time)
    var artist = $('<div></div>').html(obj.Kuenstler)
    var instruments = $("<div></div>")
    for (var i = 0; i < obj.Instrumente.length; i++){
        instruments.append($('<div></div>').html(obj.Instrumente[i].anzahl + ' x ' + obj.Instrumente[i].name))
    }
    
    container.append(title, url, key, tempo, timediv, artist, instruments)
    console.log(container.html());
    return container
    

}

function search() {
    str = $('#search').val()
    retrieveResults(str)
    
}

//Filter

var sliderTempomin;
var sliderTempomax;
var sliderLaengemin;
var sliderLaengemax;
var selectKey;



function showFilterSliderValue(){
    //print start values for all sliders
    document.getElementById("tempominValue").innerHTML = document.getElementById("tempomin").value;
    document.getElementById("tempomaxValue").innerHTML = document.getElementById("tempomax").value;
    document.getElementById("laengeminValue").innerHTML = document.getElementById("lengmin").value;
    document.getElementById("laengemaxValue").innerHTML =  document.getElementById("lengmax").value;

    //update printed slider Values when changed
    document.getElementById("tempomin").oninput = function() {
        document.getElementById("tempominValue").innerHTML = this.value;
    }
    document.getElementById("tempomax").oninput = function() {
        document.getElementById("tempomaxValue").innerHTML = this.value;
    }
    document.getElementById("lengmin").oninput = function() {
        document.getElementById("laengeminValue").innerHTML = this.value;
    }
    document.getElementById("lengmax").oninput = function() {
        document.getElementById("laengemaxValue").innerHTML = this.value;
    }
}

function setFilter(){

    //read Tempo slider
    sliderTempomin = document.getElementById("tempomin").value;
    sliderTempomax = document.getElementById("tempomax").value;

    //read Länge slider
    sliderLaengemin = document.getElementById("lengmin").value;
    sliderLaengemax = document.getElementById("lengmax").value;
    
    //read selected Tonart
    selectKey = document.getElementById("selectkey").value;

    for(var i = 0; i<results.length; i++){
        filter(results[i]);
    }
    filterConsoleLog();
}

function filterConsoleLog(){
    console.log("minTempo: " + sliderTempomin);
    console.log("maxTempo: " + sliderTempomax);

    console.log("minLänge: " + sliderLaengemin);
    console.log("maxLänge: " + sliderLaengemax);

    console.log("Tonart: " + selectKey);    
}

function filter(obj){
    document.getElementById(obj.id).style.display = 'block';
    //deleteFilter();
    if(selectKey != "alle"){
        if(obj.Tonart != selectKey){
            document.getElementById(obj.id).style.display = 'none';
            //console.log("key");
        }
    }
    if(parseInt(obj.Tempo) < parseInt(sliderTempomin) || parseInt(obj.Tempo) > parseInt(sliderTempomax)){
        document.getElementById(obj.id).style.display = 'none';
        //console.log("speed");
    }
    if((parseInt(obj.Laenge) < parseInt(sliderLaengemin)) || (parseInt(obj.Laenge) > parseInt(sliderLaengemax))){
        document.getElementById(obj.id).style.display = 'none';
        
    }    
    
    //document.getElementById(obj.id).style.display = 'block';
}

function deleteFilter(){ 

    for (i = 0; i < results.length; ++i){
        document.getElementById(results[i].id).style.display = 'block';
    }
}
