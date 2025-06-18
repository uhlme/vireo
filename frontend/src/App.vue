<template>
  <nav v-if="isAuthenticated">
    <router-link to="/dashboard">Dashboard</router-link> |
    <router-link to="/plan/erstellen">Plan erstellen</router-link> |
    <router-link to="/landwirte">Meine Landwirte</router-link> |
    <button @click="handleLogout" class="logout-button">Logout</button>
  </nav>
  <router-view/>
</template>

<script setup>
import { isAuthenticated } from './auth';
// NEU: useRouter für die Weiterleitung importieren
import { useRouter } from 'vue-router';
import axios from 'axios';

// NEU: Den Router initialisieren
const router = useRouter();

// NEU: Die Funktion, die beim Klick auf den Logout-Button ausgeführt wird
const handleLogout = () => {
  // 1. Lösche den Token aus dem lokalen Speicher des Browsers
  localStorage.removeItem('accessToken');

  // 2. Entferne den Authorization-Header aus allen zukünftigen Axios-Anfragen
  delete axios.defaults.headers.common['Authorization'];

  // 3. Setze unseren globalen Status auf 'ausgeloggt'
  isAuthenticated.value = false;

  // 4. Leite den Benutzer zur Login-Seite weiter
  router.push('/');
};
</script>

<style>
/* Dein globales CSS bleibt unverändert */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}

/* NEU: Ein einfacher Style für den Logout-Button */
.logout-button {
  background: none;
  border: none;
  color: #2c3e50;
  cursor: pointer;
  text-decoration: underline;
  font-size: 1em; /* Gleiche Grösse wie die Links */
  font-family: inherit; /* Gleiche Schriftart wie die Links */
  font-weight: bold;
  padding: 0;
  margin-left: 5px;
}
.logout-button:hover {
  color: #42b983;
}
</style>