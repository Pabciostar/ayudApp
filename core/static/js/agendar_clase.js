document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('disponibilidad');
    const inputFecha = document.getElementById('fecha');
    const inputHora = document.getElementById('hora');
    const inputDuracion = document.getElementById('duracion_min');
    const form = document.querySelector('form');

    if (select) {
        select.addEventListener('change', function () {

            console.log("Valor seleccionado:", this.value)

            if (this.value) {
                const [fecha, hora, duracion] = this.value.split('|');

                console.log("Fecha:", fecha);
                console.log("Hora:", hora);
                console.log("Duración:", duracion);

                inputFecha.value = fecha;
                inputHora.value = hora;
                inputDuracion.value = duracion;
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

            const [fecha, hora, duracion] = select.value.split('|');
            console.log("Valores divididos:", { fecha, hora, duracion});

            if (!fecha || !hora || !duracion) {
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
                    <p><strong>Hora:</strong> ${hora}</p>
                    <p><strong>Duración:</strong> ${duracion} minutos</p>
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