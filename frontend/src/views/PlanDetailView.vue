<template>
  <div v-if="plan" class="plan-detail">
    <div class="actions">
  <router-link :to="`/plan/bearbeiten/${plan.id}`" class="button-edit">
    Plan Bearbeiten
  </router-link>
  <button @click="deletePlan" class="button-delete">Plan Löschen</button>
  </div>
    <h1>Pflanzenschutzplan für {{ plan.landwirt_name }} ({{ plan.jahr }})</h1>
    <p><strong>Status:</strong> {{ plan.status }}</p>

    <div v-for="kultur in plan.kulturen" :key="kultur.id" class="kultur-block">
      <h2>Kultur: {{ kultur.name }}</h2>
      <div v-for="behandlung in kultur.behandlungen" :key="behandlung.id" class="behandlung-block">
        <h3>{{ behandlung.titel || 'Behandlung' }}</h3>
        <h4>Produkte im Mix:</h4>
        <ul>
          <li v-for="produkt_im_mix in behandlung.produkte_im_mix" :key="produkt_im_mix.id">
            <strong>{{ produkt_im_mix.produkt.produktname }}</strong>
            <span> ({{ produkt_im_mix.produkt.wirkstoff }})</span>
            <div class="dosierung">Aufwandmenge: {{ produkt_im_mix.aufwandmenge }} {{ produkt_im_mix.einheit }}</div>
          </li>
        </ul>
        <p v-if="behandlung.eigene_notizen" class="notiz"><strong>Notiz:</strong> {{ behandlung.eigene_notizen }}</p>
      </div>
    </div>
  </div>
  <div v-else>
    <p>Lade Plandaten...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import  { useToast } from "vue-toastification";

const toast = useToast();
const route = useRoute(); // Gibt uns Zugriff auf die aktuelle URL und ihre Parameter
const router = useRouter();
const plan = ref(null);   // Hier speichern wir die Plandaten vom Backend

// Diese Funktion wird ausgeführt, sobald die Seite geladen wird
onMounted(async () => {
  const planId = route.params.id; // Holt die ID aus der URL (z.B. die '1' aus '/plan/detail/1')
  try {
    // Rufe die Detail-API für genau diesen Plan auf
    const response = await axios.get(`http://127.0.0.1:8000/api/plaene/${planId}/`);
    plan.value = response.data;
  } catch (error) {
    console.error("Fehler beim Laden der Plandetails:", error);
  }
});
const deletePlan = async () => {
  const planId = route.params.id;
  // Sicherheitsabfrage, um versehentliches Löschen zu verhindern
  if (window.confirm("Möchtest du diesen Plan wirklich endgültig löschen?")) {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/plaene/${planId}/`);
      toast.success('Plan erfolgreich gelöscht.');
      // Nach dem Löschen zurück zum Dashboard
      router.push('/dashboard');
    } catch (error) {
      console.error("Fehler beim Löschen des Plans:", error);
      toast.error('Der Plan konnte nicht gelöscht werden.');
    }
  }
};
</script>

<style scoped>
.plan-detail { padding: 20px; max-width: 900px; margin: auto; }
.kultur-block { 
  margin-bottom: 30px; 
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}
.behandlung-block { 
  border: 1px solid #e3e3e3; 
  padding: 15px; 
  margin-top: 15px; 
  border-radius: 5px; 
  background-color: white;
}
h1, h2, h3, h4 { margin-top: 0; }
h2 { border-bottom: 2px solid #eee; padding-bottom: 10px; }
h3 { margin-bottom: 10px; }
ul { list-style: none; padding-left: 0; }
li { margin-bottom: 10px; }
.dosierung { padding-left: 15px; color: #555; }
.notiz { font-style: italic; color: #333; margin-top: 10px; }
.actions {
  margin-bottom: 20px;
  text-align: right;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
.button-edit, .button-delete {
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  text-decoration: none; /* Wichtig für den router-link */
  font-size: 14px;
}
.button-edit {
  background-color: #007bff; /* Blau für Bearbeiten */
}
.button-edit:hover {
  background-color: #0056b3;
}
.button-delete {
  background-color: #dc3545; /* Rot für Löschen */
}
.button-delete:hover {
  background-color: #c82333;
}
</style>