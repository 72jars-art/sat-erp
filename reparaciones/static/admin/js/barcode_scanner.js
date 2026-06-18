document.addEventListener('DOMContentLoaded', function() {
    // Detectar cuando el select2 (autocompletado) cambia
    document.addEventListener('select2:select', function (e) {
        // Al seleccionar, pasar foco al siguiente input de cantidad o nueva fila
        setTimeout(function() {
            let nextInput = document.querySelector('.add-row a'); 
            // Esto es una simplificación; podrías enfocar el input de cantidad
        }, 100);
    });
});