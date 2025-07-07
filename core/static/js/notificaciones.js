document.addEventListener("DOMContentLoaded", async () => {
    const userDiv = document.getElementById("data-usuario");
    const userId = userDiv.dataset.usuarioId;

    try {
        const response = await fetch(`/api/notificaciones/${userId}/`);
       if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const notificaciones = await response.json();

        // ✅ Ordenar por fecha – más reciente primero
        notificaciones.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));

        const contenedor = document.getElementById("contenedorNotificaciones");
        contenedor.innerHTML = "";

        if (notificaciones.length === 0) {
            contenedor.innerHTML = `
                <div class="no-notificaciones text-center my-5">
                    <i class="bi bi-bell-slash-fill icono-sin-notificaciones"></i>
                    <p class="mensaje-sin-notificaciones">No hay notificaciones disponibles.</p>
                </div>
            `;
        } else {
            // ✅ Mostramos las notificaciones ordenadas
            contenedor.innerHTML = notificaciones.map(notif => `
                <div class="mensaje-contenedor mb-4">
                    <div class="mensaje-header">
                        <h2>${notif.asunto}</h2>
                        <div class="mensaje-meta">De: ${notif.remitente} • ${notif.fecha}</div>
                    </div>
                    <div class="mensaje-cuerpo">
                        ${notif.cuerpo.substring(0, 100)}...
                        <br><a href="/notificacion/${notif.id_notificacion}/" class="btn btn-sm btn-outline-primary mt-2">Ver detalle</a>
                    </div>
                </div>
            `).join('');
        }

    } catch (error) {
        console.error("Error al cargar notificaciones:", error);
        contenedor.innerHTML = `
            <div class="alert alert-danger mt-3">
                No se pudieron cargar las notificaciones.
            </div>
        `;
    }
});