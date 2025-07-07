document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formularioReporte");
    const descripcionContainer = document.getElementById("contenedorDescripcion");
    const descripcionInput = document.getElementById("descripcion");
    // Mostrar campo de descripción solo si seleccionan "otro"
    document.getElementById("motivo").addEventListener("change", function () {
        if (this.value === "otro") {
            descripcionContainer.classList.remove("d-none");
            descripcionInput.required = true;
        } else {
            descripcionContainer.classList.add("d-none");
            descripcionInput.required = false;
        }
    });

    // Envío del formulario
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        e.stopImmediatePropagation();

        const motivo = document.getElementById("motivo").value;
        const descripcion = descripcionInput.value.trim();

        const razon = {
            "el_ayudante_no_se_presento": "El ayudante no se presentó",
            "no_dominio_materia": "El ayudante no mostró dominio de la materia",
            "lenguaje_inapropiado": "El ayudante usó lenguaje inapropiado",
            "clase_no_finalizada": "El ayudante no terminó la clase",
            "otro": descripcion || "Otra razón"
        };

        const cuerpo = `Se reporta un problema sobre la clase:\nMotivo: ${razon[motivo]}`;
        
        try {
            const csrftoken = "{% csrf_token %}";
            const response = await fetch(`/api/reportar-problema/${claseId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ motivo, descripcion })
            });

            const result = await response.json();

            if (response.ok) {
                document.getElementById("formularioReporte").style.display = "none";
                document.getElementById("mensajeExito").classList.remove("d-none");
            } else {
                alert("Hubo un error al enviar el reporte.");
            }
        } catch (error) {
            alert("No se pudo enviar el reporte. Inténtalo más tarde.");
        }
    });
    return false;
});