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
            <th>Grado</th>
            <th>Asignaturas</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          <!-- Usuario 1 - Estudiante -->
          <tr>
            <td>Ana Pérez</td>
            <td>12.345.678-9</td>
            <td>ana@example.com</td>
            <td>Estudiante</td>
            <td>No aplica</td>
            <td>No aplica</td>
            <td>
              <div class="dropdown">
                <button class="btn btn-warning dropdown-toggle" type="button" id="dropdownMenuButton1" data-bs-toggle="dropdown" aria-expanded="false">
                  Cambiar Rol
                </button>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton1">
                  <li><a class="dropdown-item" href="#">Usuario</a></li>
                  <li><a class="dropdown-item" href="#">Ayudante</a></li>
                  <li><a class="dropdown-item" href="#">Administrador</a></li>
                  <li><a class="dropdown-item" href="#">Baneado/eliminar</a></li>
                </ul>
              </div>
            </td>
          </tr>
  
          <!-- Usuario 2 - Ayudante -->
          <tr>
            <td>Carlos Soto</td>
            <td>23.456.789-0</td>
            <td>carlos@example.com</td>
            <td>Ayudante</td>
            <td>3° Medio</td>
            <td>Matemáticas, Física</td>
            <td>
              <div class="dropdown">
                <button class="btn btn-warning dropdown-toggle" type="button" id="dropdownMenuButton2" data-bs-toggle="dropdown" aria-expanded="false">
                  Cambiar Rol
                </button>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton2">
                  <li><a class="dropdown-item" href="#">Usuario</a></li>
                  <li><a class="dropdown-item" href="#">Ayudante</a></li>
                  <li><a class="dropdown-item" href="#">Administrador</a></li>
                  <li><a class="dropdown-item" href="#">Baneado/eliminar</a></li>
                </ul>
              </div>
            </td>
          </tr>
  
          <!-- Usuario 3 - Administrador -->
          <tr>
            <td>María Ruiz</td>
            <td>34.567.890-1</td>
            <td>maria@example.com</td>
            <td>Administrador</td>
            <td>No aplica</td>
            <td>No aplica</td>
            <td>
              <div class="dropdown">
                <button class="btn btn-warning dropdown-toggle" type="button" id="dropdownMenuButton3" data-bs-toggle="dropdown" aria-expanded="false">
                  Cambiar Rol
                </button>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton3">
                  <li><a class="dropdown-item" href="#">Usuario</a></li>
                  <li><a class="dropdown-item" href="#">Ayudante</a></li>
                  <li><a class="dropdown-item" href="#">Administrador</a></li>
                  <li><a class="dropdown-item" href="#">Baneado/eliminar</a></li>
                </ul>
              </div>
            </td>
          </tr>
  
          <!-- Usuario 4 - Estudiante -->
          <tr>
            <td>Lucía Fernández</td>
            <td>45.678.901-2</td>
            <td>luciafdez@example.com</td>
            <td>Estudiante</td>
            <td>No aplica</td>
            <td>No aplica</td>
            <td>
              <div class="dropdown">
                <button class="btn btn-warning dropdown-toggle" type="button" id="dropdownMenuButton4" data-bs-toggle="dropdown" aria-expanded="false">
                  Cambiar Rol
                </button>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton4">
                  <li><a class="dropdown-item" href="#">Usuario</a></li>
                  <li><a class="dropdown-item" href="#">Ayudante</a></li>
                  <li><a class="dropdown-item" href="#">Administrador</a></li>
                  <li><a class="dropdown-item" href="#">Baneado/eliminar</a></li>
                </ul>
              </div>
            </td>
          </tr>
  
          <!-- Usuario 5 - Ayudante -->
          <tr>
            <td>Pedro Torres</td>
            <td>56.789.012-3</td>
            <td>pedrotorres@example.com</td>
            <td>Ayudante</td>
            <td>4° Medio</td>
            <td>Lenguaje, Historia</td>
            <td>
              <div class="dropdown">
                <button class="btn btn-warning dropdown-toggle" type="button" id="dropdownMenuButton5" data-bs-toggle="dropdown" aria-expanded="false">
                  Cambiar Rol
                </button>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton5">
                  <li><a class="dropdown-item" href="#">Usuario</a></li>
                  <li><a class="dropdown-item" href="#">Ayudante</a></li>
                  <li><a class="dropdown-item" href="#">Administrador</a></li>
                  <li><a class="dropdown-item" href="#">Baneado/eliminar</a></li>
                </ul>
              </div>
            </td>
          </tr>
          
          <!-- Usuario 6 - Estudiante -->
          <tr>
            <td>Ana Rivas</td>
            <td>67.890.123-4</td>
            <td>anarivas@example.com</td>
            <td>Estudiante</td>
            <td>No aplica</td>
            <td>No aplica</td>
            <td>
              <div class="dropdown">
                <button class="btn btn-warning dropdown-toggle" type="button" id="dropdownMenuButton6" data-bs-toggle="dropdown" aria-expanded="false">
                  Cambiar Rol
                </button>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton6">
                  <li><a class="dropdown-item" href="#">Usuario</a></li>
                  <li><a class="dropdown-item" href="#">Ayudante</a></li>
                  <li><a class="dropdown-item" href="#">Administrador</a></li>
                  <li><a class="dropdown-item" href="#">Baneado/eliminar</a></li>
                </ul>
              </div>
            </td>
          </tr>
  
          <!-- Usuario 7 - Estudiante -->
          <tr>
            <td>David Sánchez</td>
            <td>78.901.234-5</td>
            <td>davidsanchez@example.com</td>
            <td>Estudiante</td>
            <td>No aplica</td>
            <td>No aplica</td>
            <td>
              <div class="dropdown">
                <button class="btn btn-warning dropdown-toggle" type="button" id="dropdownMenuButton7" data-bs-toggle="dropdown" aria-expanded="false">
                  Cambiar Rol
                </button>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton7">
                  <li><a class="dropdown-item" href="#">Usuario</a></li>
                  <li><a class="dropdown-item" href="#">Ayudante</a></li>
                  <li><a class="dropdown-item" href="#">Administrador</a></li>
                  <li><a class="dropdown-item" href="#">Baneado/eliminar</a></li>
                </ul>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    `;
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
  