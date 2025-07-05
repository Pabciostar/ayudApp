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

// Función para mostrar mensajes en el modal
function showSystemAlert(title, message, isSuccess = true) {
  const modal = new bootstrap.Modal(document.getElementById('systemAlertModal'));
  const modalTitle = document.getElementById('systemAlertModalTitle');
  const modalBody = document.getElementById('systemAlertModalBody');
  const modalHeader = document.querySelector('#systemAlertModal .modal-header');
  
  modalTitle.textContent = title;

  const icon = isSuccess 
    ? '<i class="bi bi-check-circle-fill me-2"></i>' 
    : '<i class="bi bi-exclamation-triangle-fill me-2"></i>';
  modalBody.innerHTML = `${icon} ${message}`;
  
  // Cambiar colores según sea éxito o error
  if(isSuccess) {
    modalHeader.classList.remove('bg-danger');
    modalHeader.classList.add('bg-success', 'text-white');
  } else {
    modalHeader.classList.remove('bg-success');
    modalHeader.classList.add('bg-danger', 'text-white');
  }
  
  modal.show();
}

// Función para manejar el estado activo de los botones del menú
function setActiveMenuItem(element) {
  const menuItems = document.querySelectorAll('.list-group-item-action');
  menuItems.forEach(item => {
    item.classList.remove('active');
  });
  element.classList.add('active');
}

function mostrarUsuarios(element) {
  limpiarPanel();
  if (element) setActiveMenuItem(element);
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
        <div class="d-flex gap-2 mt-3">
        <button id="guardar-cambios" class="btn btn-primary">Guardar cambios</button>
        <button id="descargar-excel" class="btn btn-success">Descargar Excel</button>
        </div>
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

      // Agregar evento al botón de descargar Excel
      document.getElementById('descargar-excel').addEventListener('click', () => {
        descargarExcel(data);
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
          showSystemAlert('Éxito', 'Cambios guardados exitosamente', true);
          mostrarUsuarios(); // Recarga la tabla con los datos actualizados
        }).catch(error => {
          console.error(error);
          showSystemAlert('Error', 'Hubo un error al guardar uno o más cambios', false);
        });
      };
    }
  }, 100); // Espera breve para asegurar que el botón existe
}

// Función para descargar Excel
function descargarExcel(data) {
  const sortedData = data.sort((a, b) => a.id_usuario - b.id_usuario);
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.json_to_sheet(sortedData);
  XLSX.utils.book_append_sheet(wb, ws, "Usuarios Registrados");
  XLSX.writeFile(wb, "usuarios_registrados.xlsx", { bookType: "xlsx" });
}


async function mostrarClasesAgendadas(element) {
  const panel = document.getElementById('panelInformacion');
  limpiarPanel();
  if (element) setActiveMenuItem(element);

  try {
    const response = await fetch('/api/clases-agendadas/'); // Ajusta URL según tu ruta real
    const clases = await response.json();

    let tablaHTML = `
      <h4>Clases Agendadas</h4>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Ayudante</th>
            <th>Estudiante (ID)</th>
            <th>Fecha Clase</th>
            <th>Estado</th>
            <th>Calificación</th>
            <th>Valor</th>
            <th>Comisión (15%)</th>
            <th>Pago al Ayudante (85%)</th>
          </tr>
        </thead>
        <tbody>
    `;

    clases.forEach(c => {
      const fechaAgendamiento = c.transaccion_id_transaccion?.fecha?.split('T')[0] || 'No disponible';
      const calificacion = (c.calificacion !== null && c.calificacion !== undefined)
        ? c.calificacion.toFixed(1)
        : 'No aplica';
      const comision = (c.valor * 0.15).toFixed(0);
      const pago = (c.valor * 0.85).toFixed(0);

      tablaHTML += `
        <tr>
          <td>${c.nombre_ayudante || 'Sin nombre'}</td>
          <td>${c.usuario_id_usuario}</td>
          <td>${c.fecha}</td>
          <td>${c.estado}</td>
          <td>${calificacion}</td>
          <td>$${c.valor}</td>
          <td>$${comision}</td>
          <td>$${pago}</td>
        </tr>
      `;
    });

    tablaHTML += `</tbody></table>`;
    panel.innerHTML = tablaHTML;

  } catch (error) {
    console.error('Error al cargar clases agendadas:', error);
    panel.innerHTML = `<p>Error al cargar las clases agendadas.</p>`;
  }
}


function mostrarPostulaciones(element) {
  const panel = document.getElementById('panelInformacion');
  limpiarPanel();
  if (element) setActiveMenuItem(element);

  fetch('/api/postulaciones/')
    .then(response => response.json())
    .then(postulaciones => {
      let tablaHTML = `
        <h4>Postulaciones a Ayudante</h4>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID Usuario</th>
              <th>Carrera</th>
              <th>Fecha y Hora (ID)</th>
              <th>Estado</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
      `;

      postulaciones.forEach(p => {
        const rawId = p.id_postulacion.toString();
        const year = "20" + rawId.substring(0, 2);
        const month = rawId.substring(2, 4);
        const day = rawId.substring(4, 6);
        const hour = rawId.substring(6, 8);
        const minute = rawId.substring(8, 10);
        const second = rawId.substring(10, 12);
        const fechaFormateada = `${day}/${month}/${year} ${hour}:${minute}:${second}`;


        tablaHTML += `
          <tr>
            <td>${p.usuario_id_usuario}</td>
            <td>${p.carrera}</td>
            <td>${fechaFormateada}</td>
            <td>${p.estado}</td>
            <td><a href="/detallePostulacion?id=${p.id_postulacion}" class="btn btn-primary">Ver más</a></td>
          </tr>
        `;
      });

      tablaHTML += `</tbody></table>`;
      panel.innerHTML = tablaHTML;
    });
}

function listarMaterias(element) {
  limpiarPanel();
  if (element) setActiveMenuItem(element);
  const panel = document.getElementById('panelInformacion');

  fetch('/api/materias/')
    .then(r => r.json())
    .then(materias => {
      return fetch('/api/ayudantes/')
        .then(r => r.json())
        .then(ayudantes => ({ materias, ayudantes }));
    })
    .then(({ materias, ayudantes }) => {
      let html = `
        <h3>Materias Registradas</h3>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID Materia</th>
              <th>Nombre</th>
              <th>Ayudante</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
      `;

      materias.forEach(materia => {
        const nombreAyudante = materia.nombre_ayudante || 'Desconocido';

        html += `
          <tr>
            <td>${materia.id_materia}</td>
            <td>${materia.nombre}</td>
            <td>${nombreAyudante}</td>
            <td>
              <button class="btn btn-sm btn-primary me-1" onclick="cargarFormularioEditarMateria('${materia.id_materia}', '${materia.nombre}', '${materia.id_ayudante}')">Editar</button>
              <button class="btn btn-sm btn-danger" onclick="eliminarMateria('${materia.id_materia}')">Eliminar</button>
            </td>
          </tr>
        `;
      });

      html += `
          </tbody>
        </table>

        <h4 id="tituloFormulario">Agregar Nueva Materia</h4>
        <form id="formMateria" class="row g-3 mt-2">
          <div class="col-md-4">
            <input type="text" class="form-control" id="idMateria" placeholder="ID Materia" required>
          </div>
          <div class="col-md-4">
            <input type="text" class="form-control" id="nombreMateria" placeholder="Nombre Materia" required>
          </div>
          <div class="col-md-4">
            <select id="idAyudanteMateria" class="form-select" required>
              <option value="">Selecciona un ayudante</option>
              ${ayudantes.map(a => `<option value="${a.id}">${a.usuario.nombres} ${a.usuario.apellidos}</option>`).join('')}
            </select>
          </div>
          <div class="col-12 mt-2">
            <button type="submit" class="btn btn-success" id="btnSubmit">Agregar Materia</button>
            <button type="button" class="btn btn-secondary" id="btnCancelarEdicion" style="display: none;">Cancelar</button>
          </div>
        </form>
      `;

      panel.innerHTML = html;

      let editando = false;

      document.getElementById('formMateria').addEventListener('submit', function (e) {
        e.preventDefault();

        const idMateria = document.getElementById('idMateria').value;
        const nombre = document.getElementById('nombreMateria').value;
        const idAyudante = document.getElementById('idAyudanteMateria').value;

        if (!idAyudante) {
          showSystemAlert('Error', 'Debes seleccionar un ayudante válido.', false);
          return;
        }

        const url = `/api/materias/${idMateria}/`;
        const metodo = editando ? 'PATCH' : 'POST';
        const mensajeExito = editando ? 'Materia actualizada correctamente' : 'Materia agregada correctamente';

        fetch(editando ? url : '/api/materias/', {
          method: metodo,
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({
            id_materia: idMateria,
            nombre: nombre,
            id_ayudante: idAyudante  // ya mapeado al serializer
          })
        })
          .then(response => {
            if (!response.ok) throw new Error('Error al guardar materia');
            return response.json();
          })
          .then(() => {
            showSystemAlert('Éxito', mensajeExito, true);
            listarMaterias();
          })
          .catch(error => {
            console.error(error);
            showSystemAlert('Error', 'No se pudo guardar la materia', false);
          });
      });

      document.getElementById('btnCancelarEdicion').addEventListener('click', resetFormularioMateria);

      window.cargarFormularioEditarMateria = (id, nombre, idAyudante) => {
        editando = true;
        document.getElementById('idMateria').value = id;
        document.getElementById('idMateria').disabled = true;
        document.getElementById('nombreMateria').value = nombre;
        document.getElementById('idAyudanteMateria').value = idAyudante;
        document.getElementById('btnSubmit').textContent = 'Guardar Cambios';
        document.getElementById('btnCancelarEdicion').style.display = 'inline-block';
        document.getElementById('tituloFormulario').textContent = 'Editar Materia';
      };

      function resetFormularioMateria() {
        editando = false;
        document.getElementById('formMateria').reset();
        document.getElementById('idMateria').disabled = false;
        document.getElementById('btnSubmit').textContent = 'Agregar Materia';
        document.getElementById('btnCancelarEdicion').style.display = 'none';
        document.getElementById('tituloFormulario').textContent = 'Agregar Nueva Materia';
      }
    })
    .catch(error => {
      console.error(error);
      showSystemAlert('Error', 'No se pudieron cargar las materias o ayudantes', false);
    });
}


function eliminarMateria(idMateria) {
  if (!confirm(`¿Estás seguro de eliminar la materia "${idMateria}"?`)) return;

  fetch(`/api/materias/${idMateria}/`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    }
  })
  .then(response => {
    if (response.ok) {
      showSystemAlert('Materia eliminada', 'La materia fue eliminada correctamente', true);
      listarMaterias();
    } else {
      throw new Error('Error al eliminar');
    }
  })
  .catch(error => {
    console.error(error);
    showSystemAlert('Error', 'No se pudo eliminar la materia', false);
  });
}