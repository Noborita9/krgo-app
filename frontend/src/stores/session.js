import { defineStore } from 'pinia'
import { sessionApi } from '../api'

export const useSessionStore = defineStore('session', {
  state: () => ({
    currentSession: null,
    loading: false,
    error: null,
  }),
  actions: {
    async createSession(bankInfo) {
      this.loading = true
      try {
        const res = await sessionApi.createSession(bankInfo)
        this.currentSession = res.data
        return res.data
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    async fetchSession(id) {
      this.loading = true
      try {
        const res = await sessionApi.getSession(id)
        this.currentSession = res.data
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})
