import { useEffect, useState, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { ArrowLeft, Phone, Upload, Plus, Trash2, Play, Pause, PhoneCall, Star, Users } from 'lucide-react'
import toast from 'react-hot-toast'
import { campaignsApi, prospectsApi, callsApi } from '../services/api'

export default function CampaignDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [campaign, setCampaign] = useState(null)
  const [prospects, setProspects] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [calling, setCalling] = useState(false)
  const [showAddProspect, setShowAddProspect] = useState(false)
  const [csvUploading, setCsvUploading] = useState(false)
  const [prospectForm, setProspectForm] = useState({ name: '', phone: '', email: '', budget_min: '', budget_max: '', preferred_unit_type: '', source: '' })
  const [savingProspect, setSavingProspect] = useState(false)

  useEffect(() => { loadAll() }, [id])

  const loadAll = async () => {
    try {
      const [c, p, s] = await Promise.all([campaignsApi.get(id), prospectsApi.list(id), callsApi.stats(id)])
      setCampaign(c.data); setProspects(p.data); setStats(s.data)
    } catch { navigate('/campaigns') }
    finally { setLoading(false) }
  }

  const startCalls = async () => {
    setCalling(true)
    try {
      const r = await callsApi.startCampaign(id)
      toast.success(r.data.message)
      setTimeout(loadAll, 2000)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to start calls')
    } finally { setCalling(false) }
  }

  const callOne = async prospectId => {
    try {
      await callsApi.callProspect(id, prospectId)
      toast.success('Call initiated!')
      setTimeout(loadAll, 2000)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Call failed')
    }
  }

  const addProspect = async e => {
    e.preventDefault()
    setSavingProspect(true)
    try {
      const payload = { ...prospectForm, budget_min: prospectForm.budget_min ? parseFloat(prospectForm.budget_min) : null, budget_max: prospectForm.budget_max ? parseFloat(prospectForm.budget_max) : null }
      await prospectsApi.create(id, payload)
      toast.success('Prospect added!')
      setShowAddProspect(false)
      setProspectForm({ name: '', phone: '', email: '', budget_min: '', budget_max: '', preferred_unit_type: '', source: '' })
      prospectsApi.list(id).then(r => setProspects(r.data))
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add prospect')
    } finally { setSavingProspect(false) }
  }

  const onCsvDrop = useCallback(async files => {
    if (!files[0]) return
    setCsvUploading(true)
    try {
      const r = await prospectsApi.bulkUpload(id, files[0])
      toast.success(`Added ${r.data.added} prospects (${r.data.skipped_duplicates} duplicates skipped)`)
      prospectsApi.list(id).then(r => setProspects(r.data))
    } catch { toast.error('CSV upload failed') }
    finally { setCsvUploading(false) }
  }, [id])

  const { getRootProps: csvProps, getInputProps: csvInput } = useDropzone({ onDrop: onCsvDrop, accept: { 'text/csv': ['.csv'] }, multiple: false })

  const deleteProspect = async pId => {
    await prospectsApi.delete(id, pId)
    setProspects(p => p.filter(x => x.id !== pId))
    toast.success('Prospect removed')
  }

  const set = k => e => setProspectForm(f => ({...f, [k]: e.target.value}))

  if (loading) return <div className="p-8 text-gray-400">Loading...</div>
  if (!campaign) return null

  return (
    <div className="p-8">
      <div className="flex items-center gap-4 mb-8">
        <Link to="/campaigns" className="text-gray-400 hover:text-gray-600"><ArrowLeft size={20} /></Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{campaign.name}</h1>
          <p className="text-gray-500 text-sm">{campaign.campaign_type?.replace('_', ' ')} • {campaign.status}</p>
        </div>
        <Link to={`/calls/${id}`} className="btn-secondary flex items-center gap-2">
          <Phone size={16} /> Call Logs
        </Link>
        <button onClick={startCalls} disabled={calling} className="btn-primary flex items-center gap-2">
          <Play size={16} /> {calling ? 'Starting...' : 'Start Calling'}
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatMini label="Total Prospects" value={stats.total_prospects} color="blue" />
          <StatMini label="Calls Made" value={stats.total_calls} color="gray" />
          <StatMini label="Interested" value={stats.interested} color="green" />
          <StatMini label="Site Visits" value={stats.site_visit_requested} color="yellow" icon={<Star size={12} className="text-yellow-500" />} />
        </div>
      )}

      {/* Agent Info */}
      {campaign.elevenlabs_agent_id && (
        <div className="card mb-6 border-l-4 border-blue-500">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <p className="text-sm font-semibold text-gray-800">ElevenLabs AI Agent Active</p>
          </div>
          <p className="text-xs text-gray-400">Agent ID: {campaign.elevenlabs_agent_id}</p>
          {campaign.agent_greeting && <p className="text-sm text-gray-600 mt-2 italic">"{campaign.agent_greeting}"</p>}
        </div>
      )}

      {/* Prospects */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2"><Users size={18} /> Prospects ({prospects.length})</h3>
          <div className="flex gap-2">
            <div {...csvProps()} className="btn-secondary text-sm cursor-pointer flex items-center gap-1">
              <input {...csvInput()} />
              <Upload size={14} /> {csvUploading ? 'Uploading...' : 'CSV Upload'}
            </div>
            <button onClick={() => setShowAddProspect(true)} className="btn-primary text-sm flex items-center gap-1">
              <Plus size={14} /> Add Prospect
            </button>
          </div>
        </div>

        <p className="text-xs text-gray-400 mb-3">CSV format: name, phone, email, budget_min, budget_max, preferred_unit_type, preferred_location, source, notes</p>

        {showAddProspect && (
          <form onSubmit={addProspect} className="bg-gray-50 p-4 rounded-xl mb-4 grid grid-cols-2 gap-3">
            <div><label className="label text-xs">Name</label><input className="input text-sm" value={prospectForm.name} onChange={set('name')} /></div>
            <div><label className="label text-xs">Phone *</label><input className="input text-sm" value={prospectForm.phone} onChange={set('phone')} required placeholder="+91XXXXXXXXXX" /></div>
            <div><label className="label text-xs">Email</label><input className="input text-sm" value={prospectForm.email} onChange={set('email')} /></div>
            <div><label className="label text-xs">Unit Type</label><input className="input text-sm" value={prospectForm.preferred_unit_type} onChange={set('preferred_unit_type')} placeholder="2BHK, 3BHK..." /></div>
            <div><label className="label text-xs">Budget Min (₹)</label><input className="input text-sm" type="number" value={prospectForm.budget_min} onChange={set('budget_min')} /></div>
            <div><label className="label text-xs">Budget Max (₹)</label><input className="input text-sm" type="number" value={prospectForm.budget_max} onChange={set('budget_max')} /></div>
            <div><label className="label text-xs">Source</label><input className="input text-sm" value={prospectForm.source} onChange={set('source')} placeholder="website, walk-in, referral" /></div>
            <div className="flex items-end gap-2">
              <button type="submit" disabled={savingProspect} className="btn-primary text-sm flex-1">{savingProspect ? 'Adding...' : 'Add'}</button>
              <button type="button" onClick={() => setShowAddProspect(false)} className="btn-secondary text-sm flex-1">Cancel</button>
            </div>
          </form>
        )}

        <div className="space-y-2">
          {prospects.length === 0 && <p className="text-center text-gray-400 py-8 text-sm">No prospects yet. Add individually or upload CSV.</p>}
          {prospects.map(p => (
            <div key={p.id} className="flex items-center justify-between py-2 px-3 hover:bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-800">{p.name || 'Unknown'}</p>
                <p className="text-xs text-gray-400">{p.phone} {p.email && `• ${p.email}`} {p.preferred_unit_type && `• ${p.preferred_unit_type}`}</p>
              </div>
              <div className="flex items-center gap-2">
                <ProspectBadge status={p.status} />
                <button onClick={() => callOne(p.id)} className="p-1 text-gray-400 hover:text-green-600" title="Call now"><PhoneCall size={15} /></button>
                <button onClick={() => deleteProspect(p.id)} className="p-1 text-gray-400 hover:text-red-500"><Trash2 size={14} /></button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatMini({ label, value, color, icon }) {
  const colors = { blue: 'text-blue-600 bg-blue-50', green: 'text-green-600 bg-green-50', yellow: 'text-yellow-600 bg-yellow-50', gray: 'text-gray-600 bg-gray-50' }
  return (
    <div className="card text-center py-4">
      <p className={`text-2xl font-bold ${colors[color]?.split(' ')[0]}`}>{value ?? 0}</p>
      <p className="text-xs text-gray-500 mt-1 flex items-center justify-center gap-1">{icon}{label}</p>
    </div>
  )
}

function ProspectBadge({ status }) {
  const map = { new: 'badge-gray', contacted: 'badge-blue', interested: 'badge-green', not_interested: 'badge-red', site_visit_scheduled: 'badge-yellow', converted: 'badge-green' }
  return <span className={map[status] || 'badge-gray'}>{status?.replace(/_/g, ' ')}</span>
}
