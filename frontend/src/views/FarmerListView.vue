<template>
  <div class="farmer-list">
    <h1>Meine Landwirte</h1>
    <router-link to="/landwirte/neu" class="button">+ Neuen Landwirt anlegen</router-link>
    <ul>
      <li v-for="farmer in farmers" :key="farmer.id">
        {{ farmer.betriebsname }} - {{ farmer.vorname }} {{ farmer.nachname }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const farmers = ref([]);

onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/landwirte/');
    farmers.value = response.data;
  } catch (error) {
    console.error("Fehler beim Laden der Landwirte:", error);
  }
});
</script>

<style scoped>
  /* (ähnliches CSS wie bei den anderen Seiten) */
</style>