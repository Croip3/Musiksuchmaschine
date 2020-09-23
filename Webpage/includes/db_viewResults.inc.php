<?php 
class ViewResults extends SearchDB{
        public function __construct(){
            $datas = $this->searchData();
            if (is_array($datas) || is_object($datas)){
                echo "#######################################gefundene Daten: <br>";
                foreach($datas as $data){
                    echo $data['id']." ";
                    echo $data['Tempo']." ";
                    echo $data['Genre']." ";
                    echo $data['Uploaddatum']." ";
                    echo $data['Laenge']." ";
                    echo $data['Jahr']." ";
                    echo $data['Tonart']." ";
                    echo $data['Epoche']." ";
                    echo $data['Titel']." ";
                    echo $data['Url']." ";
                    echo $data['Kuenstler_ID']."<br>";
                }
            }else{
                echo "keine Daten gefunden";
            }
        }
    }
?>