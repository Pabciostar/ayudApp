function gestionarPostulacion(accion) {
    const datos = document.getElementById('datosPostulacion');

    const idPostulacion = datos.dataset.id;
    const csrfToken = datos.dataset.csrf;
    const redirectUrl = datos.dataset.redirect;

    const url = accion === 'aceptar' ? '/aceptarPostulacion/' : '/rechazarPostulacion/';

    // Desactivar botones mientras se procesa
    const botones = document.querySelectorAll('button');
    botones.forEach(boton => boton.disabled = true);

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ id_postulacion: idPostulacion })
    })
    .then(response => response.json())
    .then(data => {
        if (data.mensaje) {
            alert(data.mensaje);
            window.location.href = redirectUrl;
        } else {
            alert("Error: " + data.error);
            botones.forEach(boton => boton.disabled = false);  // Rehabilitar si hay error
        }
    })
    .catch(error => {
        alert("Ocurrió un error al procesar la solicitud.");
        console.error(error);
        botones.forEach(boton => boton.disabled = false);
    });
}
