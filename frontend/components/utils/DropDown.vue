<template>
  <v-menu offset-y open-on-hover>
    <template #activator="{ on }">
      <v-btn color="primary text-capitalize" v-on="on">
        {{ title }}
        <v-icon>{{ mdiMenuDown }}</v-icon>
      </v-btn>
    </template>
    <v-card class="dropdown">
      <v-list>
        <v-list-item v-for="(text, index) in content" :key="index">
          <v-list-item-content>
            <v-list-item-title>{{ text }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiMenuDown } from '@mdi/js'

export default Vue.extend({
  name: 'Dropdown',

  props: {
    title: {
      type: String,
      default: 'Actions'
    },
    content: {
      type: Array,
      default: () => [],
      required: true
    }
  },

  data() {
    return {
      mdiMenuDown
    }
  }
})
</script>

<style>
.dropdown {
  max-height: 300px;
  overflow-y: auto;
}
</style>
