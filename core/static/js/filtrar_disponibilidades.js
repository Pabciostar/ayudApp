document.addEventListener("DOMContentLoaded", function () {
    const selectMateria = document.getElementById("materia");
    const selectDisponibilidad = document.getElementById("disponibilidad");

    if (!selectMateria || !selectDisponibilidad) return;

    selectMateria.addEventListener("change", function () {
        const materiaSeleccionada = this.value;

        Array.from(selectDisponibilidad.options).forEach(option => {
            if (!option.value) return;  // Saltar el option de placeholder
            const materiaId = option.getAttribute("data-materia-id");
            option.style.display = (materiaId === materiaSeleccionada) ? "block" : "none";
        });

        // Reiniciar selección
        selectDisponibilidad.value = "";
    });
});