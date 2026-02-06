<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-title>Student Management</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="logout" v-if="isAuthenticated">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <!-- Upload Excel -->
        <v-card class="mb-6">
          <v-card-title>
            <v-icon left>mdi-file-excel</v-icon>
            Upload Excel File
          </v-card-title>
          <v-card-text>
            <v-file-input
              v-model="excelFile"
              label="Select Excel file"
              accept=".xlsx"
              prepend-icon="mdi-file-excel"
              @change="onFileChange"
              :loading="uploading"
            />
            <v-btn
              color="success"
              :loading="uploading"
              @click="uploadExcel"
              :disabled="!excelFile"
            >
              Upload Students
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Search & Bulk SMS -->
        <v-row class="mb-6">
          <v-col cols="12" md="6">
            <v-text-field
              v-model="searchQuery"
              label="Search students (Name, Mobile, College)"
              prepend-inner-icon="mdi-magnify"
              clearable
              @input="debouncedSearch"
              hide-details
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-btn
              color="info"
              @click="showBulkSMS = true"
              class="float-right"
            >
              Send Bulk Messages
            </v-btn>
          </v-col>
        </v-row>

        <!-- Students Table -->
        <v-data-table
          :headers="headers"
          :items="students"
          :items-per-page="itemsPerPage"
          :page.sync="page"
          :server-items-length="totalItems"
          :loading="loading"
          class="elevation-1"
          :footer-props="footerProps"
          @update:options="loadStudents"
        >
          <template v-slot:item.actions="{ item }">
            <v-icon small class="mr-2" @click="editItem(item)">mdi-pencil</v-icon>
            <v-icon small @click="deleteItem(item)">mdi-delete</v-icon>
          </template>
        </v-data-table>
      </v-container>
    </v-main>

    <!-- Bulk SMS Dialog -->
    <v-dialog v-model="showBulkSMS" max-width="600">
      <v-card>
        <v-card-title>Send Bulk Telegram Messages</v-card-title>
        <v-card-text>
          <v-select
            v-model="selectedStudents"
            :items="students"
            item-text="mobile"
            item-value="id"
            label="Select Students"
            chips
            multiple
            clearable
          />
          <v-textarea
            v-model="bulkMessage"
            label="Message"
            rows="4"
            clearable
          />
          <v-text-field
            v-model="imageUrl"
            label="Image URL (optional)"
            clearable
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn @click="showBulkSMS = false">Cancel</v-btn>
          <v-btn color="primary" @click="sendBulkSMS">Send</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const students = ref([])
const totalItems = ref(0)
const page = ref(1)
const itemsPerPage = ref(10)
const searchQuery = ref('')
const loading = ref(false)
const uploading = ref(false)
const excelFile = ref(null)
const showBulkSMS = ref(false)
const bulkMessage = ref('')
const imageUrl = ref('')
const selectedStudents = ref([])

const headers = [
  { text: 'Class', value: 'class_name' },
  { text: 'Name', value: 'name' },
  { text: 'Mobile', value: 'mobile' },
  { text: 'College', value: 'college_name' },
  { text: 'Actions', value: 'actions', sortable: false }
]

const footerProps = {
  'items-per-page-text': 'Rows per page:',
  'items-per-page-all-text': 'All'
}

let debounceTimer = null

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
  } else {
    loadStudents()
  }
})

watch(() => authStore.isAuthenticated, (authenticated) => {
  if (!authenticated) {
    router.push('/login')
  }
})

const debouncedSearch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    loadStudents()
  }, 500)
}

const loadStudents = async (options = {}) => {
  try {
    loading.value = true
    const params = {
      page: options.page || page.value,
      limit: options.itemsPerPage || itemsPerPage.value,
      search: searchQuery.value || undefined
    }
    
    const response = await axios.get('/api/students', { params })
    students.value = response.data.students
    totalItems.value = response.data.total
    page.value = response.data.page
  } catch (error) {
    console.error('Failed to load students:', error)
  } finally {
    loading.value = false
  }
}

const uploadExcel = async () => {
  if (!excelFile.value) return
  
  try {
    uploading.value = true
    const formData = new FormData()
    formData.append('file', excelFile.value)
    
    await axios.post('/api/students/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    alert('Students uploaded successfully!')
    excelFile.value = null
    loadStudents()
  } catch (error) {
    alert('Upload failed: ' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

const onFileChange = (file) => {
  excelFile.value = file
}

const sendBulkSMS = async () => {
  try {
    const mobiles = selectedStudents.value.map(id => 
      students.value.find(s => s.id === id)?.mobile
    ).filter(Boolean)
    
    await axios.post('/api/telegram/bulk-send', {
      mobiles,
      message: bulkMessage.value,
      image_url: imageUrl.value || undefined
    })
    
    alert('Messages sent successfully!')
    showBulkSMS.value = false
    bulkMessage.value = ''
    imageUrl.value = ''
    selectedStudents.value = []
  } catch (error) {
    alert('Failed to send messages: ' + (error.response?.data?.detail || error.message))
  }
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
