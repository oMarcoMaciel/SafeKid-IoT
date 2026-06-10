# SafeKid-IoT 🛡️ 👦

[![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MQTT](https://img.shields.io/badge/MQTT-3C3F41?style=for-the-badge&logo=mqtt&logoColor=white)](https://mqtt.org/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)](https://www.espressif.com/en/products/socs/esp32)

Sistema inteligente de monitoramento e controle de acesso para proteção de crianças em ambientes educacionais e institucionais.

---

## 📌 Objetivo e Motivação

O projeto **SafeKid-IoT** nasceu da necessidade de aumentar a segurança de crianças em escolas e creches. Utilizando tecnologia IoT (Internet das Coisas), o sistema permite o monitoramento em tempo real de acessos e a localização aproximada de alunos dentro de zonas monitoradas, oferecendo tranquilidade aos responsáveis e uma gestão eficiente para a instituição.

### Principais Benefícios:
- **Segurança Proativa**: Identificação instantânea de acessos não autorizados.
- **Rastreamento em Tempo Real**: Localização por zonas (Perto, Muito Perto, Longe) via RSSI.
- **Gestão Simplificada**: Registro e controle de crachás RFID através de uma interface web moderna.

---

## 🚀 Como Funciona?

O ecossistema SafeKid é composto por três camadas principais:

1.  **Hardware (Firmware)**: Dispositivos ESP32 equipados com leitores RFID RC522 e sensores de proximidade WiFi. Eles capturam os dados dos crachás e enviam via protocolo **MQTT** para o servidor.
2.  **Backend (API)**: Desenvolvido em **FastAPI (Python)**, o servidor processa as mensagens MQTT, valida as permissões no banco de dados **SQLite** e disponibiliza os dados via API REST para o frontend.
3.  **Frontend (Dashboard)**: Uma aplicação **Vue 3** moderna que exibe métricas em tempo real, logs de acesso e ferramentas de gerenciamento de dispositivos e alunos.

---

## 📸 Demonstração

### Dashboard Principal
Visualização geral de métricas e logs de acesso recentes.
![Dashboard](media/dashboard_page.png)

### Monitoramento e Rastreamento
Acompanhamento da localização e força de sinal dos dispositivos.
![Tracking](media/tracking_page.png)

### Gerenciamento de Scanners (ESP32)
Controle dos pontos de monitoramento distribuídos.
![Scanners](media/scanners_page.png)

### Descoberta de Dispositivos (Sniffer)
![Sniffer](media/sniffer.gif)
*Identificação automática de novas tags e dispositivos próximos.*

### Gerenciamento de Crachás
Interface para cadastro e edição de alunos e tags RFID.
![Cards](media/cards_page.png)

### Operação em Tempo Real
![RFID Scan](media/rid_card.gif)
*Escaneamento de cartão e resposta instantânea.*

---

## 🛠️ Stack Tecnológica

-   **Frontend**: Vue 3 (Composition API), Vite, Tailwind CSS, TanStack Query, Lucide Icons.
-   **Backend**: FastAPI, SQLAlchemy (ORM), Paho-MQTT, Pydantic.
-   **Firmware**: C++, PlatformIO, Arduino framework.
-   **Infraestrutura**: Broker Mosquitto (MQTT), SQLite.

---

## 📂 Estrutura do Projeto

-   `/backend`: API REST e serviços de monitoramento.
-   `/frontend`: Aplicação Web Vue 3.
-   `/firmware`: Código fonte para ESP32 e dispositivos Wemos.
-   `/docs`: Documentação técnica de hardware e planejamento.
-   `/scripts`: Scripts utilitários para seed de dados e upload de firmware.

---

## 🔗 Links Importantes

-   📄 [Artigo Completo do Projeto](https://docs.google.com/document/d/1ThVJpRU6ZdF_nexUTVyQ8nrOvbpMcFH3iXfswhdYLAI/edit?usp=sharing)
-   🏗️ [Esquemático ESP32 (Web)](https://app.cirkitdesigner.com/project/96b2e6a2-5b4b-4bac-97d2-bae0015d09af)
-   🔌 [Mapeamento de Pinos ESP32](docs/MAPEAMENTO_ESP32.md)
-   🗺️ [Plano de Implementação (Master Plan)](docs/MASTER_PLAN.md)

---

## 🛠️ Instalação e Execução

Consulte os READMEs específicos em cada pasta para instruções detalhadas de configuração:
- [Guia do Backend](backend/README.md)
- [Guia do Frontend](frontend/README.md)

---