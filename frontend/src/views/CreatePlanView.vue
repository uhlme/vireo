<template>
  <div class="create-plan">
    <h1>Neuen Pflanzenschutzplan erstellen</h1>
    
    <div class="plan-header">
      <div class="form-group">
        <label>Landwirt</label>
        <select v-model="selectedLandwirt">
          <option disabled value="">Bitte einen Landwirt wählen</option>
          <option v-for="landwirt in landwirte" :key="landwirt.id" :value="landwirt.id">
            {{ landwirt.betriebsname }} ({{ landwirt.vorname }} {{ landwirt.nachname }})
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="plan-jahr">Jahr</label>
        <input type="number" id="plan-jahr" v-model="planJahr" placeholder="z.B. 2025">
      </div>
    </div>

    <div class="form-container" v-if="selectedLandwirt && planJahr">
      <h3>Behandlungen hinzufügen</h3>
      <div class="step">
        <h4>Schritt 1: Kultur auswählen</h4>
        <select v-if="!loadingKulturen" v-model="selectedKultur" @change="onKulturSelect">
          <option disabled value="">Bitte eine Kultur wählen</option>
          <option v-for="kultur in kulturen" :key="kultur.id" :value="kultur.id">
            {{ kultur.name }}
          </option>
        </select>
        <p v-else>Lade Kulturen...</p>
      </div>
  
      <div class="step" v-if="selectedKultur">
        <h4>Schritt 2: Produkt auswählen</h4>
        <select v-if="!loadingProdukte" v-model="selectedProdukt" @change="onProduktSelect">
          <option disabled value="">Bitte ein Produkt wählen</option>
          <option v-for="produkt in produkte" :key="produkt.id" :value="produkt.id">
            {{ produkt.produktname }}
          </option>
        </select>
        <p v-if="loadingProdukte">Lade zugelassene Produkte...</p>
        <p v-if="!loadingProdukte && produkte.length === 0">Keine zugelassenen Produkte für diese Kultur gefunden.</p>
      </div>

      <div class="step" v-if="selectedProdukt">
        <h4>Schritt 3: Schaderreger auswählen</h4>
        <select v-if="!loadingSchaderreger" v-model="selectedSchaderreger" @change="onSchaderregerSelect">
          <option disabled value="">Bitte einen Schaderreger wählen</option>
          <option v-for="erreger in schaderreger" :key="erreger.id" :value="erreger.id">
            {{ erreger.name }}
          </option>
        </select>
        <p v-if="loadingSchaderreger">Lade zugelassene Schaderreger...</p>
      </div>

      <div class="step" v-if="selectedSchaderreger">
        <h4>Schritt 4: Details festlegen</h4>
        <div class="form-group">
          <label for="aufwandmenge">Aufwandmenge</label>
          <input type="text" id="aufwandmenge" v-model="aufwandmenge" placeholder="Wird automatisch gefüllt...">
        </div>
        <div class="form-group">
          <label for="wartefrist">Wartefrist</label>
          <input type="text" id="wartefrist" v-model="wartefrist" placeholder="Wird automatisch gefüllt...">
        </div>
        <button @click="addBehandlung" class="add-button">Behandlung zum Plan hinzufügen</button>
      </div>
    </div>

    <div class="plan-summary" v-if="behandlungen.length > 0">
      <h2>Aktueller Plan</h2>
      <div v-for="(behandlung, index) in behandlungen" :key="index" class="behandlung-item">
        <p><strong>Behandlung {{ index + 1 }}</strong></p>
        <ul>
          <li><strong>Kultur:</strong> {{ behandlung.kulturName }}</li>
          <li><strong>Produkt:</strong> {{ behandlung.produktName }}</li>
          <li><strong>Schaderreger:</strong> {{ behandlung.schaderregerName }}</li>
          <li><strong>Aufwandmenge:</strong> {{ behandlung.aufwandmenge }}</li>
          <li><strong>Wartefrist:</strong> {{ behandlung.wartefrist }}</li>
        </ul>
      </div>
       <div class="final-save">
        <button @click="savePlan" class="save-button">Ganzen Plan speichern</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();

// Zustände für Plan-Kopfdaten
const landwirte = ref([]);
const selectedLandwirt = ref('');
const planJahr = ref(new Date().getFullYear());

// Zustände für das Formular
const kulturen = ref([]);
const loadingKulturen = ref(true);
const selectedKultur = ref('');
const produkte = ref([]);
const loadingProdukte = ref(false);
const selectedProdukt = ref('');
const schaderreger = ref([]);
const loadingSchaderreger = ref(false);
const selectedSchaderreger = ref('');
const aufwandmenge = ref('');
const wartefrist = ref('');

// Hier sammeln wir die fertigen Behandlungen für den Plan
const behandlungen = ref([]);

// onMounted lädt die Stammdaten (Landwirte und Kulturen)
onMounted(async () => {
  try {
    const kulturResponse = await axios.get('http://127.0.0.1:8000/api/kulturen/');
    kulturen.value = kulturResponse.data;
  } catch (error) { console.error("Fehler beim Laden der Kulturen:", error); } 
  finally { loadingKulturen.value = false; }

  try {
    const landwirtResponse = await axios.get('http://127.0.0.1:8000/api/landwirte/');
    landwirte.value = landwirtResponse.data;
  } catch (error) { console.error("Fehler beim Laden der Landwirte:", error); }
});

// Lädt die GEFILTERTEN Produkte, wenn eine Kultur ausgewählt wird
const onKulturSelect = async () => {
  if (!selectedKultur.value) return;
  loadingProdukte.value = true;
  produkte.value = []; 
  selectedProdukt.value = '';
  schaderreger.value = [];
  selectedSchaderreger.value = '';
  aufwandmenge.value = '';
  wartefrist.value = '';
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/produkte/?kultur=${selectedKultur.value}`);
    produkte.value = response.data;
  } catch (error) { console.error("Fehler beim Laden der Produkte:", error); } 
  finally { loadingProdukte.value = false; }
};

// Lädt die GEFILTERTEN Schaderreger, wenn ein Produkt ausgewählt wird
const onProduktSelect = async () => {
  if (!selectedProdukt.value) return;
  loadingSchaderreger.value = true;
  schaderreger.value = [];
  selectedSchaderreger.value = '';
  aufwandmenge.value = '';
  wartefrist.value = '';
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/schaderreger/?kultur=${selectedKultur.value}&produkt=${selectedProdukt.value}`);
    schaderreger.value = response.data;
  } catch (error) { console.error("Fehler beim Laden der Schaderreger:", error); }
  finally { loadingSchaderreger.value = false; }
};

// Lädt die Zulassungs-Details, wenn ein Schaderreger ausgewählt wird
const onSchaderregerSelect = async () => {
  if (!selectedSchaderreger.value) return;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/zulassungen/?kultur=${selectedKultur.value}&produkt=${selectedProdukt.value}&schaderreger=${selectedSchaderreger.value}`);
    if (response.data && response.data.length > 0) {
      const zulassungDetails = response.data[0];
      aufwandmenge.value = zulassungDetails.aufwandmenge;
      wartefrist.value = zulassungDetails.wartefrist;
    }
  } catch (error) {
    console.error("Fehler beim Laden der Zulassungsdetails:", error);
  }
};

// Fügt eine fertige Behandlung zur Plan-Liste hinzu
const addBehandlung = () => {
  const kulturName = kulturen.value.find(k => k.id === selectedKultur.value)?.name;
  const produktName = produkte.value.find(p => p.id === selectedProdukt.value)?.produktname;
  const schaderregerName = schaderreger.value.find(s => s.id === selectedSchaderreger.value)?.name;
  const neueBehandlung = {
    kulturId: selectedKultur.value, kulturName: kulturName,
    produktId: selectedProdukt.value, produktName: produktName,
    schaderregerId: selectedSchaderreger.value, schaderregerName: schaderregerName,
    aufwandmenge: aufwandmenge.value,
    wartefrist: wartefrist.value,
  };
  behandlungen.value.push(neueBehandlung);

  selectedProdukt.value = '';
  selectedSchaderreger.value = '';
  aufwandmenge.value = '';
  wartefrist.value = '';
  produkte.value = [];
  schaderreger.value = [];
};

// Speichert den gesamten Plan im Backend
const savePlan = async () => {
  const payload = {
    landwirt: selectedLandwirt.value,
    jahr: planJahr.value,
    behandlungen: behandlungen.value.map(b => ({
      kulturId: b.kulturId,
      produktId: b.produktId,
      schaderregerId: b.schaderregerId,
      aufwandmenge: b.aufwandmenge,
      wartefrist: b.wartefrist, // Senden wir mit, auch wenn das Backend es noch nicht speichert
      produktName: b.produktName
    }))
  };
  try {
    await axios.post('http://127.0.0.1:8000/api/plaene/', payload);
    alert('Plan erfolgreich gespeichert!');
    router.push('/dashboard');
  } catch (error) {
    console.error("Fehler beim Speichern des Plans:", error.response?.data || error.message);
    alert('Fehler beim Speichern des Plans.');
  }
};
</script>

<style scoped>
.create-plan { padding: 20px; max-width: 800px; margin: auto; }
.plan-header { background-color: #e9ecef; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
.form-container { background-color: #fdfdfd; padding: 20px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 20px; }
.step { margin-bottom: 30px; }
.form-group { margin-bottom: 15px; }
label { display: block; margin-bottom: 5px; font-weight: bold; }
input, select { width: 100%; padding: 10px; font-size: 16px; border-radius: 4px; border: 1px solid #ccc; box-sizing: border-box; }
.add-button { padding: 10px 15px; font-size: 16px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
.add-button:hover { background-color: #0056b3; }
.plan-summary { margin-top: 40px; border-top: 2px solid #eee; padding-top: 20px; }
.behandlung-item { background-color: #f9f9f9; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
.behandlung-item ul { list-style: none; padding-left: 0; margin: 0; }
.behandlung-item li { padding: 2px 0; }
.final-save { margin-top: 20px; }
.save-button { padding: 12px 20px; font-size: 18px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
.save-button:hover { background-color: #218838; }
</style>