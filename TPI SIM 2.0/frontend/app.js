// Referencias UI
const btnTabResultados = document.getElementById('btn-tab-resultados');
const btnTabSimular = document.getElementById('btn-tab-simular');
const tabResultados = document.getElementById('tab-resultados');
const tabSimular = document.getElementById('tab-simular');

const estadoVacio = document.getElementById('estado-vacio');
const estadoConDatos = document.getElementById('estado-con-datos');

// Inputs Formulario
const inputX = document.getElementById('tiempo_simulacion');
const inputsSecundarios = document.querySelectorAll('#form-simulacion input:not(#tiempo_simulacion)');
const btnIniciar = document.getElementById('btn-iniciar');
const btnLimpiar = document.getElementById('btn-limpiar');
const form = document.getElementById('form-simulacion');
const loadingMsg = document.getElementById('loading-msg');

let chartRechazos = null;
let chartTiempos = null;

// --- NAVEGACIÓN ---
function switchTab(tab) {
    if (tab === 'resultados') {
        tabResultados.classList.remove('hidden');
        tabSimular.classList.add('hidden');
        btnTabResultados.classList.replace('border-transparent', 'border-white');
        btnTabSimular.classList.replace('border-white', 'border-transparent');
    } else {
        tabResultados.classList.add('hidden');
        tabSimular.classList.remove('hidden');
        btnTabSimular.classList.replace('border-transparent', 'border-white');
        btnTabResultados.classList.replace('border-white', 'border-transparent');
    }
}

btnTabResultados.addEventListener('click', () => switchTab('resultados'));
btnTabSimular.addEventListener('click', () => switchTab('simular'));

// --- LÓGICA DE FORMULARIO ---
inputX.addEventListener('input', () => {
    const tieneValor = inputX.value.trim() !== '';
    inputsSecundarios.forEach(input => {
        input.disabled = !tieneValor;
        if (!tieneValor) input.classList.add('bg-gray-100');
        else input.classList.remove('bg-gray-100');
    });
    btnIniciar.disabled = !tieneValor;
});

btnLimpiar.addEventListener('click', () => {
    form.reset();
    inputX.dispatchEvent(new Event('input')); // Dispara la validación para deshabilitar
    estadoVacio.classList.remove('hidden');
    estadoConDatos.classList.add('hidden');
    switchTab('resultados');
});

// --- CONSUMO DE API Y RENDERIZADO ---
btnIniciar.addEventListener('click', async () => {
    if(!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    loadingMsg.classList.remove('hidden');
    btnIniciar.disabled = true;

    const payload = {
        tiempo_simulacion: parseFloat(inputX.value),
        max_iteraciones: parseInt(document.getElementById('max_iteraciones').value),
        cantidad_iteraciones_mostrar: parseInt(document.getElementById('cantidad_iteraciones_mostrar').value),
        mostrar_desde_hora: parseFloat(document.getElementById('mostrar_desde_hora').value),
        media_llegadas: parseFloat(document.getElementById('media_llegadas').value),
        vacunacion_min: parseFloat(document.getElementById('vacunacion_min').value),
        vacunacion_max: parseFloat(document.getElementById('vacunacion_max').value),
        tiempo_observacion: parseFloat(document.getElementById('tiempo_observacion').value),
        capacidad_observacion: parseInt(document.getElementById('capacidad_observacion').value),
        capacidad_cola_externa: parseInt(document.getElementById('capacidad_cola_externa').value)
    };

    try {
        const res = await fetch('http://127.0.0.1:8000/simular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            cargarResultados();
        } else {
            alert("Error en la simulación. Revisa la consola.");
        }
    } catch (error) {
        alert("No se pudo conectar con el backend. ¿Está corriendo Uvicorn?");
    } finally {
        loadingMsg.classList.add('hidden');
        btnIniciar.disabled = false;
    }
});

async function cargarResultados() {
    try {
        const res = await fetch('http://127.0.0.1:8000/mostrar');
        const data = await res.json();

        if (data.mensaje) { // Maneja el caso de "No hay datos..."
            estadoVacio.classList.remove('hidden');
            estadoConDatos.classList.add('hidden');
            return;
        }

        renderizarGraficos(data.metricas);
        renderizarTabla(data.vector_estado);

        estadoVacio.classList.add('hidden');
        estadoConDatos.classList.remove('hidden');
        switchTab('resultados');

    } catch (error) {
        console.error(error);
    }
}

function renderizarTabla(vector) {
    const thead = document.getElementById('tabla-head');
    const tbody = document.getElementById('tabla-body');
    thead.innerHTML = '';
    tbody.innerHTML = '';

    if (vector.length === 0) return;

    // Crear cabeceras basadas en las claves del primer objeto
    const headers = Object.keys(vector[0]);
    let trHead = document.createElement('tr');
    headers.forEach(h => {
        let th = document.createElement('th');
        th.className = "px-4 py-3 font-semibold border-b whitespace-nowrap";
        th.textContent = h;
        trHead.appendChild(th);
    });
    thead.appendChild(trHead);

    // Crear filas
    vector.forEach((fila, index) => {
        let tr = document.createElement('tr');
        // Resaltar la última fila (Momento X)
        if (index === vector.length - 1) tr.className = "bg-blue-50 font-semibold";
        else tr.className = "hover:bg-gray-50";

        headers.forEach(h => {
            let td = document.createElement('td');
            td.className = "px-4 py-2 border-b whitespace-nowrap";
            td.textContent = fila[h] !== null ? fila[h] : '-';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function renderizarGraficos(metricas) {
    const ctxRechazos = document.getElementById('graficoRechazos').getContext('2d');
    const ctxTiempos = document.getElementById('graficoTiempos').getContext('2d');

    if (chartRechazos) chartRechazos.destroy();
    if (chartTiempos) chartTiempos.destroy();

    chartRechazos = new Chart(ctxRechazos, {
        type: 'pie',
        data: {
            labels: ['Ingresaron', 'Rechazados (Fila llena)'],
            datasets: [{
                data: [100 - metricas.porcentaje_rechazo_fila_externa, metricas.porcentaje_rechazo_fila_externa],
                backgroundColor: ['#10B981', '#EF4444']
            }]
        },
        options: { plugins: { title: { display: true, text: '% de Rechazo en Fila Externa' } } }
    });

    chartTiempos = new Chart(ctxTiempos, {
        type: 'bar',
        data: {
            labels: ['Bloqueo Puesto (min)', 'Permanencia Total (min)'],
            datasets: [{
                label: 'Promedio de Tiempos',
                data: [metricas.promedio_minutos_bloqueo, metricas.promedio_permanencia_sistema],
                backgroundColor: ['#F59E0B', '#3B82F6']
            }]
        },
        options: { scales: { y: { beginAtZero: true } }, plugins: { title: { display: true, text: 'Promedios de Tiempo' } } }
    });
}