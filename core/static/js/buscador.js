let timeout = null;
let controller = null;

const input = document.getElementById("buscadorAyudantes");
const contenedorSug = document.getElementById("sugerencias");

input.addEventListener("input", () => {
  const query = input.value.trim();

  clearTimeout(timeout);
  timeout = setTimeout(() => {
    if (query.length < 2) {
      contenedorSug.innerHTML = "";
      return;
    }

    if (controller) controller.abort();
    controller = new AbortController();

    fetch(`/api/ayudantes?q=${encodeURIComponent(query)}`, { signal: controller.signal })
      .then(response => {
        if (!response.ok) throw new Error("Respuesta no válida");
        return response.json();
      })
      .then(lista => {
        contenedorSug.innerHTML = "";
        if (!lista.length) {
          contenedorSug.innerHTML =
            "<div class='list-group-item'>No se encontraron resultados</div>";
          return;
        }

        lista.forEach(ayudante => {
          const item = document.createElement("a");
          item.className = "list-group-item list-group-item-action";
          item.href = `/perfilAyudante/${ayudante.id}/`;
          item.textContent = `${ayudante.usuario.nombres} ${ayudante.usuario.apellidos} - ${ayudante.carrera}`;
          contenedorSug.appendChild(item);
        });
      })
      .catch(error => {
        console.error("Error en la búsqueda:", error);
      });
  }, 300);
});


document.addEventListener('DOMContentLoaded', function () {
    const usuario_id = document.getElementById("id_usuario")?.value || null;
    const contenedor = document.getElementById('contenedorClasesAgendadas');

    fetch(`/api/clases-agendadas/${usuario_id}/`)
        .then(response => response.json())
        .then(data => {
            const lista = document.createElement('ul');
            lista.className = 'list-group';

            if (data.length === 0) {
                lista.innerHTML = '<li class="list-group-item">No hay clases agendadas.</li>';
            } else {
                data.forEach(clase => {
                    const fecha = new Date(clase.fecha + 'T' + clase.hora);
                    const opcionesFecha = { weekday: 'long', hour: '2-digit', minute: '2-digit' };
                    const fechaFormateada = fecha.toLocaleDateString('es-CL', opcionesFecha);

                    const item = document.createElement('li');
                    item.className = 'list-group-item';
                    item.innerHTML = `
                        ${clase.nombre_ayudante} - ${fechaFormateada}
                        <a href="/detalleClase/${clase.id_clase}/" class="btn btn-primary">Ver más</a>
                    `;
                    lista.appendChild(item);
                });
            }

            contenedor.innerHTML = ''; // Limpia el contenido anterior
            contenedor.appendChild(document.createElement('h5')).textContent = 'Clases Agendadas';
            contenedor.appendChild(lista);
        })
        .catch(error => {
            console.error('Error al cargar clases agendadas:', error);
        });
});


