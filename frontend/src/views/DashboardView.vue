<template>
  <div class="dashboard">
    <h1>Mein Dashboard</h1>
    <router-link to="/plan/erstellen" class="button">
      + Neuen Plan erstellen
    </router-link>

    <div v-if="loading">
      <p>Lade Pläne...</p>
    </div>

    <div v-else-if="plaene.length > 0">
      <h2>Meine Pläne</h2>
      <ul>
        <li v-for="plan in plaene" :key="plan.id">
          <router-link :to="`/plan/detail/${plan.id}`">
            Plan für {{ plan.landwirt_name }} ({{ plan.jahr }}) - Status: {{ plan.status }}
          </router-link>
        </li>
      </ul>
    </div>

    <div v-else>
      <p>Sie haben noch keine Pläne erstellt.</p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// Eine reaktive Variable, um die geladenen Pläne zu speichern
const plaene = ref([]);
// Eine Variable, um den Ladezustand zu verfolgen
const loading = ref(true);

// onMounted ist ein "Lifecycle Hook". Die Funktion darin wird automatisch
// ausgeführt, sobald die Komponente zum ersten Mal angezeigt wird.
onMounted(async () => {
  try {
    // Wir machen einen GET-Request an unseren geschützten Endpunkt
    const response = await axios.get('http://127.0.0.1:8000/api/plaene/');

    // Wir speichern die Antwort in unserer reaktiven Variable
    plaene.value = response.data;
    console.log("Pläne erfolgreich geladen:", response.data);

  } catch (error) {
    console.error("Fehler beim Laden der Pläne:", error);
    // Hier könnte man den Benutzer informieren, dass etwas schiefgelaufen ist
  } finally {
    // Egal ob Erfolg oder Fehler, das Laden ist beendet
    loading.value = false;
  }
});
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 10px;
}
.button {
  display: inline-block;
  padding: 10px 15px;
  background-color: #42b983;
  color: white;
  text-decoration: none;
  border-radius: 5px;
  margin-bottom: 20px;
}
</style>