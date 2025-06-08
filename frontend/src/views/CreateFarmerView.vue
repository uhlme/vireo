<template>
  <div class="create-farmer">
    <h1>Neuen Landwirt anlegen</h1>
    <form @submit.prevent="saveFarmer">
      <div class="form-group">
        <label for="betriebsname">Betriebsname</label>
        <input type="text" v-model="farmer.betriebsname" required>
      </div>
      <div class="form-group">
        <label for="vorname">Vorname</label>
        <input type="text" v-model="farmer.vorname" required>
      </div>
      <div class="form-group">
        <label for="nachname">Nachname</label>
        <input type="text" v-model="farmer.nachname" required>
      </div>
      <div class="form-group">
        <label for="adresse">Adresse</label>
        <input type="text" v-model="farmer.adresse">
      </div>
      <div class="form-group">
        <label for="email">E-Mail</label>
        <input type="email" v-model="farmer.email">
      </div>
      <div class="form-group">
        <label for="telefon">Telefon</label>
        <input type="text" v-model="farmer.telefon">
      </div>
      <button type="submit">Landwirt speichern</button>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const farmer = reactive({
  betriebsname: '',
  vorname: '',
  nachname: '',
  adresse: '',
  email: '',
  telefon: '',
});

const saveFarmer = async () => {
  try {
    await axios.post('http://127.0.0.1:8000/api/landwirte/', farmer);
    // Bei Erfolg zurück zur Listenansicht
    router.push('/landwirte');
  } catch (error) {
    console.error("Fehler beim Speichern des Landwirts:", error.response.data);
  }
};
</script>