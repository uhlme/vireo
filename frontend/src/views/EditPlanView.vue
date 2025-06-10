<template>
  <div class="edit-plan" v-if="plan">
    <h1>Plan für {{ plan.landwirt_name }} ({{ plan.jahr }}) bearbeiten</h1>

    <div class="form-block">
      <h2>Stammdaten</h2>
      <div class="form-group">
        <label for="plan-jahr">Jahr</label>
        <input type="number" id="plan-jahr" v-model="plan.jahr">
      </div>
      <div class="form-group">
        <label for="status">Plan-Status</label>
        <select id="status" v-model="plan.status">
          <option value="Entwurf">Entwurf</option>
          <option value="Finalisiert">Finalisiert</option>
        </select>
      </div>
    </div>

    <div class="form-block">
      <h2>Kulturen hinzufügen</h2>
      <div class="add-section">
        <select v-model="formState.selectedKulturId">
          <option disabled value="">Kultur auswählen...</option>
          <option v-for="kultur in meta.kulturen" :key="kultur.id" :value="kultur.id">{{ kultur.name }}</option>
        </select>
        <button @click="addKultur" class="add-button-small">Kultur zum Plan hinzufügen</button>
      </div>
    </div>

    <div class="plan-summary">
      <h2>Bestehende Kulturen & Behandlungen</h2>
      <div v-if="plan.kulturen.length === 0"><p>Diesem Plan wurden noch keine Kulturen hinzugefügt.</p></div>
      
      <div v-for="(kultur, kulturIndex) in plan.kulturen" :key="kultur.meta_id || kultur.id" class="kultur-item">
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
            <li v-for="(p, pIndex) in behandlung.produkte_im_mix" :key="pIndex">
              {{ p.produktName || p.produkt.produktname }} - {{ p.aufwandmenge }}
              <button @click="deleteProdukt(kulturIndex, behandlungIndex, pIndex)" class="button-delete-tiny">x</button>
            </li>
          </ul>

          <div class="add-produkt-section">
            <button v-if="formState.activeBehandlung !== `${kulturIndex}-${behandlungIndex}`" @click="showAddProductForm(kulturIndex, behandlungIndex)" class="add-button-small">+ Produkt zu dieser Behandlung hinzufügen</button>
            <div v-if="formState.activeBehandlung === `${kulturIndex}-${behandlungIndex}`" class="add-produkt-form">
              <select v-model="formState.selectedProdukt" @change="onProduktSelect(kulturIndex)">
                <option disabled value="">Produkt wählen...</option>
                <option v-for="p in formState.produkte" :key="p.id" :value="p.id">{{ p.produktname }}</option>
              </select>
              <select v-if="formState.selectedProdukt" v-model="formState.selectedSchaderreger" @change="onSchaderregerSelect(kulturIndex)">
                <option disabled value="">Schaderreger wählen...</option>
                <option v-for="s in formState.schaderreger" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
              <input v-if="formState.selectedSchaderreger" type="text" v-model="formState.aufwandmenge" placeholder="Aufwandmenge" />
              <button @click="addProductToBehandlung(kulturIndex, behandlungIndex)">OK</button>
            </div>
          </div>
        </div>

        <div class="add-section behandlung-add">
          <input type="text" v-model="formState.behandlungTitel[kultur.id]" placeholder="Titel der neuen Behandlung...">
          <button @click="addBehandlung(kulturIndex)" class="add-button-small">+ Behandlung</button>
        </div>
      </div>
    </div>

    <button @click="saveChanges" class="save-button">Ganzen Plan mit Änderungen speichern</button>

  </div>
  <div v-else><p>Lade Plandaten...</p></div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const plan = ref(null); // Das Haupt-Plan-Objekt, das wir bearbeiten
const meta = reactive({ kulturen: [] }); // Stammdaten für Dropdowns
const formState = reactive({
  selectedKulturId: '',
  behandlungTitel: {},
  activeBehandlung: null,
  produkte: [],
  selectedProdukt: '',
  schaderreger: [],
  selectedSchaderreger: '',
  aufwandmenge: '',
  wartefrist: '',
});

onMounted(async () => {
  const planId = route.params.id;
  try {
    const [planResponse, kulturResponse] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/api/plaene/${planId}/`),
      axios.get('http://127.0.0.1:8000/api/kulturen/'),
    ]);
    plan.value = planResponse.data;
    meta.kulturen = kulturResponse.data;
  } catch (error) { console.error("Fehler beim Laden der Daten:", error); }
});

const addKultur = () => {
  if (!formState.selectedKulturId) return;
  const kulturMeta = meta.kulturen.find(k => k.id === formState.selectedKulturId);
  const schonVorhanden = plan.value.kulturen.some(k => (k.id === kulturMeta.id || k.meta_id === kulturMeta.id));
  if (schonVorhanden) { alert("Diese Kultur ist bereits im Plan."); return; }
  plan.value.kulturen.push({ id: kulturMeta.id, meta_id: kulturMeta.id, name: kulturMeta.name, behandlungen: [] });
};

const deleteKultur = (kulturIndex) => { plan.value.kulturen.splice(kulturIndex, 1); };

const addBehandlung = (kulturIndex) => {
  const kulturId = plan.value.kulturen[kulturIndex].id;
  const titel = formState.behandlungTitel[kulturId];
  if (!titel) return;
  plan.value.kulturen[kulturIndex].behandlungen.push({ titel: titel, produkte_im_mix: [] });
  formState.behandlungTitel[kulturId] = '';
};

const deleteBehandlung = (kulturIndex, behandlungIndex) => { plan.value.kulturen[kulturIndex].behandlungen.splice(behandlungIndex, 1); };

const showAddProductForm = async (kulturIndex, behandlungIndex) => {
  formState.activeBehandlung = `${kulturIndex}-${behandlungIndex}`;
  formState.selectedProdukt = ''; formState.produkte = []; formState.schaderreger = [];
  formState.selectedSchaderreger = ''; formState.aufwandmenge = ''; formState.wartefrist = '';
  try {
    const kulturId = plan.value.kulturen[kulturIndex].id;
    const response = await axios.get(`http://127.0.0.1:8000/api/produkte/?kultur=${kulturId}`);
    formState.produkte = response.data;
  } catch (e) { console.error(e); }
};

const onProduktSelect = async (kulturIndex) => {
  const kulturId = plan.value.kulturen[kulturIndex].id;
  if (!formState.selectedProdukt) return;
  formState.schaderreger = []; formState.selectedSchaderreger = '';
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/schaderreger/?kultur=${kulturId}&produkt=${formState.selectedProdukt}`);
    formState.schaderreger = response.data;
  } catch (error) { console.error(error); }
};

const onSchaderregerSelect = async (kulturIndex) => {
  const kulturId = plan.value.kulturen[kulturIndex].id;
  if (!formState.selectedSchaderreger) return;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/zulassungen/?kultur=${kulturId}&produkt=${formState.selectedProdukt}&schaderreger=${formState.selectedSchaderreger}`);
    if (response.data.length > 0) {
      formState.aufwandmenge = response.data[0].aufwandmenge;
      formState.wartefrist = response.data[0].wartefrist;
    }
  } catch (error) { console.error(error); }
};

const addProductToBehandlung = (kulturIndex, behandlungIndex) => {
  const produkt = formState.produkte.find(p => p.id === formState.selectedProdukt);
  if (!produkt) return;
  plan.value.kulturen[kulturIndex].behandlungen[behandlungIndex].produkte_im_mix.push({
    produktId: formState.selectedProdukt, produktName: produkt.produktname,
    aufwandmenge: formState.aufwandmenge,
  });
  formState.activeBehandlung = null;
};

const deleteProdukt = (kIndex, bIndex, pIndex) => {
  plan.value.kulturen[kIndex].behandlungen[bIndex].produkte_im_mix.splice(pIndex, 1);
};

const saveChanges = async () => {
  const planId = route.params.id;
  try {
    const payload = { ...plan.value };
    await axios.put(`http://127.0.0.1:8000/api/plaene/${planId}/`, payload);
    alert('Änderungen erfolgreich gespeichert!');
    router.push(`/plan/detail/${planId}`);
  } catch (error) { console.error("Fehler beim Speichern der Änderungen:", error.response?.data); }
};
</script>

<style scoped>
/* (Das CSS von CreatePlanView kann hier weitgehend übernommen werden) */
.edit-plan { max-width: 900px; margin: 40px auto; padding: 20px; }
.form-block, .summary-block, .form-container { background-color: #f9f9f9; border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
.add-section { display: flex; gap: 10px; align-items: center; }
.behandlung-add { margin-top: 15px; padding-top: 15px; border-top: 1px dashed #ccc; }
.kultur-item { border: 1px solid #e3e3e3; padding: 15px; margin-top: 15px; border-radius: 5px; }
.kultur-item h3 { display: flex; justify-content: space-between; align-items: center; }
.behandlung-item { padding: 10px; margin-left: 20px; margin-top: 10px; background-color: #fff; border: 1px solid #eee; border-radius: 4px; }
.behandlung-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
.produkt-liste { margin-left: 20px; margin-top: 10px; }
.produkt-liste li { display: flex; justify-content: space-between; font-size: 14px; padding: 4px 0; }
.save-button { width: 100%; padding: 12px; font-size: 18px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }
.add-button-small, .button-delete-small { font-size: 12px; padding: 5px 10px; white-space: nowrap; }
.button-delete-tiny { font-size: 10px; padding: 2px 5px; }
.add-produkt-section { margin-top: 10px; }
.add-produkt-form { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-top: 10px; padding: 10px; background: #f0f0f0; border-radius: 4px; }
</style>