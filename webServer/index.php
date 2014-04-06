<html>
<head>
	<style>
		body
		{ 
		background: #1975FF ; 
		}
	</style>
</head>
<body>
<?php
  $con=mysql_connect("localhost","admin","petrolog");
  $db =Mysql_select_db("eventosg4",$con);
  
  //Actualiza hora 
  mysql_query("update dispositivo set comandoConsola ='H' where dirDispositivo = '01'");   
  while(true){
		$hora_Actual = mysql_query("SELECT respuestaConsola FROM dispositivo");
		$row = mysql_fetch_row($hora_Actual);
		if($row[0] == "" ){
		// no hacermos nada por que no hay respuesta
		}else{
		$hora = substr($row[0],3);
			echo "<h2 align='center'><p><b> Hora: $hora</p></b>";
			mysql_query("update dispositivo set respuestaConsola ='' where dirDispositivo = '01'");
			break;
		}
	}

	
  //Resultado del estado del motor.
  mysql_query("update dispositivo set comandoConsola ='E' where dirDispositivo = '01'");
  
  while(true){
	$resultEdo  = mysql_query("SELECT estado FROM dispositivo");
	$resConsola = mysql_query("SELECT respuestaConsola FROM dispositivo");
	$row = mysql_fetch_row($resultEdo);
	$rowConsola = mysql_fetch_row($resConsola);
	if($rowConsola[0] == ""){
	// no hacermos nada por que no hay respuesta
	}else{
		if($row[0]=="0"){
			echo "<h2 align='center'>Estado: Apagado<h1>";
			echo "<br>";
			
		}
		else{
			echo "<h2 align='center'>Estado: Prendido<h1>";
			
			echo "<br>";
			
		}
		mysql_query("update dispositivo set respuestaConsola ='' where dirDispositivo = '01'");
		mysql_query("update dispositivo set estado ='' where dirDispositivo = '01'");
		break;
    }
  }
  
 
 
 //Resultado de la configuracion Actual
 $resultConf = mysql_query("SELECT * FROM eventos");
  echo "<h3>";
  echo "<table border='1' align='center'>
  <tr>
  <th>Fecha de Inicio</th>
  <th>Fecha de Fin</th>
  <th>Acci&oacute;n</th>
  <th>Estado</th>
  <th>Fecha de Adquisici&oacute;n</th>
  </tr>";
  while($row = mysql_fetch_array($resultConf)){
	echo "<tr>";
	$fecha_Inicio	    = $row['fecha_inicio'];
	$fecha_Fin 			= $row['fecha_fin'];	
	$accion 	= $row['accion'];
	$estado 	= $row['estado'];
	$fecha_Adquisicion 	= $row['fecha_adquisicion'];
	
	
	echo "<td> $fecha_Inicio </td>";
	echo "<td> $fecha_Fin </td>";
	echo "<td> $accion </td>";
	echo "<td> $estado  </td>";
	echo "<td> $fecha_Adquisicion </td>";
	echo "</tr>";
 }
  echo "</table>";
  echo "</h3>";
  
 
  mysql_close($con);
?>
</body>
</html>