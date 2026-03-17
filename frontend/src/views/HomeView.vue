<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 space-y-6">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Receipt Splitter</h1>
        <p class="text-gray-500">Split bills with friends using AI parsing</p>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Bank Information</label>
          <textarea
            v-model="bankInfo"
            placeholder="IBAN, Bank Name, or Account info for friends to pay you"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition h-32"
          ></textarea>
        </div>

        <button
          @click="handleCreate"
          :disabled="loading || !bankInfo"
          class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-semibold py-3 rounded-xl shadow-lg transition transform active:scale-95 flex items-center justify-center"
        >
          <span v-if="loading" class="animate-spin mr-2">⏳</span>
          Create New Session
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'

const bankInfo = ref('')
const loading = ref(false)
const router = useRouter()
const store = useSessionStore()

const handleCreate = async () => {
  loading.value = true
  try {
    const session = await store.createSession(bankInfo.value)
    router.push(`/session/${session.id}`)
  } catch (err) {
    alert('Failed to create session: ' + err.message)
  } finally {
    loading.value = false
  }
}
</script>
