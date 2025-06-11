document.addEventListener("DOMContentLoaded", function () {
  const rol = document.getElementById("user-rol")?.value || null;

  // Declarar de nuevo ayudanteId antes de usarlo
  const ayudanteId = document.getElementById("ayudante-id")?.value || null;

  const agendarBtn        = document.getElementById("agendar-btn");
  const disponibilidadBtn = document.getElementById("disponibilidad-btn");
  const editarBtn         = document.getElementById("editar-btn");

  // Mostrar/Ocultar botones según el rol
  if (rol === "estudiante") {
    agendarBtn.style.display        = "inline-block";
    disponibilidadBtn.style.display = "none";
    editarBtn.style.display         = "none";
  } else if (rol === "ayudante") {
    agendarBtn.style.display        = "none";
    disponibilidadBtn.style.display = "inline-block";
    editarBtn.style.display         = "inline-block";
  }

  // Ahora sí podemos usar ayudanteId para armar la URL
  let url = "/api/ayudante/autenticado/";
  if (ayudanteId) {
    url = `/api/ayudantes/${ayudanteId}/`;
    agendarBtn.href = `/agendarClase/${ayudanteId}/`;
  }

  fetch(url)
    .then(response => {
      if (!response.ok) throw new Error("No se pudo obtener el ayudante");
      return response.json();
    })
    .then(data => {
      // Rellenar el DOM con la info del ayudante
      document.getElementById('contenedorNombreAyudante').innerHTML =
        `<p>${data.usuario.nombres} ${data.usuario.apellidos}</p>`;

      document.getElementById('contenedorInformacionAyudante').innerHTML = `
        <h4>Nombre:</h4>
        <p>${data.usuario.nombres} ${data.usuario.apellidos}</p>
        <h4 class="fw-bold">Grado académico:</h4>
        <p>${data.carrera}</p>
        <h4 class="fw-bold">Descripción:</h4>
        <p>${data.cuentanos}</p>
        <h4 class="fw-bold">Valor por hora:</h4>
        <p>$${data.valor} CLP</p>
        <h4 class="fw-bold">Disponibilidad tentativa:</h4>
        <p>${data.disponibilidad}</p>
      `;

      if (data.foto_base64) {
        const img = document.getElementById("fotoPerfil");
        img.src = data.foto_base64.startsWith("data:image")
          ? data.foto_base64
          : `data:image/jpeg;base64,${data.foto_base64}`;
      }
    })
    .catch(error => {
      console.error("Error:", error);
    });
});
