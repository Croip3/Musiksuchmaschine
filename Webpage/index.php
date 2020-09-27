<?php 
    require 'includes/db_connection.inc.php';
    require 'includes/db_getData.inc.php';
    require 'includes/db_viewResults.inc.php';
?>

<!DOCTYPE html>
<html lang="de">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="main.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src ='js/main.js'></script>
    <title>Musiksuchmaschine</title>
</head>

<body>
    <h2>Musiksuchmaschine</h2>
    
    <form action="search.php" method="GET">

        <div id="searchbar">
            <img alt="" id="glass" src="glass.png">
            <input type="text" id="search" name="search" spellcheck="false">
        </div>
        <input type="submit" value="Suchen PHP">   
    
    </form>

    <input type='button' onClick='search()' value="Suchen">

        <div class="searchfilter">
            <form action="">
                <div class="grid-container">
                    <div class="title">
                        <label for="title">Titel</label>
                        <input type="text" name="title" id="searchtitle">
                    </div>
                    <div class="artist">
                        <label for="artist">Interpret</label>
                        <input type="text" name="artist" id="searchartist">
                    </div>
                    <div class="genre">
                        <label for="genre">Genre</label><br>
                        <select name="genre" id="selectgenre">
                            <option value="genre1">Rock</option>
                            <option value="genre2">Pop</option>
                            <option value="genre3">Hip-Hop</option>
                        </select>
                    </div>
                    <div class="year">
                        <label for="year">Jahr</label><br>
                        <select name="year" id="selectyear">
                            <option value="year1">2000</option>
                            <option value="year2">2001</option>
                            <option value="year3">2003</option>
                        </select>
                    </div>
                    <div class="epoch">
                        <label for="epoch">Epoche</label><br>
                        <select name="epoch" id="selectepoch">
                            <option value="epoch1">Klassik</option>
                            <option value="epoch2">Romantik</option>
                            <option value="epoch3">Moderne</option>
                        </select>
                    </div>
                    <div class="key">
                        <label for="key">Tonart</label><br>
                        <select name="key" id="selectkey">
                            <option value="key1">G-Dur/e-Moll</option>
                            <option value="key2">C-Dur/a-Moll</option>
                            <option value="key3">F-Dur/d-Moll</option>
                        </select>
                    </div>
                    <?php
                        class FilterData extends ViewResults{
                            public function filterData() {
                                /*$sql = "SELECT laenge FROM `musikstueck` ORDER BY CAST(laenge AS INT)";
                                $res = $this->connect()->query($sql);

                                $num = $res->num_rows;
                                if($num > 0){
                                    while($row = $res->fetch_assoc()){
                                        $data[] = $row;
                                    }

                                    $datas = $this->searchData();
                                    echo $minTempo = $datas[0]['id'];
                                    echo $maxTempo = $datas[count($datas)-1]['id'];
                                }*/                     
                    
                                echo '<div class="tempo">';
                                    echo "<p>Tempo</p>";
                                    echo "<label for='tempomin'>mindestens</label>";
                                    $minTempo = new ViewResults;                                                                        
                                    $maxTempo = new ViewResults;
                                    echo "<input type='range' name='tempomin' id='tempomin' min='".$minTempo->minTempo()."' max='".$maxTempo->maxTempo()."' value='".$minTempo->minTempo()."'>";
                                    echo "<p><span id='demo1'></span> BPM</p>";
                                    echo "<label for='tempomax'>maximal</label>";
                                    echo "<input type='range' name='tempomax' id='tempomax' min='".$minTempo->minTempo()."' max='".$maxTempo->maxTempo()."' value='".$maxTempo->maxTempo()."'>";
                                    echo "<p><span id='demo2'></span> BPM</p>";
                                echo "</div>";
                            }
                        }

                        $filter = new FilterData;
                        $filter->filterData();
                    ?>
                    <!--<div class="tempo">
                        <p>Tempo</p>
                        <label for="tempomin">mindestens</label>
                        <input type="range" name="tempomin" id="tempomin" min="1" max="400" value="1">
                        <p><span id="demo1"></span> BPM</p>
                        <label for="tempomax">maximal</label>
                        <input type="range" name="tempomax" id="tempomax" min="1" max="400" value="400">
                        <p><span id="demo2"></span> BPM</p>
                    </div>-->
                    <div class="length">
                        <p>Länge</p>
                        <label for="lengmin">mindestens</label>
                        <input type="range" name="lengmin" id="lengmin" min="1" max="60" value="1">
                        <p><span id="demo3"></span> Minuten</p>
                        <label for="lengmax">maximal</label>
                        <input type="range" name="lengmax" id="lengmax" min="1" max="60" value="60">
                        <p><span id="demo4"></span> Minuten</p>
                    </div>
                    <div class="date">
                        <p>Uploaddatum</p>
                        <label for="datemin">von</label>
                        <input type="date" name="datemin" id="datemin">
                        <label for="datemax">bis</label>
                        <input type="date" name="datemax" id="datemax">
                    </div>
                </div>
                
                <input type='button' onClick='setFilter()' value="Bestätigen">
                <button>Filter löschen</button>
            </form>            
        </div>

    


</body>

</html>
