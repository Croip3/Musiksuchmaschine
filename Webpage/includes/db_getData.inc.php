<?php 
class SearchDB extends DatabaseConnection{
        public function searchData(){
            $search = '%'.$_POST['search'].'%';
            echo 'searchbar: '.$search.'<br>';
           
            $res = $this->connect()->query("SELECT * FROM musikstueck INNER Join kuenstler ON musikstueck.Kuenstler_ID = kuenstler.id WHERE musikstueck.Genre like '$search' OR musikstueck.Epoche like '$search' OR musikstueck.Titel like '$search' OR kuenstler.name like '$search' ");
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