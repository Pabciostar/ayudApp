document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('disponibilidad');
    const inputFecha = document.getElementById('fecha');
    const inputHora = document.getElementById('hora_inicio');
    const inputDuracion = document.getElementById('duracion_min');
    const form = document.querySelector('form');
    const btnTest = document.getElementById('btn-test-agendar');

    let botonPresionado = null;

    if (btnTest) {
        btnTest.addEventListener('click', function () {
            botonPresionado = 'test';
        });
    }

    if (form) {
        form.addEventListener('submit', function (e) {
            if (botonPresionado !== 'test') {
                // Permite que el botón PayPal siga funcionando como está
                return;
            }

            // Para el botón TEST, detenemos el envío automático
            e.preventDefault();

            if (!select.value) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Seleccione un horario',
                    text: 'Debes elegir un horario disponible antes de agendar la clase.',
                    confirmButtonText: 'OK'
                });
                return;
            }

            const [fecha, hora_inicio, duracion_min] = select.value.split('|');

            if (!fecha || !hora_inicio || !duracion_min) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error interno',
                    text: 'No se pudieron cargar los datos del horario. Intenta de nuevo.',
                });
                return;
            }

            Swal.fire({
                icon: 'question',
                title: '¿Confirmar agendamiento de prueba?',
                html: `
                    <p><strong>Fecha:</strong> ${fecha}</p>
                    <p><strong>Hora:</strong> ${hora_inicio}</p>
                    <p><strong>Duración:</strong> ${duracion_min} minutos</p>
                `,
                showCancelButton: true,
                confirmButtonText: 'Sí, agendar (Test)',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // ⚠️ Aquí asignamos los valores a los inputs ocultos
                    inputFecha.value = fecha;
                    inputHora.value = hora_inicio;
                    inputDuracion.value = duracion_min;

                    // ⚡ Establecemos el action y enviamos el formulario
                    form.setAttribute('action', btnTest.getAttribute('formaction'));
                    form.submit();
                }
            });
        });
    }
});