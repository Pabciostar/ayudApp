function mostrarPasos(tipo) {
  const pasosAyudante = document.getElementById('pasos-ayudante');
  const pasosEstudiante = document.getElementById('pasos-estudiante');
  const btnAyudante = document.getElementById('btn-ayudante');
  const btnEstudiante = document.getElementById('btn-estudiante');

  if (tipo === 'ayudante') {
    pasosAyudante.style.display = 'block';
    pasosEstudiante.style.display = 'none';
    btnAyudante.classList.add('active');
    btnEstudiante.classList.remove('active');
  } else {
    pasosAyudante.style.display = 'none';
    pasosEstudiante.style.display = 'block';
    btnEstudiante.classList.add('active');
    btnAyudante.classList.remove('active');
  }
}