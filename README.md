# 🎨 OFI - Piattaforma Integrata Arte & Eventi

Una piattaforma web che unisce marketplace per opere d'arte, live streaming di performance artistiche, aste in tempo reale e gestione eventi.

## 🚀 Funzionalità Principali

- **Marketplace Opere d'Arte**
  - Opere fisiche e digitali
  - Upload opere con dettagli automatici
  - Acquisto diretto o all'asta

- **Live Streaming**
  - Performance artistiche in diretta
  - Chat in tempo reale
  - Salvataggio automatico replay

- **Aste in Tempo Reale**
  - Durante le live
  - Timer estendibile post-live
  - Sistema di offerte in tempo reale

- **Gestione Eventi**
  - Creazione e promozione eventi
  - Sistema QR per accesso
  - Gestione partecipanti

## 🛠️ Tecnologie Utilizzate

- **Backend**
  - Django 4+
  - Django REST Framework
  - Django Channels (WebSocket)
  - PostgreSQL
  - Redis

- **Frontend**
  - React.js
  - Tailwind CSS
  - WebSocket client
  - QR Code generator

## 📋 Prerequisiti

- Python 3.8+
- Node.js 14+
- PostgreSQL
- Redis

## 🔧 Installazione

1. Clona il repository:
```bash
git clone https://github.com/yourusername/ofi.git
cd ofi
```

2. Crea e attiva l'ambiente virtuale:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installa le dipendenze Python:
```bash
pip install -r requirements.txt
```

4. Configura le variabili d'ambiente:
```bash
cp .env.example .env
# Modifica .env con le tue configurazioni
```

5. Esegui le migrazioni:
```bash
python manage.py migrate
```

6. Crea un superuser:
```bash
python manage.py createsuperuser
```

7. Avvia il server di sviluppo:
```bash
python manage.py runserver
```

## 🌐 Configurazione Frontend

1. Installa le dipendenze Node.js:
```bash
cd frontend
npm install
```

2. Avvia il server di sviluppo:
```bash
npm run dev
```

## 📝 Documentazione API

La documentazione dell'API è disponibile all'indirizzo `/api/docs/` quando il server è in esecuzione.

## 🔐 Ruoli Utente

- **Guest**: Visualizza contenuti e genera QR per eventi
- **Base**: Acquisti, offerte, commenti
- **Artista**: Upload opere, live streaming, aste
- **Artista Verificato**: Badge e visibilità aumentata
- **Admin**: Gestione completa della piattaforma
- **Promoter**: Gestione eventi assegnati

## 📄 Licenza

Questo progetto è sotto licenza MIT. Vedi il file `LICENSE` per i dettagli.

## 👥 Contribuire

1. Fai il fork del progetto
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Committa le tue modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Pusha al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📞 Supporto

Per supporto, email support@ofi.com o apri un issue nel repository. 