<template>
  <div class="login-container">
    <h2>Anmeldung</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Benutzername</label>
        <input type="text" id="username" v-model="username" />
      </div>
      <div class="form-group">
        <label for="password">Passwort</label>
        <input type="password" id="password" v-model="password" />
      </div>
      <button type="submit">Anmelden</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { isAuthenticated } from '../auth'; // Importiere unseren Status

const username = ref('');
const password = ref('');
// NEU: Den Router initialisieren
const router = useRouter();

const handleLogin = async () => {
  console.log('Sende Login-Daten an das Backend...');
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/token/', {
      username: username.value,
      password: password.value
    });

    console.log('Erfolgreich eingeloggt!', response.data);

    // --- HIER IST DIE NEUE LOGIK ---
    const accessToken = response.data.access;

    // 1. Speichere den Token im lokalen Speicher des Browsers
    localStorage.setItem('accessToken', accessToken);

    // 2. Setze den "Authorization"-Header für alle zukünftigen axios-Anfragen
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
    
    isAuthenticated.value = true;
    // 3. Leite den Benutzer zum Dashboard weiter
    router.push('/dashboard');
    // --- ENDE DER NEUEN LOGIK ---

  } catch (error) {
    if (error.response) {
      console.error('Login-Daten fehlerhaft:', error.response.data);
    } else if (error.request) {
      console.error('Keine Antwort vom Server. Läuft das Backend auf Port 8000 und ist CORS konfiguriert?');
    } else {
      console.error('Fehler:', error.message);
    }
  }
};
</script>

<style scoped>
/* ... dein CSS bleibt unverändert ... */
</style>