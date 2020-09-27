

<?php

class ViewResults extends SearchDB{
        public function __construct(){
            $datas = $this->searchData();
            if (is_array($datas) || is_object($datas)){
                echo "gefundene Daten: <br>";

                echo '<table>';
                    echo '<tr>';
                        echo '<td>Titel</td>';
                        echo "<td>Kuenstler</td>";
                        echo "<td>Url</td>";
                        echo "<td>Genre</td>";
                        echo "<td>Epoche</td>";
                    echo "</tr>";

                foreach($datas as $data){
                    echo '<tr>';
                        echo "<td>".$data['Titel']."</td>";
                        echo "<td>".$data['name']."</td>";
                        echo "<td><a href=".$data['Url'].">".$data['Url']."</a></td>";
                        echo "<td>".$data['Genre']."</td>";
                        echo "<td>".$data['Epoche']."</td>";
                    echo "</tr>";

                        /*echo $data['id']." ";
                        echo $data['Tempo']." ";
                        echo $data['Genre']." ";
                        echo $data['Uploaddatum']." ";
                        echo $data['Laenge']." ";
                        echo $data['Jahr']." ";
                        echo $data['Tonart']." ";
                        echo $data['Epoche']." ";
                        echo $data['Titel']." ";
                        echo "<a href=".$data['Url'].">".$data['Url']."</a>";
                        echo $data['name']."<br>";*/
                }
                echo "</table>";
            }else{
                echo "keine Daten gefunden";
            }
        }
    }
?>
