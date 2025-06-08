document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/ayudante/autenticado/")
        .then(response => {
            if (!response.ok) {
                throw new Error("No se pudo obtener el ayudante");
            }
            return response.json();
        })
        .then(data => {
            console.log("Datos del ayudante:", data);
            const nombreCompleto = data.usuario.nombres + ' ' + data.usuario.apellidos;
            const divNombreAyudante = document.getElementById('nombreAyudante');

            divNombreAyudante.textContent = nombreCompleto;
            document.querySelector('input[name="nombre"]').value = nombreCompleto;
            document.querySelector('input[name="grado"]').value = data.carrera;
            document.querySelector('input[name="valor"]').value = data.valor;
            document.querySelector('input[name="disponibilidad"]').value = data.disponibilidad;
            document.querySelector('textarea[name="descripcion"]').value = data.cuentanos;
        })
        .catch(error => {
            console.error('Error:', error);
        });

});


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


document.querySelector("form").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append("cuentanos", document.querySelector('textarea[name="descripcion"]').value);
    formData.append("valor", document.querySelector('input[name="valor"]').value);
    formData.append("disponibilidad", document.querySelector('input[name="disponibilidad"]').value);

    const foto = document.getElementById("foto_perfil").files[0];
    if (foto) {
        formData.append("foto_perfil", foto);
    }

    fetch("/api/ayudante/autenticado/", {
        method: "PATCH",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: formData
    })
        .then(response => {
            if (!response.ok) throw new Error("No se pudo actualizar");
            return response.json();
        })
        .then(data => {
            alert("¡Perfil actualizado!");

            if (foto) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const imgPerfil = document.getElementById("fotoPerfil");
                    if (imgPerfil) {
                        imgPerfil.src = e.target.result;
                    }
                };
                reader.readAsDataURL(foto);
            }
        })
        .catch(error => console.error(error));
});