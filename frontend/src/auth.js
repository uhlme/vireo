// src/auth.js
import { ref } from 'vue';

// Wir erstellen eine reaktive Variable, die den globalen Login-Status hält.
// Der Startwert wird direkt aus dem localStorage gelesen (!! wandelt den Wert in true/false um).
export const isAuthenticated = ref(!!localStorage.getItem('accessToken'));