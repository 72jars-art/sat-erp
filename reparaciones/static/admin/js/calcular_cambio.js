document.addEventListener("DOMContentLoaded", function() {
    
    // Función auxiliar para obtener valor de un campo, sea input o div
    function obtenerValor(id) {
        const el = document.getElementById(id);
        if (!el) return 0;
        // Si tiene .value (es un input), lo usamos. Si no, usamos .innerText (es un div/span)
        const valorRaw = (el.tagName === 'INPUT') ? el.value : el.innerText;
        return parseFloat(valorRaw.replace(',', '.')) || 0;
    }

    // Delegamos el evento al body para que siempre detecte el cambio
    document.body.addEventListener('input', function(event) {
        if (event.target && event.target.id === 'id_importe_entregado') {
            
            const total = obtenerValor('id_total');
            const entregado = parseFloat(event.target.value.replace(',', '.')) || 0;
            const cambio = entregado - total;
            
            const campoCambio = document.getElementById('id_cambio_a_devolver');
            if (campoCambio) {
                const resultado = cambio.toFixed(2).replace('.', ',');
                // Actualizamos según el tipo de elemento
                if (campoCambio.tagName === 'INPUT') {
                    campoCambio.value = resultado;
                } else {
                    campoCambio.innerText = resultado;
                }
            }
        }
    });
});