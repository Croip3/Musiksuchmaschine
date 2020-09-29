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
    <script src='js/main.js'></script>
    <title>Musiksuchmaschine</title>
</head>

<body onload="showFilterSliderValue()">
    <div class="searcharea">
        <div class="heading">
            <h2>Musiksuchmaschine</h2>

            <form action="search.php" method="GET">

                <div id="searchbar">
                    <img alt="" id="glass" src="glass.png">
                    <input type="text" id="search" name="search" spellcheck="false">
                </div>

                <!-- echo sql query -->
                <!--<input type="submit" value="echo search array">-->

            </form>


            <input type='button' onClick='search()' value="Suchen">
        </div>

        <div class="searchfilter">
            <form action="">
                <div class="grid-container">
                    <div class="title">
                        <p style="color: #FF0000; font-weight: bold;">INOP</p>

                        <label for="title">Titel</label>
                        <input type="text" name="title" id="searchtitle">
                    </div>
                    <div class="artist">
                        <p style="color: #FF0000; font-weight: bold;">INOP</p>

                        <label for="artist">Interpret</label>
                        <input type="text" name="artist" id="searchartist">
                    </div>
                    <div class="genre">
                        <p style="color: #FF0000; font-weight: bold;">INOP</p>

                        <label for="genre">Genre</label><br>
                        <select name="genre" id="selectgenre">
                            <option value="genre1">Rock</option>
                            <option value="genre2">Pop</option>
                            <option value="genre3">Hip-Hop</option>
                        </select>
                    </div>
                    <div class="year">
                        <p style="color: #FF0000; font-weight: bold;">INOP</p>

                        <label for="year">Jahr</label><br>
                        <select name="year" id="selectyear">
                            <option value="year1">2000</option>
                            <option value="year2">2001</option>
                            <option value="year3">2003</option>
                        </select>
                    </div>
                    <div class="epoch">
                        <p style="color: #FF0000; font-weight: bold;">INOP</p>

                        <label for="epoch">Epoche</label><br>
                        <select name="epoch" id="selectepoch">
                            <option value="epoch1">Klassik</option>
                            <option value="epoch2">Romantik</option>
                            <option value="epoch3">Moderne</option>
                        </select>
                    </div>

                    <?php
                    class Filter extends ViewResults
                    {
                        public function filterTonart()
                        {
                            //select Tonart
                            echo '<div class="key">';
                            echo '<label for="key">Tonart</label><br>';
                            $getKeys = new ViewResults;
                            $keys = $getKeys->key();
                            echo '<select name="key" id="selectkey">';
                            foreach ($keys as $key) {
                                echo '<option value="' . $key["Tonart"] . '">' . $key["Tonart"] . '</option>';
                            }
                            echo '</select>';
                            echo '</div>';
                        }

                        public function filterTempo()
                        {
                            //sliders minimum/maximum speed in BPM
                            echo '<div class="tempo" >';
                            echo "<p>Tempo</p>";
                            echo "<label for='tempomin'>mindestens</label>";
                            $tempo = new ViewResults;
                            echo "<input type='range' name='tempomin' id='tempomin' min='" . $tempo->minTempo() . "' max='" . $tempo->maxTempo() . "' value='" . $tempo->minTempo() . "'>";
                            echo "<p><span id='tempominValue'></span> BPM</p><br>";
                            echo "<label for='tempomax'>maximal</label>";
                            echo "<input type='range' name='tempomax' id='tempomax' min='" . $tempo->minTempo() . "' max='" . $tempo->maxTempo() . "' value='" . $tempo->maxTempo() . "'>";
                            echo "<p><span id='tempomaxValue'></span> BPM</p>";
                            echo "</div>";
                        }

                        public function filterLaenge()
                        {
                            //slider minimum/maximum length in seconds
                            echo '<div class="length">';
                            echo '<p>Länge</p>';
                            echo '<label for="lengmin">mindestens</label>';
                            $laenge = new ViewResults;
                            echo '<input type="range" name="lengmin" id="lengmin" min="' . $laenge->minLaenge() . '" max="' . $laenge->maxLaenge() . '" value="' . $laenge->minLaenge() . '">';
                            echo '<p><span id="laengeminValue"></span> Sekunden</p><br>';
                            echo '<label for="lengmax">maximal</label>';
                            echo '<input type="range" name="lengmax" id="lengmax" min="' . $laenge->minLaenge() . '" max="' . $laenge->maxLaenge() . '" value="' . $laenge->maxLaenge() . '">';
                            echo '<p><span id="laengemaxValue"></span> Sekunden</p>';
                            echo '</div>';
                        }
                    }

                    $filter = new Filter;
                    $filter->filterTempo();
                    $filter->filterLaenge();
                    $filter->filterTonart();
                    ?>

                    <div class="date">
                        <p style="color: #FF0000; font-weight: bold;">INOP</p>

                        <p>Uploaddatum</p>
                        <label for="datemin">von</label>
                        <input type="date" name="datemin" id="datemin">
                        <label for="datemax">bis</label>
                        <input type="date" name="datemax" id="datemax">
                    </div>
                </div>

                <?php

                ?>

                <input type='button' onClick='setFilter()' value="Bestätigen">
                <button>Filter löschen</button>
            </form>
        </div>
    </div>




</body>

</html>
