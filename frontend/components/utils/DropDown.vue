<template>
  <v-menu offset-y open-on-hover open-on-click>
    <template #activator="{ on }">
      <v-btn color="primary text-capitalize" v-on="on">
        {{ title }}
        <v-icon>{{ mdiMenuDown }}</v-icon>
      </v-btn>
    </template>
    <v-card class="dropdown">
      <template>
        <v-text-field
          v-model="filenameSearch"
          :prepend-inner-icon="mdiMagnify"
          :label="$t('generic.search')"
          single-line
          hide-details
          filled
          @click.stop
        />
      </template>
      <v-list>
        <v-list-item key="0" @click="handleItemClick(0)">
          <v-list-item-content>
            <v-list-item-title>None</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-for="item in content" :key="item.id" @click="handleItemClick(item.id)">
          <v-list-item-content>
            <v-list-item-title>{{ item.text }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script lang="ts">
import Vue from 'vue'
import { mdiMenuDown, mdiMagnify } from '@mdi/js'

export default Vue.extend({
  name: 'Dropdown',

  props: {
    title: {
      type: String,
      default: 'Dropdown'
    },
    content: {
      type: Array,
      default: () => [],
      required: true
    },
    clickEvent: {
      type: Function,
      required: true
    },
    searchEvent: {
      type: Function,
      required: true
    }
  },

  data() {
    return {
      filenameSearch: '',
      searchTimer: null as ReturnType<typeof setTimeout> | null,
      mdiMenuDown,
      mdiMagnify
    }
  },

  methods: {
    handleItemClick(key: number) {
      this.clickEvent('' + key)
    },

    makeServerRequest() {
      this.searchEvent(this.filenameSearch)
    }
  },

  watch: {
    filenameSearch() {
      clearTimeout(this.searchTimer!)

      this.searchTimer = setTimeout(() => {
        this.makeServerRequest()
      }, 500)
    }
  }
})
</script>

<style>
.dropdown {
  max-height: 300px;
  width: 800px;
  overflow-y: auto;
}
</style>
