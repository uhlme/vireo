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
            <button v-if="formState.activeBehandlung !== `${kulturIndex}-${behandlungIndex}`" @click="showAddProductForm(kultur, kulturIndex, behandlungIndex)" class="add-button-small">+ Produkt zu dieser Behandlung hinzufügen</button>
            
            <div v-if="formState.activeBehandlung === `${kulturIndex}-${behandlungIndex}`" class="add-produkt-form">
              <select v-model="formState.selectedProdukt" @change="onProduktSelect(kultur)">
                <option disabled value="">Produkt wählen...</option>
                <option v-for="p in formState.produkte" :key="p.id" :value="p.id">{{ p.produktname }}</option>
              </select>
              <p v-if="formState.loadingProdukte">Lade Produkte...</p>

              <select v-if="formState.selectedProdukt" v-model="formState.selectedSchaderreger" @change="onSchaderregerSelect(kultur)">
                <option disabled value="">Schaderreger wählen...</option>
                <option v-for="s in formState.schaderreger" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
              <p v-if="formState.loadingSchaderreger">Lade Schaderreger...</p>

              <div class="details-grid" v-if="formState.selectedSchaderreger">
                <div class="form-group">
                  <label>Dosierung</label>
                  <p class="auto-filled-field">{{ formState.dosage_from || '–' }} bis {{ formState.dosage_to || '–' }}</p>
                </div>
                <div class="form-group">
                  <label for="aufwandmenge">Aufwandmenge</label>
                  <div class="input-with-unit">
                    <input type="text" id="aufwandmenge" v-model="formState.aufwandmenge" />
                    <span class="unit">{{ formState.aufwandmenge_einheit }}</span>
                  </div>
                </div>
                <div class="form-group">
                  <label>Wartefrist</label>
                   <p class="auto-filled-field">{{ formState.wartefrist || 'N/A' }}</p>
                </div>
                <div class="form-group-full" v-if="formState.auflagen.length > 0">
                  <label>Auflagen & Bemerkungen</label>
                  <ul class="auflagen-liste">
                    <li v-for="auflage in formState.auflagen" :key="auflage.id">{{ auflage.text }}</li>
                  </ul>
                </div>
              </div>
              
              <button @click="addProductToBehandlung(kulturIndex, behandlungIndex)" :disabled="!formState.selectedSchaderreger" class="add-button">Produkt hinzufügen</button>
            </div>
          </div>
        </div>

        <div class="add-section behandlung-add">
          <input type="text" v-model="formState.behandlungTitel[kultur.meta_id]" placeholder="Titel der Behandlung, z.B. Herbizid im Frühling">
          <button @click="addBehandlung(kulturIndex)" class="add-button-small">+ Behandlung</button>
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

const router = useRouter();
const toast = useToast();
const plan = reactive({ landwirtId: '', jahr: new Date().getFullYear(), kulturen: [] });
const meta = reactive({ landwirte: [], kulturen: [] });
const formState = reactive({
  selectedKulturId: '',
  behandlungTitel: {},
  activeBehandlung: null,
  produkte: [], loadingProdukte: false, selectedProdukt: '',
  schaderreger: [], loadingSchaderreger: false, selectedSchaderreger: '',
  aufwandmenge: '', wartefrist: '',
  aufwandmenge_einheit: '', dosage_from: '', dosage_to: '',
  auflagen: [],
});

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

const addKultur = () => {
  if (!formState.selectedKulturId) return;
  const schonVorhanden = plan.kulturen.some(k => k.meta_id === formState.selectedKulturId);
  if (schonVorhanden) { return toast.warning("Diese Kultur ist bereits im Plan."); }
  const kulturMeta = meta.kulturen.find(k => k.id === formState.selectedKulturId);
  plan.kulturen.push({ meta_id: kulturMeta.id, name: kulturMeta.name, behandlungen: [] });
};

const deleteKultur = (kulturIndex) => { plan.kulturen.splice(kulturIndex, 1); };

const addBehandlung = (kulturIndex) => {
  const kulturMetaId = plan.kulturen[kulturIndex].meta_id;
  const titel = formState.behandlungTitel[kulturMetaId];
  if (!titel) return;
  plan.kulturen[kulturIndex].behandlungen.push({ titel: titel, produkte_im_mix: [] });
  formState.behandlungTitel[kulturMetaId] = '';
};

const deleteBehandlung = (kulturIndex, behandlungIndex) => { plan.kulturen[kulturIndex].behandlungen.splice(behandlungIndex, 1); };

const showAddProductForm = async (kultur, kulturIndex, behandlungIndex) => {
  formState.activeBehandlung = `${kulturIndex}-${behandlungIndex}`;
  formState.selectedProdukt = ''; formState.produkte = []; formState.schaderreger = [];
  formState.selectedSchaderreger = ''; formState.aufwandmenge = ''; formState.wartefrist = '';
  formState.aufwandmenge_einheit = ''; formState.dosage_from = ''; formState.dosage_to = ''; formState.auflagen = [];
  formState.loadingProdukte = true;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/produkte/?kultur=${kultur.meta_id}`);
    formState.produkte = response.data;
  } catch (e) { console.error(e); } finally { formState.loadingProdukte = false; }
};

const onProduktSelect = async (kultur) => {
  if (!formState.selectedProdukt) return;
  formState.loadingSchaderreger = true;
  formState.schaderreger = []; formState.selectedSchaderreger = '';
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/schaderreger/?kultur=${kultur.meta_id}&produkt=${formState.selectedProdukt}`);
    formState.schaderreger = response.data;
  } catch (error) { console.error(error); } finally { formState.loadingSchaderreger = false; }
};

const onSchaderregerSelect = async (kultur) => {
  if (!formState.selectedSchaderreger) return;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/zulassungen/?kultur=${kultur.meta_id}&produkt=${formState.selectedProdukt}&schaderreger=${formState.selectedSchaderreger}`);
    if (response.data.length > 0) {
      const zulassungDetails = response.data[0];
      formState.aufwandmenge = zulassungDetails.aufwandmenge;
      formState.wartefrist = zulassungDetails.wartefrist;
      formState.aufwandmenge_einheit = zulassungDetails.aufwandmenge_einheit;
      formState.dosage_from = zulassungDetails.dosage_from;
      formState.dosage_to = zulassungDetails.dosage_to;
      formState.auflagen = zulassungDetails.auflagen;
    }
  } catch (error) { console.error(error); }
};

const addProductToBehandlung = (kulturIndex, behandlungIndex) => {
  const produkt = formState.produkte.find(p => p.id === formState.selectedProdukt);
  if (!produkt) return;
  plan.kulturen[kulturIndex].behandlungen[behandlungIndex].produkte_im_mix.push({
    produktId: formState.selectedProdukt,
    produktName: produkt.produktname,
    aufwandmenge: `${formState.aufwandmenge} ${formState.aufwandmenge_einheit}`,
    auflagen: formState.auflagen,
  });
  formState.activeBehandlung = null;
};

const deleteProdukt = (kIndex, bIndex, pIndex) => { plan.kulturen[kIndex].behandlungen[bIndex].produkte_im_mix.splice(pIndex, 1); };

const savePlan = async () => {
  if (!plan.landwirtId || !plan.jahr) { return toast.error("Bitte Landwirt und Jahr auswählen."); }
  try {
    await axios.post('http://127.0.0.1:8000/api/plaene/', plan);
    toast.success('Plan erfolgreich erstellt!');
    router.push('/dashboard');
  } catch (error) {
    console.error("Fehler beim Speichern des Plans:", error.response?.data);
    toast.error("Fehler beim Speichern des Plans.");
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
.behandlung-item { padding: 10px; margin-left: 20px; margin-top: 10px; background-color: #fff; border: 1px solid #eee; border-radius: 4px; }
.behandlung-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
.produkt-liste { margin-left: 20px; margin-top: 10px; }
.produkt-liste li { display: flex; justify-content: space-between; font-size: 14px; padding: 4px 0; }
.save-button { width: 100%; padding: 12px; font-size: 18px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }
.add-button, .add-button-small, .button-delete-small, .button-delete-tiny { font-size: 12px; padding: 5px 10px; white-space: nowrap; }
.button-delete-tiny { font-size: 10px; padding: 2px 5px; }
.add-produkt-section { margin-top: 10px; }
.add-produkt-form { display: flex; flex-direction: column; gap: 10px; margin-top: 10px; padding: 15px; background: #f0f0f0; border-radius: 4px; }
.details-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; width: 100%; margin-top: 10px; }
.form-group-full { grid-column: 1 / -1; }
.auflagen-liste { font-size: 12px; max-height: 100px; overflow-y: auto; background: #fff; border: 1px solid #ccc; padding: 5px; margin-top: 5px; }
.input-with-unit { display: flex; align-items: center; }
.input-with-unit input { flex-grow: 1; border-top-right-radius: 0; border-bottom-right-radius: 0; }
.input-with-unit span { padding: 8px; background-color: #e9ecef; border: 1px solid #ccc; border-left: none; border-radius: 0 4px 4px 0; }
.auto-filled-field { background-color: #e9ecef; padding: 8px; border-radius: 4px; border: 1px solid #ccc; min-height: 35px; text-align: left;}
</style>