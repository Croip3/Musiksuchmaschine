<?php 
    class DatabaseConnection {

        private $ip;
        private $username;
        private $password;
        private $db;

        public function connect() {
            $this->ip = "localhost:3306";
            $this->username = "root";
            $password = "3X2SDuKU8v5";
            $this->db = "musiksuchmaschine";


            $conn  = new mysqli($this->ip, $this->username, $this->password, $this->db);

            if ($conn->connect_error) {
                die("connection failed: " . $conn->connect_error);
            } else {
                echo "connected successfully<br>";
            }
        
            return $conn;
        }
    }    
?>