var results
function retrieveResults(search){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        // results = JSON.parse(this.responseText)
        results = JSON.parse(this.responseText)
        console.log(results)
        for (i = 0; i < results.length; ++i){
            $('body').append(renderCard(results[i]))
        }
      }
    };
    xmlhttp.open("GET", "search.php?search=" + search, true);
    xmlhttp.send();
}

function renderCard(obj) {
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

    container = $("<a></a>").attr({id : obj.id, class : 'result-card', href: obj.Url})
    console.log(obj.Titel.trim())    
    if (String(obj.Titel).trim() == "") {
        titleString = GetFilename(obj.url)
    } else {
        titleString = obj.Titel
    }
    title = $('<h3></h3>').html(titleString)
    key = $('<div></div>').html(obj.Tonart)
    tempo = $('<div></div>').html(obj.Tempo)
    time = new Date(parseInt(obj.Laenge) * 1000).toISOString().substr(11, 8)
    timediv = $('<div></div>').html(time)
    artist = $('<div></div>').html(obj.Kuenstler)
    instruments = $("<div></div>")
    for (x in obj.Instrumente){
        instruments.append($('<div></div>').html(x))
    }
    container.append(title, key, tempo, timediv, artist, instruments)
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

function setFilter(){
    sliderTempomin = document.getElementById("tempomin").value;
    sliderTempomax = document.getElementById("tempomax").value;

    filterResults();
}

function filterResults(){
    console.log(sliderTempomin);
    console.log(sliderTempomax);
}