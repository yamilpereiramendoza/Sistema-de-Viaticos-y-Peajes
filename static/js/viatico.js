$(document).ready(function () {
    id_horaSalida = document.getElementById("id_horaSalida");
    id_horaSalida.type = "time";
    id_horallegada = document.getElementById("id_horallegada");
    id_horallegada.type = "time";
    id_fecha_legada = document.getElementById("id_fecha_legada");
    id_fecha_legada.type = "date";
    id_fecha_salida = document.getElementById("id_fecha_salida");
    id_fecha_salida.type = "date";
    if( !$('#id_tipo_viatico').val()) {
        var theSelect = document.getElementById('id_monto');
        var options = theSelect.getElementsByTagName('OPTION');
        for(var i=0; i<options.length; i++) {
            theSelect.removeChild(options[i]);
            i--; 
        }
    }
    
});
$('select#id_tipo_viatico').change(function () {
    var optionSelected = $(this).find("option:selected");
    var id  = optionSelected.val();
    //var monto_id   = optionSelected.text();
    $.ajax({
        data:{'id':id},
        url:'/viaticos/buscar_montos/',
        type:'get',
        success : function(data) {
            var html=""
            //console.log(data)
            for (var i =0;i < data.length ; i++) {
                    html +='<option value='+data[i].pk+'>'+data[i].fields.Nombre+' '+data[i].fields.Cantidad+'</option>'
            }
            $('#id_monto').html(html);
        },
        error : function(message) {
            console.log(message);
        }
    })
});