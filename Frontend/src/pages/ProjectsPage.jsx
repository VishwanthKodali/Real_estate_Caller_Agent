import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Building2, MapPin, Calendar, Hash } from 'lucide-react'
import toast from 'react-hot-toast'
import { projectsApi } from '../services/api'

const PROJECT_TYPES = ['apartment', 'villa', 'plot', 'commercial']
const STATUSES = ['upcoming', 'under_construction', 'ready_to_move']

export default function ProjectsPage() {
  const [projects, setProjects] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({ name: '', location: '', project_type: 'apartment', total_units: '', price_range_min: '', price_range_max: '', possession_date: '', rera_id: '', amenities: '', status: 'under_construction', description: '' })

  useEffect(() => { load() }, [])
  const load = () => projectsApi.list().then(r => { setProjects(r.data); setLoading(false) })

  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))

  const submit = async e => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = { ...form, total_units: form.total_units ? parseInt(form.total_units) : null, price_range_min: form.price_range_min ? parseFloat(form.price_range_min) : null, price_range_max: form.price_range_max ? parseFloat(form.price_range_max) : null }
      await projectsApi.create(payload)
      toast.success('Project created!')
      setShowForm(false)
      setForm({ name: '', location: '', project_type: 'apartment', total_units: '', price_range_min: '', price_range_max: '', possession_date: '', rera_id: '', amenities: '', status: 'under_construction', description: '' })
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create project')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-500 mt-1">Manage your real estate projects</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus size={18} /> New Project
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-lg font-bold text-gray-900">Create New Project</h2>
            </div>
            <form onSubmit={submit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="label">Project Name *</label>
                  <input className="input" value={form.name} onChange={set('name')} required placeholder="e.g. Skyline Residencies" />
                </div>
                <div>
                  <label className="label">Location</label>
                  <input className="input" value={form.location} onChange={set('location')} placeholder="e.g. Banjara Hills, Hyderabad" />
                </div>
                <div>
                  <label className="label">Project Type</label>
                  <select className="input" value={form.project_type} onChange={set('project_type')}>
                    {PROJECT_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">Total Units</label>
                  <input className="input" type="number" value={form.total_units} onChange={set('total_units')} />
                </div>
                <div>
                  <label className="label">Status</label>
                  <select className="input" value={form.status} onChange={set('status')}>
                    {STATUSES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">Min Price (₹)</label>
                  <input className="input" type="number" value={form.price_range_min} onChange={set('price_range_min')} placeholder="e.g. 5000000" />
                </div>
                <div>
                  <label className="label">Max Price (₹)</label>
                  <input className="input" type="number" value={form.price_range_max} onChange={set('price_range_max')} />
                </div>
                <div>
                  <label className="label">Possession Date</label>
                  <input className="input" value={form.possession_date} onChange={set('possession_date')} placeholder="e.g. Dec 2026" />
                </div>
                <div>
                  <label className="label">RERA ID</label>
                  <input className="input" value={form.rera_id} onChange={set('rera_id')} />
                </div>
                <div className="col-span-2">
                  <label className="label">Amenities</label>
                  <input className="input" value={form.amenities} onChange={set('amenities')} placeholder="e.g. Swimming Pool, Gym, Clubhouse, 24/7 Security" />
                </div>
                <div className="col-span-2">
                  <label className="label">Description</label>
                  <textarea className="input" rows={3} value={form.description} onChange={set('description')} />
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" disabled={saving} className="btn-primary flex-1">{saving ? 'Creating...' : 'Create Project'}</button>
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-16 text-gray-400">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="text-center py-16">
          <Building2 size={48} className="text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">No projects yet</h3>
          <p className="text-gray-400 mb-6">Create your first real estate project to get started</p>
          <button onClick={() => setShowForm(true)} className="btn-primary">Create Project</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map(p => (
            <Link key={p.id} to={`/projects/${p.id}`} className="card hover:shadow-md transition-shadow group">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Building2 size={20} className="text-blue-600" />
                </div>
                <StatusBadge status={p.status} />
              </div>
              <h3 className="font-bold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">{p.name}</h3>
              <div className="space-y-1 text-sm text-gray-500">
                {p.location && <p className="flex items-center gap-1"><MapPin size={12} /> {p.location}</p>}
                {p.possession_date && <p className="flex items-center gap-1"><Calendar size={12} /> {p.possession_date}</p>}
                {p.rera_id && <p className="flex items-center gap-1"><Hash size={12} /> RERA: {p.rera_id}</p>}
                {(p.price_range_min || p.price_range_max) && (
                  <p className="font-medium text-gray-700">₹{(p.price_range_min/1e5).toFixed(0)}L – ₹{(p.price_range_max/1e5).toFixed(0)}L</p>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

function StatusBadge({ status }) {
  const map = { upcoming: 'badge-yellow', under_construction: 'badge-blue', ready_to_move: 'badge-green' }
  return <span className={map[status] || 'badge-gray'}>{status?.replace(/_/g, ' ')}</span>
}
