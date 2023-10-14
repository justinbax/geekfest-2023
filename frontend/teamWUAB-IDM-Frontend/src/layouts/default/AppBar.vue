<template>
  <v-app-bar flat>
    <v-app-bar-title>
      <v-icon icon="mdi-lock" />

      IDM Permission Management
    </v-app-bar-title>
  </v-app-bar>
  <app-menu></app-menu>
</template>

<script lang="ts" setup>
  import AppMenu from './AppMenu.vue';
</script>
