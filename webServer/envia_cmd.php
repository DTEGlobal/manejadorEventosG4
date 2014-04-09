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
  
  
  $resultDisp = mysql_query("update dispositivo set comandoConsola ='".$_POST['cmd']."' where dirDispositivo = '01'");
  
  echo "<h1 align='center'>Consola</h1>";
  echo "<br>"; 
  echo "<h2 align='center'><p><b> Comando: 01".$_POST['cmd']."</p></b></h2>";
	sleep(2);
	$result_cmd = mysql_query("SELECT respuestaConsola FROM dispositivo");	
	$row = mysql_fetch_row($result_cmd);
		 
	if($row[0] == "" ){
		echo "No Tenemos Respuesta press F5";
	// no hacermos nada por que no hay respuesta
	}
	else{
		echo "<h2 align='center'><p><b> Respuesta: $row[0]</p></b>";
		mysql_query("update dispositivo set respuestaConsola ='' where dirDispositivo = '01'");
	}
  echo "<a href='consola.html' align='center'> <input type='button' name='boton' value='Comando Nuevo' /> </a>"; 
?>
</body>
</html>