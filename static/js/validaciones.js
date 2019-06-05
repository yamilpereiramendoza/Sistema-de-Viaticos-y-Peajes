/// validaciones de BUSCAR EMPLEADOS
if($('#mostrarerrordjango').css('display') == 'block'){
    var error=document.getElementById("mostrarerrordjango");
    setTimeout(function() {
        $("#error").fadeOut(1000);
        error.style.display = "none";
    },3000);
}


/// FIN DE BUSCAR EMPLEADOS