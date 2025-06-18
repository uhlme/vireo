<template>
  <div class="create-plan">
    <h1>Neuen Pflanzenschutzplan erstellen</h1>
    
    <div class="form-block">
      <h2>Stammdaten</h2>
      <div class="form-group">
        <label>Landwirt</label>
        <select v-model="plan.landwirtId">
          <option disabled value="">Bitte einen Landwirt wählen</option>
          <option v-for="landwirt in meta.landwirte" :key="landwirt.id" :value="landwirt.id">
            {{ landwirt.betriebsname }} ({{ landwirt.vorname }} {{ landwirt.nachname }})
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="plan-jahr">Jahr</label>
        <input type="number" id="plan-jahr" v-model="plan.jahr">
      </div>
    </div>

    <div class="form-block" v-if="plan.landwirtId && plan.jahr">
      <h2>Kulturen</h2>
      <div class="add-section">
        <select v-model="formState.selectedKulturId">
          <option disabled value="">Kultur auswählen...</option>
          <option v-for="kultur in meta.kulturen" :key="kultur.id" :value="kultur.id">
            {{ kultur.name }}
          </option>
        </select>
        <button @click="addKultur" class="add-button-small">Kultur zum Plan hinzufügen</button>
      </div>
    </div>

    <div class="plan-summary">
      <div v-for="(kultur, kulturIndex) in plan.kulturen" :key="kultur.meta_id" class="kultur-item">
        <h3>
          <span>Kultur: {{ kultur.name }}</span>
          <button @click="deleteKultur(kulturIndex)" class="button-delete-small">Ganze Kultur entfernen</button>
        </h3>
        
        <div v-for="(behandlung, behandlungIndex) in kultur.behandlungen" :key="behandlungIndex" class="behandlung-item">
          <div class="behandlung-header">
            <span>{{ behandlung.titel }}</span>
            <button @click="deleteBehandlung(kulturIndex, behandlungIndex)" class="button-delete-small">X</button>
          </div>
          
          <ul class="produkt-liste">
            <li v-for="(p, pIndex) in behandlung.produkte_im_mix" :key="p.produktId">
              {{ p.produktName }} - {{ p.aufwandmenge }}
              <button @click="deleteProdukt(kulturIndex, behandlungIndex, pIndex)" class="button-delete-tiny">x</button>
            </li>
          </ul>

          <div class="add-produkt-section">
            <button v-if="formState.activeBehandlung !== `${kulturIndex}-${behandlungIndex}`" @click="showAddProductForm(kulturIndex, behandlungIndex)" class="add-button-small">+ Produkt zu dieser Behandlung hinzufügen</button>
            
            <div v-if="formState.activeBehandlung === `${kulturIndex}-${behandlungIndex}`" class="add-produkt-form">
              <select v-model="formState.selectedProdukt" @change="onProduktSelect()">
                <option disabled value="">Produkt wählen...</option>
                <option v-for="p in formState.produkte" :key="p.id" :value="p.id">{{ p.produktname }}</option>
              </select>
              <select v-if="formState.selectedProdukt" v-model="formState.selectedSchaderreger" @change="onSchaderregerSelect()">
                <option disabled value="">Schaderreger wählen...</option>
                <option v-for="s in formState.schaderreger" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
              <input v-if="formState.selectedSchaderreger" type="text" v-model="formState.aufwandmenge" placeholder="Aufwandmenge" />
              <button @click="addProductToBehandlung(kulturIndex, behandlungIndex)">OK</button>
            </div>
          </div>
        </div>

        <div class="add-section behandlung-add">
          <input type="text" v-model="formState.behandlungTitel[kultur.meta_id]" placeholder="Titel der Behandlung, z.B. Herbizid im Frühling">
          <button @click="addBehandlung(kulturIndex)" class="add-button-small">+ Behandlung hinzufügen</button>
        </div>
      </div>
    </div>

    <button @click="savePlan" class="save-button" v-if="plan.kulturen.length > 0">Ganzen Plan speichern</button>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useToast } from "vue-toastification";

const toast = useToast();
const router = useRouter();

// Das Haupt-Objekt, das den gesamten Plan enthält und am Ende gespeichert wird
const plan = reactive({
  landwirtId: '',
  jahr: new Date().getFullYear(),
  kulturen: [], 
});

// Statische Daten für die Dropdowns
const meta = reactive({
  landwirte: [],
  kulturen: [],
});

// Temporärer Zustand für die verschiedenen Formulare auf der Seite
const formState = reactive({
  selectedKulturId: '',
  behandlungTitel: {},
  activeBehandlung: null, // z.B. "0-1" für Kultur-Index 0, Behandlungs-Index 1
  produkte: [],
  loadingProdukte: false,
  selectedProdukt: '',
  schaderreger: [],
  loadingSchaderreger: false,
  selectedSchaderreger: '',
  aufwandmenge: '',
  wartefrist: '',
});

// Lädt die initialen Stammdaten (Landwirte und alle möglichen Kulturen)
onMounted(async () => {
  try {
    const [landwirtResponse, kulturResponse] = await Promise.all([
      axios.get('http://127.0.0.1:8000/api/landwirte/'),
      axios.get('http://127.0.0.1:8000/api/kulturen/'),
    ]);
    meta.landwirte = landwirtResponse.data;
    meta.kulturen = kulturResponse.data;
  } catch (error) { console.error("Fehler beim Laden der Stammdaten:", error); }
});

// Fügt eine Kultur zum Plan hinzu
const addKultur = () => {
  if (!formState.selectedKulturId) return;
  const schonVorhanden = plan.kulturen.some(k => k.meta_id === formState.selectedKulturId);
  if (schonVorhanden) { toast.error("Diese Kultur wurde bereits zum Plan hinzugefügt."); return; }

  const kulturMeta = meta.kulturen.find(k => k.id === formState.selectedKulturId);
  plan.kulturen.push({
    meta_id: kulturMeta.id,
    name: kulturMeta.name,
    behandlungen: [],
  });
};

const deleteKultur = (kulturIndex) => { plan.kulturen.splice(kulturIndex, 1); };

// Fügt eine leere, benannte Behandlung zu einer spezifischen Kultur hinzu
const addBehandlung = (kulturIndex) => {
  const kulturMetaId = plan.kulturen[kulturIndex].meta_id;
  const titel = formState.behandlungTitel[kulturMetaId];
  if (!titel) { toast.error("Bitte einen Titel für die Behandlung eingeben."); return; }
  plan.kulturen[kulturIndex].behandlungen.push({ titel: titel, produkte_im_mix: [] });
  formState.behandlungTitel[kulturMetaId] = '';
};

const deleteBehandlung = (kulturIndex, behandlungIndex) => { plan.kulturen[kulturIndex].behandlungen.splice(behandlungIndex, 1); };

// Aktiviert das "Produkt hinzufügen"-Formular für eine spezifische Behandlung
const showAddProductForm = async (kulturIndex, behandlungIndex) => {
  formState.activeBehandlung = `${kulturIndex}-${behandlungIndex}`;
  formState.selectedProdukt = '';
  formState.produkte = [];
  formState.schaderreger = [];
  formState.selectedSchaderreger = '';
  formState.aufwandmenge = '';
  formState.wartefrist = '';
  formState.loadingProdukte = true;
  try {
    const kulturId = plan.kulturen[kulturIndex].meta_id;
    const response = await axios.get(`http://127.0.0.1:8000/api/produkte/?kultur=${kulturId}`);
    formState.produkte = response.data;
  } catch (e) { console.error(e); }
  finally { formState.loadingProdukte = false; }
};

// Lädt die gefilterten Schaderreger, wenn ein Produkt ausgewählt wird
const onProduktSelect = async () => {
  const kulturIndex = formState.activeBehandlung.split('-')[0];
  const kulturId = plan.kulturen[kulturIndex].meta_id;
  if (!formState.selectedProdukt) return;
  formState.loadingSchaderreger = true;
  formState.schaderreger = [];
  formState.selectedSchaderreger = '';
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/schaderreger/?kultur=${kulturId}&produkt=${formState.selectedProdukt}`);
    formState.schaderreger = response.data;
  } catch (error) { console.error("Fehler beim Laden der Schaderreger:", error); }
  finally { formState.loadingSchaderreger = false; }
};

// Lädt die Zulassungsdetails, wenn ein Schaderreger ausgewählt wird
const onSchaderregerSelect = async () => {
  const kulturIndex = formState.activeBehandlung.split('-')[0];
  const kulturId = plan.kulturen[kulturIndex].meta_id;
  if (!formState.selectedSchaderreger) return;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/zulassungen/?kultur=${kulturId}&produkt=${formState.selectedProdukt}&schaderreger=${formState.selectedSchaderreger}`);
    if (response.data && response.data.length > 0) {
      const zulassungDetails = response.data[0];
      formState.aufwandmenge = zulassungDetails.aufwandmenge;
      formState.wartefrist = zulassungDetails.wartefrist;
    }
  } catch (error) { console.error("Fehler beim Laden der Zulassungsdetails:", error); }
};

// Fügt das ausgewählte Produkt zur richtigen Behandlung im Plan hinzu
const addProductToBehandlung = () => {
  const [kulturIndex, behandlungIndex] = formState.activeBehandlung.split('-').map(Number);
  const produkt = formState.produkte.find(p => p.id === formState.selectedProdukt);
  plan.kulturen[kulturIndex].behandlungen[behandlungIndex].produkte_im_mix.push({
    produktId: formState.selectedProdukt,
    produktName: produkt.produktname,
    aufwandmenge: formState.aufwandmenge,
  });
  formState.activeBehandlung = null; // Formular schliessen
};

// Löscht ein spezifisches Produkt aus einem Tank-Mix
const deleteProdukt = (kIndex, bIndex, pIndex) => {
  plan.kulturen[kIndex].behandlungen[bIndex].produkte_im_mix.splice(pIndex, 1);
};

// Speichert den gesamten Plan im Backend
const savePlan = async () => {
  if (!plan.landwirtId || !plan.jahr) { toast.error("Bitte Landwirt und Jahr auswählen."); return; }
  try {
    await axios.post('http://127.0.0.1:8000/api/plaene/', plan);
    toast.success('Plan erfolgreich erstellt!');
    router.push('/dashboard');
  } catch (error) {
    console.error("Fehler beim Speichern des Plans:", error.response?.data);
    toast.error("Fehler beim Speichern.");
  }
};
</script>

<style scoped>
.create-plan { max-width: 900px; margin: 40px auto; padding: 20px; }
.form-block { background-color: #f9f9f9; border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
.add-section { display: flex; gap: 10px; align-items: center; }
.behandlung-add { margin-top: 15px; padding-top: 15px; border-top: 1px dashed #ccc; }
.kultur-item { border: 1px solid #e3e3e3; padding: 15px; margin-top: 15px; border-radius: 5px; }
.kultur-item h3 { display: flex; justify-content: space-between; align-items: center; }
.behandlung-item { padding: 10px; margin-left: 20px; margin-top: 10px; background-color: #fff; border: 1px solid #eee; }
.behandlung-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
.produkt-liste { margin-left: 20px; margin-top: 10px; }
.produkt-liste li { display: flex; justify-content: space-between; font-size: 14px; padding: 4px 0; }
.save-button { width: 100%; padding: 12px; font-size: 18px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }
.add-button-small, .button-delete-small { font-size: 12px; padding: 5px 10px; white-space: nowrap; }
.button-delete-tiny { font-size: 10px; padding: 2px 5px; }
.add-produkt-section { margin-top: 10px; }
.add-produkt-form { display: flex; gap: 10px; align-items: center; margin-top: 10px; padding: 10px; background: #f0f0f0; border-radius: 4px; }
</style>