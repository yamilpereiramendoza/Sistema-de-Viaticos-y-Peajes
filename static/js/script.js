$(document).on("ready",inicio);

function inicio(){
	$("span.help-block").hide();
	$("#Registrar").click(function(){
		if(validar()==false)
			alert("los campos no estan validados");
		else{
			alert("los campos estan validados");
		}
	});
	$("#texto").keyup(validar);
}

function validar(){
	var valor = document.getElementById("texto").value;
	if( valor == null || valor.length == 0 || /^\s+$/.test(valor) ) {
		$("#texto").parent().parent().attr("class","form-group has-error has-feedback");
		$("#texto").parent().children("span").text("Debe ingresar algun caracter").show();
		$("#texto").parent().append("<span id='iconotexto' class='glyphicon glyphicon-remove form-control-feedback'></span>");
	  	return false;
	}
	else if( isNaN(valor) ) {
		$("#texto").parent().parent().attr("class","form-group has-error has-feedback");
		$("#texto").parent().children("span").text("Debe ingresar caracteres numericos").show();
		$("#texto").parent().append("<span id='iconotexto' class='glyphicon glyphicon-remove form-control-feedback'></span>");
		return false;
	}
	else{
		$("#texto").parent().parent().attr("class","form-group has-success has-feedback");
		$("#texto").parent().children("span").text("").hide();
		$("#texto").parent().append("<span id='iconotexto' class='glyphicon glyphicon-ok form-control-feedback'></span>");
		return true;
	}
}