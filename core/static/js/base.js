document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/mi-rol/')
        .then(response => {
            if (!response.ok) throw new Error("No autenticado o error al obtener rol.");
            return response.json();
        })
        .then(data => {
            if (data.rol !== 'admin') {
                const panelAdmin = document.querySelector("a[href='{% url 'panelAdministrador' %}']");
                if (panelAdmin) {
                    panelAdmin.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.log('Error al obtener el rol:', error);
            const panelAdmin = document.querySelector("a[href='{% url 'panelAdministrador' %}']");
            if (panelAdmin) {
                panelAdmin.style.display = 'none';
            }
        });
});