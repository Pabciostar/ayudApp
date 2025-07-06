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

            const ahora = new Date();

            // Filtra clases confirmadas y que aún no han terminado
            const clasesPendientes = data.filter(clase => {
                if (clase.estado !== "confirmada") return false;

                // Construir fecha de inicio de clase
                const fechaInicio = new Date(clase.fecha + 'T' + clase.hora);

                // Calcular fecha de término sumando duracion_min en milisegundos
                const fechaTermino = new Date(fechaInicio.getTime() + clase.duracion_min * 60000);

                // Mantener si la clase no ha terminado
                return fechaTermino >= ahora;
            });

            if (clasesPendientes.length === 0) {
                lista.innerHTML = '<li class="list-group-item">No hay clases agendadas.</li>';
            } else {
                clasesPendientes.forEach(clase => {
                    const fechaInicio = new Date(clase.fecha + 'T' + clase.hora);
                    const opcionesFecha = { 
                        year: '2-digit', 
                        month: '2-digit', 
                        day: '2-digit',
                        hour: '2-digit', 
                        minute: '2-digit',
                        hour12: true
                    };
                    const fechaFormateada = fechaInicio.toLocaleDateString('es-CL', opcionesFecha);

                    const item = document.createElement('li');
                    item.className = 'list-group-item';
                    item.innerHTML = `
                        ${clase.nombre_materia} - ${fechaFormateada}
                        <a href="/detalleClase/${clase.id_clase}/" class="btn btn-primary">Ver más</a>
                    `;
                    lista.appendChild(item);
                });
            }

            contenedor.innerHTML = ''; // Limpia el contenido anterior
            const titulo = document.createElement('h5');
            titulo.textContent = 'Clases Agendadas';
            contenedor.appendChild(titulo);
            contenedor.appendChild(lista);
        })
        .catch(error => {
            console.error('Error al cargar clases agendadas:', error);
        });
});


document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/mejores-ayudantes/")
    .then(response => response.json())
    .then(data => crearCarruselAyudantes(data))
    .catch(error => console.error("Error al cargar ayudantes:", error));
});

function crearCarruselAyudantes(ayudantes) {
  const carrusel = document.getElementById("carrusel-ayudantes");
  const indicadores = document.getElementById("indicadores-ayudantes");

  carrusel.innerHTML = "";
  indicadores.innerHTML = "";

  const grupos = agruparPorTres(ayudantes);

  grupos.forEach((grupo, index) => {
    // Crear el item del carrusel
    const item = document.createElement("div");
    item.classList.add("carousel-item");
    if (index === 0) item.classList.add("active");

    const fila = document.createElement("div");
    fila.classList.add("row", "justify-content-center");

    grupo.forEach(ayudante => {
      const tarjeta = document.createElement("div");
      tarjeta.classList.add("col-md-4", "mb-3");

      tarjeta.innerHTML = `
        <div class="card">
          <div class="square-image-container">
            <img src="${ayudante.imagen_url || 'core/static/images/placeHolderPerfilAyudante.png'}" class="img-fluid rounded" alt="Ayudante" style="width: 250px; height: 250px; object-fit: cover;">
          </div>
          <div class="card-body">
            <h5 class="card-title">${ayudante.nombre}</h5>
            <p class="card-text">${ayudante.ramos}</p>
            <p class="card-text">descripción: ${ayudante.descripcion}</p>
            <button type="button" class="btn btn-primary">
              <a href="/perfilAyudante/${ayudante.id}" class="link-light">Ver más</a>
            </button>
          </div>
        </div>
      `;

      fila.appendChild(tarjeta);
    });

    item.appendChild(fila);
    carrusel.appendChild(item);

    // Crear indicador
    const indicador = document.createElement("button");
    indicador.type = "button";
    indicador.setAttribute("data-bs-target", "#ayudantesCarousel");
    indicador.setAttribute("data-bs-slide-to", index);
    if (index === 0) {
      indicador.classList.add("active");
      indicador.setAttribute("aria-current", "true");
    }
    indicadores.appendChild(indicador);
  });
}

// Agrupa de 3 en 3
function agruparPorTres(lista) {
  const grupos = [];
  for (let i = 0; i < lista.length; i += 3) {
    grupos.push(lista.slice(i, i + 3));
  }
  return grupos;
}
