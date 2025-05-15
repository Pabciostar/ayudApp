const ayudantesFake = [
    { nombre: "Juan Pérez", area: "Matemáticas" },
    { nombre: "María González", area: "Física" },
    { nombre: "Carlos Soto", area: "Programación" },
    { nombre: "Valentina Rojas", area: "Estadística" },
    { nombre: "Andrés Ramírez", area: "Química" }
  ];

  const input = document.getElementById("buscadorAyudantes");
  const sugerencias = document.getElementById("sugerencias");

  input.addEventListener("input", function () {
    const valor = this.value.toLowerCase();
    sugerencias.innerHTML = "";

    if (valor.length === 0) return;

    const filtrados = ayudantesFake.filter(a =>
      a.nombre.toLowerCase().includes(valor) || a.area.toLowerCase().includes(valor)
    );

    if (filtrados.length === 0) {
      sugerencias.innerHTML = '<div class="list-group-item">No se encontraron ayudantes</div>';
    } else {
      filtrados.forEach(a => {
        sugerencias.innerHTML += `
          <a href="/perfilAyudante" class="list-group-item list-group-item-action">
            <strong>${a.nombre}</strong> – ${a.area}
          </a>
        `;
      });
    }
  });