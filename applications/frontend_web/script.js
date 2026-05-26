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
    } else if (perfil === 'pais') {
        secaoCoordenacao.style.display = 'none';
        secaoPais.style.display = 'block';
        userDisplay.innerText = 'Painel do Responsável';
    }
}

// Função para sair e voltar à tela inicial
function fazerLogout() {
    // Esconde o painel
    document.getElementById('dashboard-view').style.display = 'none';
    
    // Mostra novamente a tela de login
    document.getElementById('login-view').style.display = 'flex';
}