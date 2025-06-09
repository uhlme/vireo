<template>
  <div class="edit-plan" v-if="plan">
    <h1>Plan für {{ plan.landwirt_name }} ({{ plan.jahr }}) bearbeiten</h1>

    <div class="form-block">
      <h2>Stammdaten</h2>
      <div class="form-group">
        <label for="status">Plan-Status</label>
        <select id="status" v-model="plan.status">
          <option value="Entwurf">Entwurf</option>
          <option value="Finalisiert">Finalisiert</option>
        </select>
      </div>
    </div>

    <div class="summary-block">
      <h2>Bestehende Behandlungen im Plan</h2>
      <div v-for="kultur in plan.kulturen" :key="kultur.id" class="kultur-block">
        <h3>Kultur: {{ kultur.name }}</h3>
        <div v-for="behandlung in kultur.behandlungen" :key="behandlung.id" class="behandlung-block">
          <h4>{{ behandlung.titel || 'Behandlung' }}</h4>
          <ul>
            <li v-for="produkt_im_mix in behandlung.produkte_im_mix" :key="produkt_im_mix.id">
              <strong>{{ produkt_im_mix.produkt.produktname }}</strong>
              <span> - {{ produkt_im_mix.aufwandmenge }} {{ produkt_im_mix.einheit }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <button @click="saveChanges" class="save-button">Änderungen speichern</button>

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
    // Wir senden nur die geänderten Status-Daten mit PATCH
    await axios.patch(`http://127.0.0.1:8000/api/plaene/${planId}/`, {
      status: plan.value.status
    });
    alert('Änderungen gespeichert!');
    router.push(`/plan/detail/${planId}`);
  } catch (error) {
    console.error("Fehler beim Speichern der Änderungen:", error);
  }
};
</script>

<style scoped>
.edit-plan { padding: 20px; max-width: 900px; margin: auto; }
.form-block, .summary-block {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.kultur-block { margin-top: 20px; }
.behandlung-block { border: 1px solid #e3e3e3; padding: 15px; margin-top: 10px; border-radius: 5px; background-color: white; }
h1, h2, h3, h4 { margin-top: 0; }
.form-group { margin-bottom: 20px; }
label { display: block; margin-bottom: 8px; font-weight: bold; }
select { width: 100%; padding: 10px; font-size: 16px; }
.save-button {
  width: 100%;
  padding: 12px 20px;
  font-size: 18px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.save-button:hover { background-color: #218838; }
ul { list-style: none; padding-left: 0; }
</style>