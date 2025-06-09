<template>
  <div class="edit-plan" v-if="plan">
    <h1>Plan für {{ plan.landwirt_name }} ({{ plan.jahr }}) bearbeiten</h1>
    <div class="form-group">
      <label for="status">Status</label>
      <select id="status" v-model="plan.status">
        <option value="Entwurf">Entwurf</option>
        <option value="Finalisiert">Finalisiert</option>
      </select>
    </div>
    <button @click="saveChanges">Änderungen speichern</button>
  </div>
  <div v-else>
    <p>Lade Plandaten...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const plan = ref(null);

onMounted(async () => {
  const planId = route.params.id;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/plaene/${planId}/`);
    plan.value = response.data;
  } catch (error) {
    console.error("Fehler beim Laden der Plandetails:", error);
  }
});

const saveChanges = async () => {
  const planId = route.params.id;
  try {
    // Wir senden nur die geänderten Daten mit PATCH
    await axios.patch(`http://127.0.0.1:8000/api/plaene/${planId}/`, {
      status: plan.value.status
    });
    alert('Änderungen gespeichert!');
    // Zurück zur Detailansicht
    router.push(`/plan/detail/${planId}`);
  } catch (error) {
    console.error("Fehler beim Speichern der Änderungen:", error);
  }
};
</script>

<style scoped>
.edit-plan {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

select {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border-radius: 4px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 12px 20px;
  font-size: 18px;
  background-color: #28a745; /* Grün für Speichern */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #218838;
}
</style>