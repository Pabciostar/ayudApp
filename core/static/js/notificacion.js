document.addEventListener("DOMContentLoaded", async () => {
    const notificacionId = "{{ id_notificacion }}";
    const response = await fetch(`/api/notificacion/${notificacionId}/`);
    const notif = await response.json();

    const contenedor = document.getElementById("contenedorNotificacion");
    contenedor.innerHTML = `
        <div class="mensaje-contenedor">
            <div class="mensaje-header">
                <h2>${notif.asunto}</h2>
                <div class="mensaje-meta">De: ${notif.remitente} • ${notif.fecha}</div>
            </div>
            <div class="mensaje-cuerpo">
                ${notif.cuerpo}
            </div>
            <a href="/notificaciones/" class="btn btn-secondary btn-volver">← Volver a notificaciones</a>
        </div>
    `;
});