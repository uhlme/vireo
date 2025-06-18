import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { isAuthenticated } from './auth'

// NEU: Importiere die Toast-Bibliothek und ihr CSS
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

// Der Startup-Check für den Token bleibt bestehen
const token = localStorage.getItem('accessToken');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

// Der Interceptor bleibt ebenfalls bestehen
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('accessToken');
      delete axios.defaults.headers.common['Authorization'];
      isAuthenticated.value = false;
      router.push('/');
    }
    return Promise.reject(error);
  }
);

const app = createApp(App);
app.use(router);

// NEU: Sage der App, dass sie die Toast-Bibliothek mit Standard-Optionen verwenden soll
app.use(Toast, {
  transition: "Vue-Toastification__bounce",
  maxToasts: 5,
  newestOnTop: true
});

app.mount('#app');