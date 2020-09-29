<?php 
class SearchDB extends DatabaseConnection{
        public function searchData(){
            $search = '%'.$_GET['search'].'%';
           
            $res = $this->connect()->query("SELECT * FROM musikstueck WHERE Genre like '$search' OR Epoche like '$search' OR Titel like '$search' OR Url LIKE '$search' OR Sonstiges LIKE '$search' ");
            $num = $res->num_rows;
            if($num > 0){
                while($row = $res->fetch_assoc()){
                    $data[] = $row;
                }
                return $data;
                
            }
        }

        public function getArtist($id) {
            $res = $this->connect()->query("SELECT kuenstler.name FROM musikstueck JOIN kuenstler ON musikstueck.Kuenstler_ID = kuenstler.id WHERE musikstueck.id = $id");
            $num = $res->num_rows;
            if($num > 0){
                while($row = $res->fetch_assoc()){
                    $data[] = $row;
                }
                return $data;
                
            }
        }

        public function getInstruments($id) {
            $res = $this->connect()->query("SELECT instrument.name FROM beinhaltet JOIN musikstueck ON musikstueck.id = beinhaltet.stueckid JOIN instrument ON beinhaltet.instrumentid = instrument.id WHERE musikstueck.id = $id");
            $num = $res->num_rows;
            if($num > 0){
                while($row = $res->fetch_assoc()){
                    $data[] = $row;
                }
                return $data;                
            }
        }

        public function getTempo(){
            $sql = "SELECT Tempo FROM `musikstueck` ORDER BY Tempo*1";
            $res = $this->connect()->query($sql);

            $num = $res->num_rows;
            if($num > 0){
                while($row = $res->fetch_assoc()){
                    $data[] = $row;
                }
                return $data;                
            }
        }

        public function getLaenge(){
            $sql = "SELECT laenge FROM `musikstueck` ORDER BY laenge*1";
            $res = $this->connect()->query($sql);

            $num = $res->num_rows;
            if($num > 0){
                while($row = $res->fetch_assoc()){
                    $data[] = $row;
                }
                return $data;                
            }
        }

        protected function getKey(){
            $sql = "SELECT DISTINCT Tonart FROM `musikstueck`";
            $res = $this->connect()->query($sql);

            $num = $res->num_rows;
            if($num > 0){
                while($row = $res->fetch_assoc()){
                    $data[] = $row;
                }
                return $data;                
            }
        }
    }
?>