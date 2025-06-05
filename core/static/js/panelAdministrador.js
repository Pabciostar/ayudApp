function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function limpiarPanel() {
  const panel = document.getElementById('panelInformacion');
  panel.innerHTML = '';
}

function mostrarUsuarios() {
  limpiarPanel();
  const panel = document.getElementById('panelInformacion');

  panel.innerHTML = `
        <h3>Usuarios Registrados</h3>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Nombre</th>
                    <th>RUT</th>
                    <th>Correo</th>
                    <th>Rol</th>
                </tr>
            </thead>
            <tbody id="tabla-usuarios"></tbody>
        </table>
        <button id="guardar-cambios" class="btn btn-primary mt-3">Guardar cambios</button>
    `;

  // Cargar usuarios inmediatamente (ya no se necesita DOMContentLoaded aquí)
  fetch('/api/usuarios/')
    .then(response => response.json())
    .then(data => {
      const tbody = document.getElementById('tabla-usuarios');
      tbody.innerHTML = ''; // Limpia antes de llenar

      data.forEach(usuario => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
                    <td>${usuario.nombres} ${usuario.apellidos}</td>
                    <td>${usuario.rut_usuario}</td>
                    <td>${usuario.correo}</td>
                    <td>
                        <select data-id="${usuario.id_usuario}" class="form-select rol-select">
                            <option value="estudiante" ${usuario.rol === 'estudiante' ? 'selected' : ''}>Estudiante</option>
                            <option value="ayudante" ${usuario.rol === 'ayudante' ? 'selected' : ''}>Ayudante</option>
                            <option value="administrador" ${usuario.rol === 'administrador' ? 'selected' : ''}>Administrador</option>
                        </select>
                    </td>
                `;
        tbody.appendChild(fila);
      });
    });

  // Evitar múltiples listeners duplicados al botón
  setTimeout(() => {
    const botonGuardar = document.getElementById('guardar-cambios');
    if (botonGuardar) {
      botonGuardar.onclick = () => {
        const cambios = [];

        document.querySelectorAll('.rol-select').forEach(select => {
          const id = select.dataset.id;
          const nuevoRol = select.value;
          cambios.push({ id_usuario: id, rol: nuevoRol });
        });

        Promise.all(cambios.map(cambio =>
          fetch(`/api/usuarios/${cambio.id_usuario}/`, {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ rol: cambio.rol })
          }).then(response => {
            if (!response.ok) {
              throw new Error(`Error al guardar usuario ${cambio.id_usuario}`);
            }
          })
        )).then(() => {
          alert('Cambios guardados exitosamente');
          mostrarUsuarios(); // Recarga la tabla con los datos actualizados
        }).catch(error => {
          console.error(error);
          alert('Hubo un error al guardar uno o más cambios');
        });
        alert('Cambios guardados exitosamente');
      };
    }
  }, 100); // Espera breve para asegurar que el botón existe
}



function mostrarClasesAgendadas() {
  const panel = document.getElementById('panelInformacion');
  limpiarPanel();

  const clases = [
    {
      ayudante: 'Ana Martínez',
      estudiante: 'Pedro Torres',
      fechaAgendamiento: '2025-05-01',
      fechaClase: '2025-05-03',
      estado: 'Realizada',
      calificacion: '4.0',
      valor: 20000
    },
    {
      ayudante: 'Luis González',
      estudiante: 'Sofía Rojas',
      fechaAgendamiento: '2025-04-28',
      fechaClase: '2025-05-02',
      estado: 'Pagada',
      calificacion: 'No aplica',
      valor: 15000
    },
    {
      ayudante: 'María López',
      estudiante: 'Carlos Pérez',
      fechaAgendamiento: '2025-05-04',
      fechaClase: '2025-05-06',
      estado: 'Realizada',
      calificacion: '5.0',
      valor: 18000
    },
    {
      ayudante: 'Daniela Reyes',
      estudiante: 'Fernanda Díaz',
      fechaAgendamiento: '2025-05-02',
      fechaClase: '2025-05-05',
      estado: 'Confirmada',
      calificacion: 'No aplica',
      valor: 22000
    }
  ];

  let tablaHTML = `
      <h4>Clases Agendadas</h4>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Ayudante</th>
            <th>Estudiante</th>
            <th>Fecha Agendamiento</th>
            <th>Fecha Clase</th>
            <th>Estado</th>
            <th>Calificacion</th>
            <th>Valor</th>
            <th>Comisión (15%)</th>
            <th>Pago al Ayudante (85%)</th>
          </tr>
        </thead>
        <tbody>
    `;

  clases.forEach(c => {
    const comision = (c.valor * 0.15).toFixed(0);
    const pago = (c.valor * 0.85).toFixed(0);
    tablaHTML += `
        <tr>
          <td>${c.ayudante}</td>
          <td>${c.estudiante}</td>
          <td>${c.fechaAgendamiento}</td>
          <td>${c.fechaClase}</td>
          <td>${c.estado}</td>
          <td>${c.calificacion}</td>
          <td>$${c.valor}</td>
          <td>$${comision}</td>
          <td>$${pago}</td>
        </tr>
      `;
  });

  tablaHTML += `</tbody></table>`;
  panel.innerHTML = tablaHTML;
}



function mostrarPostulaciones() {
  const panel = document.getElementById('panelInformacion');
  limpiarPanel();

  const postulaciones = [
    {
      usuario: 'Ana Martínez',
      fechaPostulacion: '2025-03-12',
      grado: 'Estudiante de ingeniería en informática'
    },
    {
      usuario: 'Juana Oyarce',
      fechaPostulacion: '2025-03-05',
      grado: 'Estudiante de pedagogía en lenguaje'
    },
    {
      usuario: 'Jorge Muñoz',
      fechaPostulacion: '2025-02-28',
      grado: 'Ingeniero Comercial'
    }
  ];

  let tablaHTML = `
      <h4>Postulaciones a ayudante</h4>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Fecha de postulación</th>
            <th>Grado</th>
            <th>Acción Clase</th>
          </tr>
        </thead>
        <tbody>
    `;

  postulaciones.forEach(c => {
    tablaHTML += `
        <tr>
          <td>${c.usuario}</td>
          <td>${c.fechaPostulacion}</td>
          <td>${c.grado}</td>
          <td><a href="/detallePostulacion" class="btn btn-primary">Ver más</a></td>
        </tr>
      `;
  });

  tablaHTML += `</tbody></table>`;
  panel.innerHTML = tablaHTML;
}
