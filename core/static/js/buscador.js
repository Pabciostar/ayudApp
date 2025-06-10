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


