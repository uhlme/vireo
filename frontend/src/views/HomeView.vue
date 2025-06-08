<template>
  <div class="home">
    <LoginComponent />
  </div>
</template>

<script>
// 1. Wir importieren unsere neue Login-Komponente
import LoginComponent from '@/components/LoginComponent.vue'

export default {
  name: 'HomeView',
  // 2. Wir registrieren die Komponente, damit wir sie im Template verwenden können
  components: {
    LoginComponent
  }
}
</script>