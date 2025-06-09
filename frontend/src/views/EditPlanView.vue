<template>
  <div class="edit-plan" v-if="plan">
    <h1>Plan für {{ plan.landwirt_name }} ({{ plan.jahr }}) bearbeiten</h1>

    <!-- Block 1: Stammdaten des Plans bearbeiten -->
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

    <!-- Block 2: Bestehende Behandlungen anzeigen und löschen -->
    <div class="summary-block">
      <h2>Bestehende Behandlungen</h2>
      <p v-if="behandlungen.length === 0">Noch keine Behandlungen für diesen Plan vorhanden.</p>
      <div v-for="(behandlung, index) in behandlungen" :key="index" class="behandlung-item">
        <span>
          <strong>Kultur:</strong> {{ behandlung.kulturName }} | 
          <strong>Produkt:</strong> {{ behandlung.produktName }} | 
          <strong>Aufwand:</strong> {{ behandlung.aufwandmenge }}
        </span>
        <button @click="deleteBehandlung(index)" class="button-delete-small">Löschen</button>
      </div>
    </div>

    <!-- Block 3: Formular zum Hinzufügen einer neuen Behandlung -->
    <div class="form-container">
      <h3>Neue Behandlung hinzufügen</h3>
      <div class="step">
        <h4>Schritt 1: Kultur auswählen</h4>
        <select v-model="formState.selectedKultur" @change="onKulturSelect">
          <option disabled value="">Bitte eine Kultur wählen</option>
          <option v-for="kultur in meta.kulturen" :key="kultur.id" :value="kultur.id">
            {{ kultur.name }}
          </option>
        </select>
      </div>
  
      <div class="step" v-if="formState.selectedKultur">
        <h4>Schritt 2: Produkt auswählen</h4>
        <select v-model="formState.selectedProdukt" @change="onProduktSelect">
          <option disabled value="">Bitte ein Produkt wählen</option>
          <option v-for="produkt in formState.produkte" :key="produkt.id" :value="produkt.id">
            {{ produkt.produktname }}
          </option>
        </select>
      </div>

      <div class="step" v-if="formState.selectedProdukt">
        <h4>Schritt 3: Schaderreger auswählen</h4>
        <select v-model="formState.selectedSchaderreger" @change="onSchaderregerSelect">
          <option disabled value="">Bitte einen Schaderreger wählen</option>
          <option v-for="erreger in formState.schaderreger" :key="erreger.id" :value="erreger.id">
            {{ erreger.name }}
          </option>
        </select>
      </div>

      <div class="step" v-if="formState.selectedSchaderreger">
        <h4>Schritt 4: Details festlegen</h4>
        <input type="text" v-model="formState.aufwandmenge" placeholder="Aufwandmenge">
        <input type="text" v-model="formState.wartefrist" placeholder="Wartefrist" class="input-spacing">
        <button @click="addBehandlung" class="add-button">Behandlung hinzufügen</button>
      </div>
    </div>

    <button @click="saveChanges" class="save-button">Ganzen Plan mit Änderungen speichern</button>

  </div>
  <div v-else>
    <p>Lade Plandaten...</p>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

// Hält die Haupt-Plandaten
const plan = ref(null);
// Hält die "Arbeitskopie" der Behandlungen, die wir bearbeiten
const behandlungen = ref([]);
// Hält die Metadaten für die Dropdowns
const meta = reactive({
  kulturen: [],
});
// Hält den Zustand des "Neue Behandlung hinzufügen"-Formulars
const formState = reactive({
  selectedKultur: '',
  produkte: [],
  selectedProdukt: '',
  schaderreger: [],
  selectedSchaderreger: '',
  aufwandmenge: '',
  wartefrist: '',
});

// onMounted lädt alle initialen Daten
onMounted(async () => {
  const planId = route.params.id;
  try {
    const planResponse = await axios.get(`http://127.0.0.1:8000/api/plaene/${planId}/`);
    plan.value = planResponse.data;
    
    let tempBehandlungen = [];
    plan.value.kulturen.forEach(kultur => {
      kultur.behandlungen.forEach(b => {
        b.produkte_im_mix.forEach(p => {
          tempBehandlungen.push({
            kulturId: kultur.id, 
            kulturName: kultur.name,
            produktId: p.produkt.id,
            produktName: p.produkt.produktname,
            aufwandmenge: `${p.aufwandmenge} ${p.einheit}`,
            wartefrist: "N/A", // Dieses Feld müssen wir noch vom Backend bekommen
          });
        });
      });
    });
    behandlungen.value = tempBehandlungen;

    const kulturResponse = await axios.get('http://127.0.0.1:8000/api/kulturen/');
    meta.kulturen = kulturResponse.data;

  } catch (error) {
    console.error("Fehler beim Laden der Plandetails:", error);
  }
});

const onKulturSelect = async () => {
  if (!formState.selectedKultur) return;
  formState.produkte = []; 
  formState.selectedProdukt = '';
  formState.schaderreger = [];
  formState.selectedSchaderreger = '';
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/produkte/?kultur=${formState.selectedKultur}`);
    formState.produkte = response.data;
  } catch (error) { console.error("Fehler beim Laden der Produkte:", error); } 
};

const onProduktSelect = async () => {
  if (!formState.selectedProdukt) return;
  formState.schaderreger = [];
  formState.selectedSchaderreger = '';
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/schaderreger/?kultur=${formState.selectedKultur}&produkt=${formState.selectedProdukt}`);
    formState.schaderreger = response.data;
  } catch (error) { console.error("Fehler beim Laden der Schaderreger:", error); }
};

const onSchaderregerSelect = async () => {
  if (!formState.selectedSchaderreger) return;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/zulassungen/?kultur=${formState.selectedKultur}&produkt=${formState.selectedProdukt}&schaderreger=${formState.selectedSchaderreger}`);
    if (response.data && response.data.length > 0) {
      const zulassungDetails = response.data[0];
      formState.aufwandmenge = zulassungDetails.aufwandmenge;
      formState.wartefrist = zulassungDetails.wartefrist;
    }
  } catch (error) { console.error("Fehler beim Laden der Zulassungsdetails:", error); }
};

const addBehandlung = () => {
  const kulturName = meta.kulturen.find(k => k.id === formState.selectedKultur)?.name;
  const produktName = formState.produkte.find(p => p.id === formState.selectedProdukt)?.produktname;
  
  behandlungen.value.push({
    kulturId: formState.selectedKultur, kulturName: kulturName,
    produktId: formState.selectedProdukt, produktName: produktName,
    aufwandmenge: formState.aufwandmenge,
    wartefrist: formState.wartefrist,
  });

  formState.selectedKultur = '';
  formState.produkte = [];
  formState.selectedProdukt = '';
  formState.schaderreger = [];
  formState.selectedSchaderreger = '';
  formState.aufwandmenge = '';
  formState.wartefrist = '';
};

const deleteBehandlung = (index) => {
  behandlungen.value.splice(index, 1);
};

const saveChanges = async () => {
  const planId = route.params.id;
  try {
    const payload = {
      status: plan.value.status,
      jahr: plan.value.jahr,
      landwirt: plan.value.landwirt,
      behandlungen: behandlungen.value,
    };
    await axios.put(`http://127.0.0.1:8000/api/plaene/${planId}/`, payload);
    alert('Änderungen gespeichert!');
    router.push(`/plan/detail/${planId}`);
  } catch (error) {
    console.error("Fehler beim Speichern der Änderungen:", error.response?.data);
  }
};
</script>

<style scoped>
.edit-plan { max-width: 900px; margin: 40px auto; padding: 20px; }
.form-block, .summary-block, .form-container { background-color: #f9f9f9; border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
h1, h2, h3, h4 { margin-top: 0; }
h2, h3 { border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }
.form-group { margin-bottom: 20px; }
label { display: block; margin-bottom: 8px; font-weight: bold; }
input, select { width: 100%; padding: 10px; font-size: 16px; border-radius: 4px; border: 1px solid #ccc; box-sizing: border-box; }
.input-spacing { margin-top: 15px; }
.save-button, .add-button { width: 100%; padding: 12px 20px; font-size: 18px; color: white; border: none; border-radius: 5px; cursor: pointer; }
.save-button { background-color: #28a745; margin-top: 20px; }
.save-button:hover { background-color: #218838; }
.add-button { background-color: #007bff; margin-top: 15px; }
.add-button:hover { background-color: #0056b3; }
.behandlung-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
.behandlung-item:last-child { border-bottom: none; }
.button-delete-small { background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
.button-delete-small:hover { background-color: #c82333; }
.step { margin-bottom: 20px; }
</style>