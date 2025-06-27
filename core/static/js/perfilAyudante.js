document.addEventListener("DOMContentLoaded", function () {
  const rol = document.getElementById("user-rol")?.value || null;
  const ayudanteIdInput = document.getElementById("ayudante-id");
  let ayudanteId = ayudanteIdInput?.value || null;

  const agendarBtn = document.getElementById("agendar-btn");
  const disponibilidadBtn = document.getElementById("disponibilidad-btn");
  const editarBtn = document.getElementById("editar-btn");
  const bancariosBtn = document.getElementById("bancarios-btn");

  // Ocultar todos los botones por defecto
  if (agendarBtn) agendarBtn.style.display = "none";
  if (disponibilidadBtn) disponibilidadBtn.style.display = "none";
  if (editarBtn) editarBtn.style.display = "none";
  if (bancariosBtn) bancariosBtn.style.display = "none";

  function fetchPerfilAyudante(idAyudante) {
    fetch(`/api/ayudantes/${idAyudante}/`)
      .then(response => {
        if (!response.ok) throw new Error("No se pudo obtener el ayudante visitado");
        return response.json();
      })
      .then(data => {
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
        console.error("Error al obtener perfil del ayudante:", error);
      });
  }

  if (rol === "estudiante") {
    if (agendarBtn) {
      agendarBtn.style.display = "inline-block";
      agendarBtn.href = `/agendarClase/${ayudanteId}`;
    }
    fetchPerfilAyudante(ayudanteId);

  } else if (rol === "ayudante") {
    fetch("/api/ayudante/autenticado/")
      .then(response => {
        if (!response.ok) throw new Error("No se pudo obtener el ayudante autenticado");
        return response.json();
      })
      .then(authData => {
        const authUserIdStr = authData.usuario.id_usuario.toString();
        const ayudanteIdStr = ayudanteId?.toString() || authUserIdStr;
        const esMismoAyudante = authUserIdStr === ayudanteIdStr;

        if (agendarBtn) agendarBtn.href = `/agendarClase/${ayudanteIdStr}`;

        if (esMismoAyudante) {
          if (disponibilidadBtn) disponibilidadBtn.style.display = "inline-block";
          if (editarBtn) editarBtn.style.display = "inline-block";
          if (bancariosBtn) bancariosBtn.style.display = "inline-block";

          if (agendarBtn) {
            agendarBtn.addEventListener("click", function (e) {
              e.preventDefault();
              Swal.fire({
                icon: "warning",
                title: "Acción no permitida",
                text: "No puedes agendar una clase contigo mismo.",
                confirmButtonColor: "#3085d6"
              });
            });
          }
        } else {
          if (agendarBtn) agendarBtn.style.display = "inline-block";
        }

        fetchPerfilAyudante(ayudanteIdStr);
      })
      .catch(error => {
        console.error("Error al obtener ayudante autenticado:", error);
      });

  } else {
    console.warn("Rol desconocido o no autenticado:", rol);
    if (ayudanteId) fetchPerfilAyudante(ayudanteId);
  }
});
