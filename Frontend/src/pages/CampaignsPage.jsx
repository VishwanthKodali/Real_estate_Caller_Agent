import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Plus, Megaphone, Play, Pause } from 'lucide-react'
import toast from 'react-hot-toast'
import { campaignsApi, projectsApi } from '../services/api'

const CAMPAIGN_TYPES = ['launch', 'offer', 'follow_up', 'site_visit']

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState([])
  const [projects, setProjects] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [saving, setSaving] = useState(false)
  const [searchParams] = useSearchParams()
  const [form, setForm] = useState({ project_id: searchParams.get('project') || '', name: '', campaign_type: 'launch', agent_greeting: '', agent_system_prompt: '', voice_id: '' })

  useEffect(() => {
    campaignsApi.list().then(r => setCampaigns(r.data))
    projectsApi.list().then(r => setProjects(r.data))
    if (searchParams.get('project')) setShowForm(true)
  }, [])

  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))

  const submit = async e => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = { ...form, project_id: parseInt(form.project_id) }
      await campaignsApi.create(payload)
      toast.success('Campaign created with ElevenLabs agent!')
      setShowForm(false)
      campaignsApi.list().then(r => setCampaigns(r.data))
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create campaign')
    } finally { setSaving(false) }
  }

  const toggleStatus = async (campaign) => {
    if (campaign.status === 'active') {
      await campaignsApi.pause(campaign.id)
      toast.success('Campaign paused')
    } else {
      await campaignsApi.activate(campaign.id)
      toast.success('Campaign activated')
    }
    campaignsApi.list().then(r => setCampaigns(r.data))
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-gray-500 mt-1">Manage your AI calling campaigns</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus size={18} /> New Campaign
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-lg font-bold">Create Campaign</h2>
              <p className="text-sm text-gray-500 mt-1">An ElevenLabs AI agent will be automatically created for this campaign</p>
            </div>
            <form onSubmit={submit} className="p-6 space-y-4">
              <div>
                <label className="label">Project *</label>
                <select className="input" value={form.project_id} onChange={set('project_id')} required>
                  <option value="">Select project</option>
                  {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Campaign Name *</label>
                <input className="input" value={form.name} onChange={set('name')} required placeholder="e.g. Pre-launch Outreach" />
              </div>
              <div>
                <label className="label">Campaign Type</label>
                <select className="input" value={form.campaign_type} onChange={set('campaign_type')}>
                  {CAMPAIGN_TYPES.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Agent Opening Message (optional)</label>
                <textarea className="input" rows={2} value={form.agent_greeting} onChange={set('agent_greeting')} placeholder="Hello! I'm calling from XYZ Developers about our new project..." />
              </div>
              <div>
                <label className="label">Custom System Prompt (optional — auto-generated if empty)</label>
                <textarea className="input" rows={4} value={form.agent_system_prompt} onChange={set('agent_system_prompt')} placeholder="Leave blank to use the default real estate consultant prompt" />
              </div>
              <div>
                <label className="label">ElevenLabs Voice ID (optional)</label>
                <input className="input" value={form.voice_id} onChange={set('voice_id')} placeholder="e.g. 21m00Tcm4TlvDq8ikWAM (default: Rachel)" />
                <p className="text-xs text-gray-400 mt-1">Find voice IDs in your ElevenLabs dashboard</p>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" disabled={saving} className="btn-primary flex-1">{saving ? 'Creating agent...' : 'Create Campaign'}</button>
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {campaigns.length === 0 ? (
        <div className="text-center py-16">
          <Megaphone size={48} className="text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">No campaigns yet</h3>
          <p className="text-gray-400 mb-6">Create a campaign to start AI-powered calling</p>
          <button onClick={() => setShowForm(true)} className="btn-primary">Create Campaign</button>
        </div>
      ) : (
        <div className="space-y-3">
          {campaigns.map(c => (
            <div key={c.id} className="card flex items-center justify-between hover:shadow-md transition-shadow">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Megaphone size={18} className="text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{c.name}</h3>
                  <p className="text-sm text-gray-400">{c.campaign_type?.replace('_', ' ')} • {c.elevenlabs_agent_id ? `Agent: ${c.elevenlabs_agent_id.slice(0, 12)}...` : 'No agent'}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status={c.status} />
                <button onClick={() => toggleStatus(c)} className="btn-secondary flex items-center gap-1 text-sm py-1.5">
                  {c.status === 'active' ? <><Pause size={14} /> Pause</> : <><Play size={14} /> Activate</>}
                </button>
                <Link to={`/campaigns/${c.id}`} className="btn-primary text-sm py-1.5">Manage</Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function StatusBadge({ status }) {
  const map = { active: 'badge-green', draft: 'badge-gray', paused: 'badge-yellow', completed: 'badge-blue' }
  return <span className={map[status] || 'badge-gray'}>{status}</span>
}
