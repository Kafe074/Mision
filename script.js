function controlCarrusel(btn, direccion) {
    // 1. Buscamos el contenedor padre del botón presionado
    const contenedor = btn.closest('.carrusel-container');
    const track = contenedor.querySelector('.carrusel-track');
    const imagenes = track.querySelectorAll('img');
    const total = imagenes.length;

    // 2. Obtenemos o inicializamos el índice actual de este carrusel específico
    if (contenedor.dataset.index === undefined) {
        contenedor.dataset.index = 0;
    }

    let index = parseInt(contenedor.dataset.index);

    // 3. Calculamos la nueva posición
    index += direccion;

    if (index < 0) {
        index = total - 1;
    } else if (index >= total) {
        index = 0;
    }

    // 4. Guardamos el nuevo índice y movemos el track
    contenedor.dataset.index = index;
    const desplazamiento = -index * (100 / total);
    track.style.transform = `translateX(${desplazamiento}%)`;
}