// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { isAuthenticated } from './auth' // Importiere unseren neuen Status

// Der Startup-Check für einen bestehenden Token bleibt bestehen
const token = localStorage.getItem('accessToken');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

// --- NEU: Der globale Response Interceptor ---
axios.interceptors.response.use(
  // Funktion für erfolgreiche Antworten (hier tun wir nichts)
  (response) => response,
  // Funktion für fehlerhafte Antworten
  (error) => {
    // Prüfen, ob der Fehler ein 401-Status ist
    if (error.response && error.response.status === 401) {
      // 1. Token aus dem Speicher entfernen
      localStorage.removeItem('accessToken');
      // 2. Auth-Header für zukünftige Anfragen entfernen
      delete axios.defaults.headers.common['Authorization'];
      // 3. Unseren globalen Status auf 'false' setzen
      isAuthenticated.value = false;
      // 4. Den Benutzer zur Login-Seite weiterleiten
      router.push('/'); // Annahme: '/' ist deine Login-Seite
      console.log("Token abgelaufen oder ungültig. Automatischer Logout.");
    }
    // Wichtig: Den Fehler trotzdem weitergeben, damit die ursprüngliche Komponente ihn fangen kann
    return Promise.reject(error);
  }
);
// --- ENDE DES INTERCEPTORS ---

createApp(App).use(router).mount('#app')