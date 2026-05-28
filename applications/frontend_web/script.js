const graficosCoordenacao = {};
const dadosMapaCalor = [
    0.18, 0.22, 0.38, 0.52, 0.61,
    0.15, 0.31, 0.63, 0.82, 0.76,
    0.1, 0.34, 0.78, 0.98, 0.84,
    0.08, 0.26, 0.54, 0.68, 0.57
];

function calcularCorMapaCalor(intensidade) {
    const valor = Math.max(0, Math.min(1, intensidade));
    const matiz = 220 - (220 * valor);
    const saturacao = 78;
    const luminosidade = 58 - (14 * valor);

    return `hsl(${matiz}, ${saturacao}%, ${luminosidade}%)`;
}

function renderizarMapaCalor() {
    const grade = document.getElementById('heatmap-grid');

    if (!grade) {
        return;
    }

    grade.innerHTML = '';

    dadosMapaCalor.forEach((intensidade) => {
        const celula = document.createElement('div');
        const percentual = Math.round(intensidade * 100);

        celula.className = 'heatmap-cell';
        celula.style.backgroundColor = calcularCorMapaCalor(intensidade);
        celula.dataset.value = `${percentual}%`;
        celula.title = `Presenca estimada: ${percentual}%`;

        grade.appendChild(celula);
    });
}

function formatarMinutosParaHorario(minutos) {
    const horas = String(Math.floor(minutos / 60)).padStart(2, '0');
    const restoMinutos = String(minutos % 60).padStart(2, '0');
    return `${horas}:${restoMinutos}`;
}

function criarGraficoBarras(elementoId, label, labels, dados, cor) {
    const contexto = document.getElementById(elementoId);

    if (!contexto) {
        return;
    }

    if (graficosCoordenacao[elementoId]) {
        graficosCoordenacao[elementoId].destroy();
    }

    graficosCoordenacao[elementoId] = new Chart(contexto, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label,
                data: dados,
                backgroundColor: cor,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#5f6c7b'
                    },
                    grid: {
                        color: 'rgba(44, 62, 80, 0.08)'
                    }
                },
                x: {
                    ticks: {
                        color: '#5f6c7b'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function criarGraficoLinhaHorario(elementoId, label, labels, dados, cor) {
    const contexto = document.getElementById(elementoId);

    if (!contexto) {
        return;
    }

    if (graficosCoordenacao[elementoId]) {
        graficosCoordenacao[elementoId].destroy();
    }

    graficosCoordenacao[elementoId] = new Chart(contexto, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label,
                data: dados,
                borderColor: cor,
                backgroundColor: `${cor}22`,
                pointBackgroundColor: cor,
                pointRadius: 4,
                tension: 0.35,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label(contextoTooltip) {
                            return `${label}: ${formatarMinutosParaHorario(contextoTooltip.parsed.y)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    min: 360,
                    max: 1080,
                    ticks: {
                        stepSize: 60,
                        color: '#5f6c7b',
                        callback(valor) {
                            return formatarMinutosParaHorario(valor);
                        }
                    },
                    grid: {
                        color: 'rgba(44, 62, 80, 0.08)'
                    }
                },
                x: {
                    ticks: {
                        color: '#5f6c7b'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function inicializarGraficosCoordenacao() {
    criarGraficoBarras(
        'grafico-faltas',
        'Faltas',
        ['Ana Clara', 'Joao Silva', 'Pedro Santos', 'Marina Costa', 'Lucas Lima'],
        [1, 4, 2, 0, 3],
        '#e74c3c'
    );

    criarGraficoLinhaHorario(
        'grafico-chegada',
        'Chegada media',
        ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'],
        [432, 428, 435, 440, 426, 470, 0],
        '#3498db'
    );

    criarGraficoBarras(
        'grafico-sala',
        'Tempo em sala',
        ['1A', '1B', '2A', '2B', '3A'],
        [285, 278, 301, 294, 288],
        '#2ecc71'
    );

    criarGraficoLinhaHorario(
        'grafico-saida',
        'Saida media',
        ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'],
        [742, 748, 745, 752, 738, 720, 0],
        '#f39c12'
    );
}

// Função para lidar com a seleção de perfil
function fazerLogin(perfil) {
    // Esconde a tela de login
    document.getElementById('login-view').style.display = 'none';
    
    // Mostra a estrutura do painel (Dashboard)
    document.getElementById('dashboard-view').style.display = 'block';

    // Pega as seções
    const secaoCoordenacao = document.getElementById('secao-coordenacao');
    const secaoPais = document.getElementById('secao-pais');
    const userDisplay = document.getElementById('user-role-display');

    // Lógica para mostrar apenas a seção correta baseada no perfil
    if (perfil === 'coordenacao') {
        secaoCoordenacao.style.display = 'block';
        secaoPais.style.display = 'none';
        userDisplay.innerText = 'Painel da Coordenação';
        inicializarGraficosCoordenacao();
    } else if (perfil === 'pais') {
        secaoCoordenacao.style.display = 'none';
        secaoPais.style.display = 'block';
        userDisplay.innerText = 'Painel do Responsável';
        renderizarMapaCalor();
    }
}

// Função para sair e voltar à tela inicial
function fazerLogout() {
    // Esconde o painel
    document.getElementById('dashboard-view').style.display = 'none';
    
    // Mostra novamente a tela de login
    document.getElementById('login-view').style.display = 'flex';
}