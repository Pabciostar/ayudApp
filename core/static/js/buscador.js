
let timeout = null;

document.getElementById("buscadorAyudantes").addEventListener("input", function () {
  const query = this.value;

  clearTimeout(timeout);
  timeout = setTimeout(() => {
    if (query.length < 2) {
      document.getElementById("sugerencias").innerHTML = "";
      return;
    }

    fetch(`/api/ayudantes?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => {
        const sugerencias = document.getElementById("sugerencias");
        sugerencias.innerHTML = "";
        console.log(data);
        if (data.length === 0) {
          sugerencias.innerHTML = "<div class='list-group-item'>No se encontraron resultados</div>";
          return;
        }

        data.forEach(ayudante => {
          const item = document.createElement("a");
          item.className = "list-group-item list-group-item-action";
          item.href = `/perfil/${ayudante.id}/`;
          item.textContent = `${ayudante.usuario.nombres} ${ayudante.usuario.apellidos} - ${ayudante.carrera}`;
          sugerencias.appendChild(item);
        });
      })
      .catch(error => {
        console.error("Error en la búsqueda:", error);
      });
  }, 200); 
});
