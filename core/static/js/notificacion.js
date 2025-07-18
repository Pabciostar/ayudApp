document.addEventListener("DOMContentLoaded", async () => {
    const contenedor = document.getElementById("marcoNotificaciones");
    const notificacionId = contenedor.dataset.id;
    const response = await fetch(`/api/notificacion/${notificacionId}/`);
    const notif = await response.json();

    let contenidoHTML = `
        
        <div class="contenedor-general-mensaje">
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
        </div>

    `;

    contenedor.innerHTML = contenidoHTML;

    const form = document.getElementById("formularioCalificacion");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const nota = document.getElementById("nota").value;
            const comentario = document.getElementById("comentario").value;

            const response = await fetch(`/api/notificacion/${notificacionId}/calificar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ nota, comentario })
            });

            const result = await response.json();

            if (response.ok) {
                alert("Tu calificación ha sido enviada.");
                window.location.href = "/notificaciones";
            } else {
                alert("Hubo un error al enviar tu calificación:\n" + (result.error || "Inténtalo más tarde."));
            }
        });
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '='))
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return cookieValue;
}