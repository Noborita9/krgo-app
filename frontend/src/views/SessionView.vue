<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-900 flex items-center">
          <Receipt class="mr-2 text-indigo-600" />
          Receipt Splitter
        </h1>
        <div class="flex space-x-2">
          <button
            @click="copyLink"
            class="p-2 rounded-lg hover:bg-gray-100 text-gray-600 flex items-center text-sm"
          >
            <Share2 class="w-4 h-4 mr-1" />
            Share Link
          </button>
          <router-link
            :to="`/session/${$route.params.id}/summary`"
            class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700"
          >
            View Summary
          </router-link>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <!-- Session Empty State -->
      <div v-if="!items.length" class="text-center bg-white rounded-2xl border-2 border-dashed border-gray-200 p-12">
        <div class="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <Upload class="text-indigo-600" />
        </div>
        <h2 class="text-lg font-semibold mb-2">Upload your receipt</h2>
        <p class="text-gray-500 mb-6 max-w-sm mx-auto">
          Our AI will automatically extract items and prices so everyone can claim their part.
        </p>
        <input
          type="file"
          id="receipt"
          class="hidden"
          @change="handleUpload"
          accept="image/*"
        />
        <label
          for="receipt"
          class="inline-block bg-indigo-600 text-white px-8 py-3 rounded-xl cursor-pointer hover:bg-indigo-700 font-medium transition"
        >
          {{ uploading ? 'Parsing Receipt...' : 'Select Receipt' }}
        </label>
      </div>

      <!-- Items List -->
      <div v-else class="space-y-4">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold">Claim your items</h2>
          <label class="text-indigo-600 text-sm font-semibold cursor-pointer hover:underline">
            <input type="file" class="hidden" @change="handleUpload" accept="image/*" />
            Add another receipt
          </label>
        </div>

        <div v-for="item in items" :key="item.id" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex items-center justify-between hover:border-indigo-200 transition">
          <div class="flex-1">
            <h3 class="font-bold text-gray-900 capitalize">{{ item.name }}</h3>
            <p class="text-indigo-600 font-medium">${{ item.price.toFixed(2) }}</p>
            <!-- Current Claims -->
            <div class="flex flex-wrap gap-1 mt-2">
              <span
                v-for="claim in item.claims"
                :key="claim.id"
                class="bg-indigo-50 text-indigo-700 text-xs px-2 py-1 rounded-full border border-indigo-100"
              >
                {{ claim.user_name }} ({{ (claim.amount_claimed * 100).toFixed(0) }}%)
              </span>
            </div>
          </div>
          
          <button
            @click="openClaimModal(item)"
            class="ml-4 bg-gray-50 hover:bg-indigo-50 hover:text-indigo-600 p-3 rounded-xl transition text-gray-500"
          >
            <Plus class="w-6 h-6" />
          </button>
        </div>
      </div>
    </main>

    <!-- Claim Modal -->
    <div v-if="claimModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white rounded-3xl w-full max-w-sm p-8 shadow-2xl animate-in zoom-in duration-200">
        <h3 class="text-xl font-bold mb-1">Claim {{ selectedItem?.name }}</h3>
        <p class="text-gray-500 mb-6 text-sm">How much of this item is yours?</p>
        
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Your Name</label>
            <input
              v-model="claimName"
              type="text"
              class="w-full bg-gray-50 border-none rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500"
              placeholder="e.g. John"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Ownership ({{ (claimPercent).toFixed(0) }}%)</label>
            <input
              v-model="claimPercent"
              type="range"
              min="0"
              max="100"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <div class="flex justify-between text-[10px] text-gray-400 mt-1 font-bold">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3 mt-8">
          <button
            @click="claimModal = false"
            class="px-4 py-3 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-xl font-bold transition"
          >
            Cancel
          </button>
          <button
            @click="handleClaim"
            :disabled="!claimName || claimPercent == 0"
            class="px-4 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white rounded-xl font-bold transition"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { sessionApi } from '../api'
import { Receipt, Share2, Upload, Plus, Check } from 'lucide-vue-next'

const route = useRoute()
const items = ref([])
const uploading = ref(false)
const claimModal = ref(false)
const selectedItem = ref(null)
const claimName = ref(localStorage.getItem('user_name') || '')
const claimPercent = ref(100)

const fetchSession = async () => {
  try {
    const res = await sessionApi.getSession(route.params.id)
    items.value = res.data.items
  } catch (err) {
    console.error(err)
  }
}

const handleUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  uploading.value = true
  try {
    await sessionApi.uploadReceipt(route.params.id, file)
    await fetchSession()
  } catch (err) {
    alert('Failed to parse receipt')
  } finally {
    uploading.value = false
  }
}

const openClaimModal = (item) => {
  selectedItem.value = item
  claimModal.value = true
  claimPercent.value = 100
}

const handleClaim = async () => {
  localStorage.setItem('user_name', claimName.value)
  try {
    await sessionApi.claimItem(
      route.params.id,
      selectedItem.value.id,
      claimName.value,
      claimPercent.value / 100
    )
    claimModal.value = false
    await fetchSession()
  } catch (err) {
    alert('Failed to claim item')
  }
}

const copyLink = () => {
  navigator.clipboard.writeText(window.location.href)
  alert('Link copied to clipboard!')
}

onMounted(fetchSession)
</script>
