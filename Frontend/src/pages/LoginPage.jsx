import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Phone } from 'lucide-react'
import toast from 'react-hot-toast'
import useAuthStore from '../store/authStore'

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const submit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(form.email, form.password)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-blue-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Phone size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">PropCaller</h1>
          <p className="text-gray-400 mt-1">AI Real Estate Caller Platform</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Sign in to your account</h2>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">Email address</label>
              <input className="input" type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
            </div>
            <div>
              <label className="label">Password</label>
              <input className="input" type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} required />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full py-3 text-base">
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
          <p className="text-center text-sm text-gray-600 mt-4">
            Don't have an account? <Link to="/register" className="text-blue-600 font-medium hover:underline">Register</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
