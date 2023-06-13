<template>
  <v-card>
    <v-card-title v-if="isProjectAdmin">
      <div class="title-components-container">
        <action-menu
          @upload="$router.push('dataset/import')"
          @download="$router.push('dataset/export')"
        />
        <default-action-menu
          :text="statusText"
          :items="actionMenuItems"
          @none="queryUpdate('none')"
          @inprogress="queryUpdate('inprogress')"
          @finished="queryUpdate('finished')"
        />
        <dropdown-menu
          title="File Names"
          :content="dropDownItems"
          :clickEvent="dropDownClickEvent"
          :searchEvent="dropDownSearchEvent"
        />
      </div>
      <v-spacer />
      <div class="title-components-container">
        <v-btn
          class="text-capitalize ms-2"
          :disabled="!canDelete"
          outlined
          @click.stop="dialogDelete = true"
        >
          {{ $t('generic.delete') }}
        </v-btn>
        <v-btn
          :disabled="!item.count"
          class="text-capitalize"
          color="error"
          @click="dialogDeleteAll = true"
        >
          {{ $t('generic.deleteAll') }}
        </v-btn>
      </div>
      <v-dialog v-model="dialogDelete">
        <form-delete
          :selected="selected"
          :item-key="itemKey"
          @cancel="dialogDelete = false"
          @remove="remove"
        />
      </v-dialog>
      <v-dialog v-model="dialogDeleteAll">
        <form-delete-bulk @cancel="dialogDeleteAll = false" @remove="removeAll" />
      </v-dialog>
    </v-card-title>
    <image-list
      v-if="project.isImageProject"
      v-model="selected"
      :items="item.items"
      :is-loading="isLoading"
      :total="item.count"
      @update:query="updateQuery"
      @click:labeling="movePage"
    />
    <audio-list
      v-else-if="project.isAudioProject"
      v-model="selected"
      :items="item.items"
      :is-loading="isLoading"
      :total="item.count"
      @update:query="updateQuery"
      @click:labeling="movePage"
    />
    <document-list
      v-else
      v-model="selected"
      :items="item.items"
      :is-loading="isLoading"
      :total="item.count"
      @update:query="updateQuery"
      @click:labeling="movePage"
      @edit="editItem"
    />
  </v-card>
</template>

<script lang="ts">
import _ from 'lodash'
import Vue from 'vue'
import { mdiCheck, mdiClockOutline, mdiClose } from '@mdi/js'
import DocumentList from '@/components/example/DocumentList.vue'
import FormDelete from '@/components/example/FormDelete.vue'
import FormDeleteBulk from '@/components/example/FormDeleteBulk.vue'
import ActionMenu from '~/components/example/ActionMenu.vue'
import DefaultActionMenu from '~/components/utils/ActionMenu.vue'
import DropdownMenu from '~/components/utils/DropDown.vue'
import AudioList from '~/components/example/AudioList.vue'
import ImageList from '~/components/example/ImageList.vue'
import { Project } from '~/domain/models/project/project'
import { getLinkToAnnotationPage } from '~/presenter/linkToAnnotationPage'
import { ExampleDTO, ExampleListDTO } from '~/services/application/example/exampleData'

export default Vue.extend({
  components: {
    ActionMenu,
    AudioList,
    DocumentList,
    ImageList,
    FormDelete,
    FormDeleteBulk,
    DefaultActionMenu,
    DropdownMenu
  },

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  validate({ params, query }) {
    // @ts-ignore
    return /^\d+$/.test(params.id) && /^\d+|$/.test(query.limit) && /^\d+|$/.test(query.offset)
  },

  data() {
    return {
      dialogDelete: false,
      dialogDeleteAll: false,
      project: {} as Project,
      item: {} as ExampleListDTO,
      selected: [] as ExampleDTO[],
      isLoading: false,
      isProjectAdmin: false,
      showIcon: false,
      dropDownItems: [] as { id: number; text: string }[],
      statusText: 'Status: None'
    }
  },

  async fetch() {
    this.isLoading = true
    this.item = await this.$services.example.list(this.projectId, this.$route.query)
    this.isLoading = false
  },

  computed: {
    canDelete(): boolean {
      return this.selected.length > 0
    },

    projectId(): string {
      return this.$route.params.id
    },

    itemKey(): string {
      if (this.project.isImageProject || this.project.isAudioProject) {
        return 'filename'
      } else {
        return 'text'
      }
    },

    actionMenuItems() {
      return [
        {
          title: 'None',
          icon: mdiClose,
          event: 'none'
        },
        {
          title: 'In progress',
          icon: mdiClockOutline,
          event: 'inprogress'
        },
        {
          title: 'Finished',
          icon: mdiCheck,
          event: 'finished'
        }
      ]
    }
  },

  watch: {
    '$route.query': _.debounce(function () {
      // @ts-ignore
      this.$fetch()
    }, 1000)
  },

  async created() {
    this.project = await this.$services.project.findById(this.projectId)
    const member = await this.$repositories.member.fetchMyRole(this.projectId)
    this.isProjectAdmin = member.isProjectAdmin

    // make a request to /metrics/filenames
    const filenames = await this.$repositories.metrics.fetchFilenames(this.projectId)
    console.log(filenames)
    this.dropDownItems = filenames.map((example) => {
      return { id: example.id, text: example.upload_name }
    })
  },

  methods: {
    async remove() {
      await this.$services.example.bulkDelete(this.projectId, this.selected)
      this.$fetch()
      this.dialogDelete = false
      this.selected = []
    },

    async removeAll() {
      await this.$services.example.bulkDelete(this.projectId, [])
      this.$fetch()
      this.dialogDeleteAll = false
      this.selected = []
    },

    updateQuery(query: object) {
      this.$router.push(query)
    },

    movePage(query: object) {
      const link = getLinkToAnnotationPage(this.projectId, this.project.projectType)
      this.updateQuery({
        path: this.localePath(link),
        query
      })
    },

    editItem(item: ExampleDTO) {
      this.$router.push(`dataset/${item.id}/edit`)
    },

    toggleIcon() {
      this.showIcon = !this.showIcon
    },

    queryUpdate(value: string) {
      const query = { ...this.$route.query, status: value }
      this.$router.push({ path: this.$route.path, query })

      if (value === 'inprogress') {
        this.statusText = 'Status: In Progress'
      } else {
        this.statusText = `Status: ${value[0].toUpperCase() + value.slice(1)}`
      }
    },

    dropDownClickEvent(id: string) {
      const query = { ...this.$route.query, id }
      this.$router.push({ path: this.$route.path, query })
    },

    dropDownSearchEvent(newValue: string) {
      console.log(newValue)
    }
  }
})
</script>

<style scoped>
::v-deep .v-dialog {
  width: 800px;
}

.title-components-container {
  display: flex;
  gap: 0.5rem;
}
</style>
