<?php 
    class DatabaseConnection {

        protected $ip;
        protected $username;
        protected $password;
        protected $con;
        protected $db;

        public function __construct() {
            $ip = "141.57.21.72:3306";
            $username = "root";
            $password = "3X2SDuKU8v5";
            $db = "musiksuchmaschine";


            $this->con  = mysqli_connect($ip, $username, $password, $db);
            //mysqli_select_db($this->conn, "spardose");
            //$res = mysqli_query($conn, "select * from dose");
            //$num = mysqli_num_rows($res);
            //echo "$num Datensätze gefunden<br />";

            if ($this->con->connect_error) {
                die("Connection failed: " . $con->connect_error);
            } else {
                echo "Connected successfully";
            }

            $res = mysqli_query($this->con, "SELECT * FROM `crawled_urls`");
            echo $num = mysqli_num_rows($res);
        }
    }

    
?>