<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <router-link :to="`/session/${$route.params.id}`" class="text-gray-500 hover:text-gray-700 flex items-center text-sm font-medium">
          <ArrowLeft class="w-4 h-4 mr-1" />
          Back to Session
        </router-link>
        <h1 class="text-lg font-bold">Payment Summary</h1>
        <div class="w-20"></div> <!-- spacer -->
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <!-- Bank Info Card -->
      <div class="bg-indigo-600 rounded-3xl p-8 text-white mb-8 shadow-xl">
        <h3 class="text-indigo-100 text-xs font-bold uppercase tracking-wider mb-2">Transfer to</h3>
        <p class="text-xl font-medium whitespace-pre-wrap">{{ bankInfo }}</p>
      </div>

      <!-- User Breakdowns -->
      <div class="space-y-6">
        <div v-for="user in summaries" :key="user.user_name" class="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="bg-gray-50 px-6 py-4 border-b border-gray-100 flex justify-between items-center">
            <h3 class="font-bold text-gray-900 text-lg">{{ user.user_name }}</h3>
            <span class="text-indigo-600 font-bold text-lg">${{ user.total.toFixed(2) }}</span>
          </div>
          
          <div class="p-6">
            <ul class="space-y-4">
              <li v-for="item in user.items" :key="item.item_id" class="flex flex-col space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-gray-600 capitalize">{{ item.item_name }}</span>
                  <div class="flex items-center space-x-3">
                    <span class="font-medium text-gray-900">${{ item.cost.toFixed(2) }}</span>
                    
                    <!-- Upload/View Proof -->
                    <div v-if="item.payment_file_url">
                      <a :href="item.payment_file_url" target="_blank" class="text-green-600 hover:underline text-xs flex items-center font-bold">
                        <FileCheck class="w-4 h-4 mr-1" />
                        Proof
                      </a>
                    </div>
                    <label v-else class="cursor-pointer text-indigo-600 hover:text-indigo-700">
                      <input type="file" class="hidden" @change="(e) => handlePaymentUpload(e, item.item_id, user.user_name)" />
                      <div class="flex items-center text-xs font-bold border border-indigo-200 px-2 py-1 rounded-lg">
                        <Upload class="w-3 h-3 mr-1" />
                        Paid?
                      </div>
                    </label>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="!summaries.length" class="text-center py-12 text-gray-400">
        No claims yet. Go back and claim some items!
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { sessionApi } from '../api'
import { ArrowLeft, Upload, FileCheck } from 'lucide-vue-next'

const route = useRoute()
const summaries = ref([])
const bankInfo = ref('')

const fetchData = async () => {
  try {
    const [summaryRes, sessionRes] = await Promise.all([
      sessionApi.getSummary(route.params.id),
      sessionApi.getSession(route.params.id)
    ])
    summaries.value = summaryRes.data.user_summaries
    bankInfo.value = sessionRes.data.bank_account_info
  } catch (err) {
    console.error(err)
  }
}

const handlePaymentUpload = async (e, itemId, userName) => {
  const file = e.target.files[0]
  if (!file) return

  try {
    await sessionApi.uploadPayment(route.params.id, itemId, userName, file)
    await fetchData()
  } catch (err) {
    alert('Failed to upload proof of payment')
  }
}

onMounted(fetchData)
</script>
