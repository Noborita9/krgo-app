import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const sessionApi = {
  createSession: (bankInfo) => api.post('/sessions/', { bank_account_info: bankInfo }),
  getSession: (id) => api.get(`/sessions/${id}`),
  uploadReceipt: (id, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/sessions/${id}/receipt`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  claimItem: (sessionId, itemId, userName, amountClaimed) => 
    api.post(`/sessions/${sessionId}/items/${itemId}/claim`, { 
      user_name: userName, 
      amount_claimed: amountClaimed 
    }),
  uploadPayment: (sessionId, itemId, userName, file) => {
    const formData = new FormData()
    formData.append('user_name', userName)
    formData.append('file', file)
    return api.post(`/sessions/${sessionId}/items/${itemId}/pay`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getSummary: (id) => api.get(`/sessions/${id}/summary`),
}

export default api
