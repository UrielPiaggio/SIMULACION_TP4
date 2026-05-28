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
    const tfoot = document.getElementById('tabla-foot');
    
    thead.innerHTML = '';
    tbody.innerHTML = '';
    if (tfoot) tfoot.innerHTML = '';

    if (vector.length === 0) return;

    // 1. SEPARAR COLUMNAS GENERALES DE LAS DE PACIENTES
    const todasLasKeys = Object.keys(vector[0]);
    // Filtramos las llaves que empiezan con "P1_", "P2_", etc.
    const keysPacientes = todasLasKeys.filter(k => /^P\d+_/.test(k));
    // El resto son datos generales de la simulación
    const keysGenerales = todasLasKeys.filter(k => !/^P\d+_/.test(k));

    // Calcular cuántos bloques de pacientes hay (si el máximo en python fue 15, serán 15)
    // Cada paciente tiene 5 campos (ID, Estado, Llegada, FinVac, FinObs)
    const totalColumnasPacientes = keysPacientes.length;

    // --- FILA 1: SUPER-CABECERA ---
    const trSuper = document.createElement('tr');

    // Celda vacía/azul para los datos generales
    const thGralSuper = document.createElement('th');
    thGralSuper.colSpan = keysGenerales.length;
    thGralSuper.className = "px-4 py-2 text-center bg-blue-200 text-blue-900 border-b font-bold";
    thGralSuper.textContent = "Datos de Simulación";
    trSuper.appendChild(thGralSuper);

    // Celda naranja/roja gigante para "Seguimiento pacientes" (estilo Excel de la imagen)
    const thPacientesSuper = document.createElement('th');
    thPacientesSuper.colSpan = totalColumnasPacientes;
    thPacientesSuper.className = "px-4 py-3 text-center bg-orange-700 text-white border-b font-bold uppercase tracking-wider text-base";
    thPacientesSuper.textContent = "Seguimiento pacientes";
    trSuper.appendChild(thPacientesSuper);
    
    thead.appendChild(trSuper);

    // --- FILA 2: SUB-CABECERA (Nombres de las columnas individuales) ---
    const trSub = document.createElement('tr');

    // Sub-cabeceras generales
    keysGenerales.forEach(k => {
        let th = document.createElement('th');
        th.className = "px-4 py-2 font-semibold border-b border-r bg-blue-100 text-blue-900 whitespace-nowrap text-xs text-center";
        th.textContent = k;
        trSub.appendChild(th);
    });

    // Sub-cabeceras de pacientes (Limpia el "P1_")
    keysPacientes.forEach(k => {
        let th = document.createElement('th');
        // Identificar qué propiedad es (ID, Estado, Llegada, etc.)
        let nombreLimpio = k.replace(/^P\d+_/, '');
        
        // Estilo visual para separar visualmente los bloques de pacientes (borde derecho más grueso al final de cada paciente)
        let esFinBloque = nombreLimpio === "FinObs";
        th.className = `px-2 py-2 font-semibold border-b text-center whitespace-nowrap text-xs bg-gray-100 text-gray-700 ${esFinBloque ? 'border-r-2 border-r-gray-400' : 'border-r'}`;
        
        th.textContent = nombreLimpio;
        trSub.appendChild(th);
    });

    thead.appendChild(trSub);

    // --- CUERPO DE LA TABLA (FILAS DE DATOS) ---
    vector.forEach((fila, index) => {
        let tr = document.createElement('tr');
        let esUltimaFila = (index === vector.length - 1);

        if (esUltimaFila) {
            tr.className = "bg-blue-50 font-bold text-blue-900"; 
        } else {
            tr.className = "hover:bg-gray-50 odd:bg-white even:bg-gray-50/50";
        }

        // Renderizar celdas generales
        keysGenerales.forEach(k => {
            let td = document.createElement('td');
            td.className = "px-4 py-2 border-b border-r text-center whitespace-nowrap";
            td.textContent = fila[k] !== null ? fila[k] : '-';
            tr.appendChild(td);
        });

        // Renderizar celdas de pacientes
        keysPacientes.forEach(k => {
            let td = document.createElement('td');
            let nombreLimpio = k.replace(/^P\d+_/, '');
            let esFinBloque = nombreLimpio === "FinObs";
            
            td.className = `px-2 py-1 border-b text-center whitespace-nowrap text-xs ${esFinBloque ? 'border-r-2 border-r-gray-400' : 'border-r'}`;
            
            let valor = fila[k];
            // Si el valor es null (columna vacía porque no hay paciente asignado), se dibuja vacío como el Excel
            td.textContent = (valor !== null && valor !== undefined) ? valor : '';
            
            // Opcional: Color tenue si la celda tiene datos de un paciente para destacar sobre el vacío
            if (fila[k] !== null && fila[k] !== undefined) {
                if (nombreLimpio === "Estado") {
                    if (valor === "Vacunandose") td.classList.add("text-green-600", "font-medium");
                    if (valor === "Observacion") td.classList.add("text-amber-600", "font-medium");
                }
            }

            tr.appendChild(td);
        });

        if (esUltimaFila && tfoot) {
            tfoot.appendChild(tr);
        } else {
            tbody.appendChild(tr);
        }
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