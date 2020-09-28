<?php
    require 'includes/db_connection.inc.php';
    require 'includes/db_getData.inc.php';
    require 'includes/db_viewResults.inc.php';
?>

<?php

    
    $search = new ViewResults();
    echo $search->data;
?>