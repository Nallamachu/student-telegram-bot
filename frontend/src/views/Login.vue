<template>
  <v-container fluid fill-height>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6">
        <v-card class="pa-8">
          <v-card-title class="text-h4 text-center mb-6">
            Student Management
          </v-card-title>
          
          <v-form @submit.prevent="login" ref="form">
            <v-text-field
              v-model="credentials.username"
              label="Username"
              prepend-inner-icon="mdi-account"
              :error-messages="errors.username"
              required
            />
            
            <v-text-field
              v-model="credentials.password"
              label="Password"
              type="password"
              prepend-inner-icon="mdi-lock"
              :error-messages="errors.password"
              required
            />
            
            <v-btn
              color="primary"
              block
              type="submit"
              :loading="loading"
              :disabled="loading"
            >
              Login
            </v-btn>
          </v-form>
          
          <v-divider class="my-4"></v-divider>
          
          <v-btn
            variant="outlined"
            block
            @click="showForgotPassword = true"
            :disabled="loading"
          >
            Forgot Password?
          </v-btn>
          
          <v-alert
            v-if="error"
            type="error"
            class="mt-4"
            closable
            @click:close="error = null"
          >
            {{ error }}
          </v-alert>
        </v-card>
      </v-col>
    </v-row>
    
    <v-dialog v-model="showForgotPassword" max-width="500">
      <v-card>
        <v-card-title>Forgot Password</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="forgotEmail"
            label="Email"
            prepend-inner-icon="mdi-email"
            :error-messages="forgotErrors"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showForgotPassword = false">Cancel</v-btn>
          <v-btn color="primary" @click="sendForgotPassword">Send</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const credentials = reactive({
  username: '',
  password: ''
})

const forgotEmail = ref('')
const showForgotPassword = ref(false)
const loading = computed(() => authStore.loading)
const error = computed(() => authStore.error)

const errors = reactive({
  username: [],
  password: []
})

const forgotErrors = computed(() => {
  const errors = []
  if (!forgotEmail.value) errors.push('Email is required')
  return errors
})

async function login() {
  try {
    await authStore.login(credentials)
    router.push('/dashboard')
  } catch (err) {
    // Error handled by store
  }
}

async function sendForgotPassword() {
  try {
    await axios.post('/api/forgot-password', { email: forgotEmail.value })
    showForgotPassword.value = false
    forgotEmail.value = ''
    alert('Password reset instructions sent!')
  } catch (error) {
    alert(error.response?.data?.detail || 'Failed to send email')
  }
}
</script>
