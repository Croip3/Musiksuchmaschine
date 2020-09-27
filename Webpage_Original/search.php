<?php
    require 'includes/db_connection.inc.php';
    require 'includes/db_getData.inc.php';
    require 'includes/db_viewResults.inc.php';
?>

<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="main.css">
        <title>Musiksuchmaschine</title>
    </head>
    <body>
        <header>
            <a href="index.html">SUCHE</a>
        </header>
    </body>
</html>

<?php    
    $search = new ViewResults();
?>