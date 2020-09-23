<?php 
class SearchDB extends DatabaseConnection{
        public function searchData(){
            $search = '%'.$_POST['search'].'%';
            echo 'searchbar: '.$search.'<br>';
           
            $res = $this->connect()->query("SELECT * FROM musikstueck WHERE Genre like '$search' OR Epoche like '$search' OR Titel like '$search' ");
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