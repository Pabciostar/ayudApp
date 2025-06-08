document.addEventListener("DOMContentLoaded", function () {
fetch("/api/ayudante/autenticado/")
    .then(response => {
      if (!response.ok) {
        throw new Error("No se pudo obtener el ayudante");
      }
      return response.json();
    })
    .then(data => {
      const contenedorNombre = document.getElementById('contenedorNombreAyudante');
      contenedorNombre.innerHTML = `<p>${data.usuario.nombres} ${data.usuario.apellidos}</p>`;

      const contenedor = document.getElementById('contenedorInformacionAyudante');
      contenedor.innerHTML = `
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
      console.error('Error:', error);
    });
    
});