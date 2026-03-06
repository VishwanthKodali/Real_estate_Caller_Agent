import { create } from 'zustand'
import { authApi } from '../services/api'

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  loading: false,

  login: async (email, password) => {
    set({ loading: true })
    try {
      const { data } = await authApi.login({ email, password })
      localStorage.setItem('token', data.access_token)
      const { data: user } = await authApi.me()
      set({ token: data.access_token, user, loading: false })
      return user
    } finally {
      set({ loading: false })
    }
  },

  register: async (payload) => {
    set({ loading: true })
    try {
      await authApi.register(payload)
      const { data: token } = await authApi.login({ email: payload.email, password: payload.password })
      localStorage.setItem('token', token.access_token)
      const { data: user } = await authApi.me()
      set({ token: token.access_token, user, loading: false })
    } finally {
      set({ loading: false })
    }
  },

  fetchMe: async () => {
    try {
      const { data } = await authApi.me()
      set({ user: data })
    } catch {
      set({ user: null, token: null })
      localStorage.removeItem('token')
    }
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null })
  },

  updateUser: async (payload) => {
    const { data } = await authApi.updateMe(payload)
    set({ user: data })
  }
}))

export default useAuthStore