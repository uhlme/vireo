import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
// NEU: axios importieren
import axios from 'axios'

// --- NEUER STARTUP-CHECK ---
// Wir prüfen, ob ein Token im localStorage vorhanden ist,
// wenn die Anwendung zum ersten Mal geladen wird.
const token = localStorage.getItem('accessToken');

if (token) {
  // Wenn ja, setzen wir ihn als Standard-Header für alle zukünftigen axios-Anfragen.
  // So "erinnert" sich die App bei jedem Neuladen daran, eingeloggt zu sein.
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}
// --- ENDE DES CHECKS ---

createApp(App).use(router).mount('#app')