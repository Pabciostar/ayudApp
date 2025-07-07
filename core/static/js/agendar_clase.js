document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('disponibilidad');
    const inputFecha = document.getElementById('fecha');
    const inputHora = document.getElementById('hora_inicio');
    const inputDuracion = document.getElementById('duracion_min');
    const form = document.querySelector('form');

    if (select) {
        select.addEventListener('change', function () {

            console.log("Valor seleccionado:", this.value)

            if (this.value) {
                const [fecha, hora_inicio, duracion_min] = this.value.split('|');

                console.log("Fecha:", fecha);
                console.log("Hora:", hora_inicio);
                console.log("Duración:", duracion_min);

                inputFecha.value = fecha;
                inputHora.value = hora_inicio;
                inputDuracion.value = duracion_min;
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();  // Evita el envío inmediato

            if (!select.value) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Seleccione un horario',
                    text: 'Debes elegir un horario disponible antes de agendar la clase.',
                    confirmButtonText: 'OK'
                });
                return;
            }

            console.log("Valor del select en el submit:", select.value);

            const [fecha, hora_inicio, duracion_min] = select.value.split('|');
            console.log("Valores divididos:", { fecha, hora_inicio, duracion_min});

            if (!fecha || !hora_inicio || !duracion_min) {
                console.error("Faltan datos en el horario. Valor original:", select.value);
                Swal.fire({
                    icon: 'error',
                    title: 'Error interno',
                    text: 'No se pudieron cargar los datos del horario. Intenta de nuevo.',
                });
                return;
            }

            Swal.fire({
                icon: 'question',
                title: '¿Confirmar agendamiento?',
                html: `
                    <p><strong>Fecha:</strong> ${fecha}</p>
                    <p><strong>Hora:</strong> ${hora_inicio}</p>
                    <p><strong>Duración:</strong> ${duracion_min} minutos</p>
                `,
                showCancelButton: true,
                confirmButtonText: 'Sí, agendar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    }
});