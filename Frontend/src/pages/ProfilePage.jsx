import { useState } from 'react'
import { User, Building2, Save } from 'lucide-react'
import toast from 'react-hot-toast'
import useAuthStore from '../store/authStore'

export default function ProfilePage() {
  const { user, updateUser } = useAuthStore()
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    company_name: user?.company_name || '',
    phone: user?.phone || '',
    rera_number: user?.rera_number || '',
    office_address: user?.office_address || '',
    website: user?.website || '',
  })
  const [saving, setSaving] = useState(false)
  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))

  const submit = async e => {
    e.preventDefault()
    setSaving(true)
    try {
      await updateUser(form)
      toast.success('Profile updated!')
    } catch { toast.error('Failed to update') }
    finally { setSaving(false) }
  }

  return (
    <div className="p-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Developer Profile</h1>
        <p className="text-gray-500 mt-1">This info is used by the AI agent during calls</p>
      </div>

      <div className="card">
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-100">
          <div className="w-16 h-16 bg-blue-500 rounded-2xl flex items-center justify-center text-white text-2xl font-bold">
            {user?.full_name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <p className="text-lg font-bold text-gray-900">{user?.full_name}</p>
            <p className="text-gray-500">{user?.email}</p>
          </div>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Full Name</label>
              <input className="input" value={form.full_name} onChange={set('full_name')} />
            </div>
            <div>
              <label className="label">Company / Developer Name</label>
              <input className="input" value={form.company_name} onChange={set('company_name')} />
            </div>
            <div>
              <label className="label">Phone</label>
              <input className="input" value={form.phone} onChange={set('phone')} />
            </div>
            <div>
              <label className="label">RERA Number</label>
              <input className="input" value={form.rera_number} onChange={set('rera_number')} placeholder="Your RERA registration" />
            </div>
            <div className="col-span-2">
              <label className="label">Office Address</label>
              <input className="input" value={form.office_address} onChange={set('office_address')} />
            </div>
            <div className="col-span-2">
              <label className="label">Website</label>
              <input className="input" type="url" value={form.website} onChange={set('website')} placeholder="https://" />
            </div>
          </div>
          <button type="submit" disabled={saving} className="btn-primary flex items-center gap-2">
            <Save size={16} /> {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </form>
      </div>

      <div className="card mt-6">
        <h3 className="font-semibold text-gray-900 mb-2">How your profile is used</h3>
        <ul className="text-sm text-gray-500 space-y-1">
          <li>• <strong>Company Name</strong> — spoken by the AI agent when introducing itself</li>
          <li>• <strong>RERA Number</strong> — shared with prospects for credibility</li>
          <li>• <strong>Office Address</strong> — provided for site visit scheduling</li>
          <li>• All info is injected into the AI agent's system prompt automatically</li>
        </ul>
      </div>
    </div>
  )
}
