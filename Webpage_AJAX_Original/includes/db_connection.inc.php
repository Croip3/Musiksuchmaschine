<?php 
    class DatabaseConnection {

        private $ip;
        private $username;
        private $password;
        //$conn;
        private $db;

        public function connect() {
            $this->ip = "localhost:3306";
            $this->username = "root";
            //$password = "3X2SDuKU8v5";
            $this->password = "";
            $this->db = "musiksuchmaschine";


            $conn  = new mysqli($this->ip, $this->username, $this->password, $this->db);
            //mysqli_select_db($this->conn, "spardose");
            //$res = mysqli_query($conn, "select * from dose");
            //$num = mysqli_num_rows($res);
            //echo "$num Datensätze gefunden<br />";

            if ($conn->connect_error) {
                die("connection failed: " . $conn->connect_error);
            } else {
                // echo "connected successfully<br>";
            }
        
            return $conn;
        }
    }    
?>