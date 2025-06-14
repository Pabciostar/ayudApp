document.addEventListener("DOMContentLoaded", async () => {
    const contenedor = document.getElementById("marcoNotificaciones");
    const notificacionId = contenedor.dataset.id;
    const response = await fetch(`/api/notificacion/${notificacionId}/`);
    const notif = await response.json();

    let contenidoHTML = `
        <div class="mensaje-contenedor">
            <div class="mensaje-header">
                <h2>${notif.asunto}</h2>
                <div class="mensaje-meta">De: ${notif.remitente} • ${notif.fecha}</div>
            </div>
            <div class="mensaje-cuerpo">
                ${notif.cuerpo}
            </div>
    `;

    if (notif.asunto === "¿Cómo fue tu clase?") {
        contenidoHTML += `
            <hr>
            <form id="formularioCalificacion" class="mt-3">
                <div class="mb-3">
                    <label for="nota" class="form-label">Coloca tu nota (1 a 5):</label>
                    <select id="nota" name="nota" class="form-select" required>
                        <option value="" selected disabled>Selecciona una nota</option>
                        <option value="1">1 - Muy mala</option>
                        <option value="2">2 - Mala</option>
                        <option value="3">3 - Regular</option>
                        <option value="4">4 - Buena</option>
                        <option value="5">5 - Excelente</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="comentario" class="form-label">Escribe una pequeña reseña:</label>
                    <textarea id="comentario" name="comentario" class="form-control" rows="3" required></textarea>
                </div>
                <button type="submit" class="btn btn-success">Enviar calificación</button>
            </form>
        `;
    }

    contenidoHTML += `
        <a href="/notificaciones" class="btn btn-secondary btn-volver mt-3">← Volver a notificaciones</a>
        </div>
    `;

    contenedor.innerHTML = contenidoHTML;
});