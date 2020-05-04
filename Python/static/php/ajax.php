<?php
    echo '<div> Dpc pis nieco!!! </div>';
    $servername = "localhost";
    $dbname = "MPC_optimization";

    $reference = $_GET['action'];
    $c_id = $_GET['c_id'];
    $sql = "UPDATE MPC_optimization SET x_referenc=$reference WHERE id=$c_id";
?>