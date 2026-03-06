import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Phone, Star, ChevronDown, ChevronUp, Download } from 'lucide-react'
import { callsApi, campaignsApi, prospectsApi } from '../services/api'

export default function CallLogsPage() {
  const { campaignId } = useParams()
  const [campaign, setCampaign] = useState(null)
  const [calls, setCalls] = useState([])
  const [prospects, setProspects] = useState({})
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState('')
  const [expandedCall, setExpandedCall] = useState(null)
  const [hotProspects, setHotProspects] = useState([])

  useEffect(() => {
    campaignsApi.get(campaignId).then(r => setCampaign(r.data))
    loadLogs()
    callsApi.stats(campaignId).then(r => setStats(r.data))
    callsApi.hotProspects(campaignId).then(r => setHotProspects(r.data))
  }, [campaignId])

  const loadLogs = async () => {
    const r = await callsApi.logs(campaignId)
    setCalls(r.data)
    // Load prospects
    const ids = [...new Set(r.data.map(c => c.prospect_id))]
    const pMap = {}
    await Promise.all(ids.map(pid => 
      prospectsApi.get(campaignId, pid).then(r => { pMap[pid] = r.data }).catch(() => {})
    ))
    setProspects(pMap)
  }

  const filtered = calls.filter(c => {
    if (!filter) return true
    const p = prospects[c.prospect_id]
    return p?.phone?.includes(filter) || p?.name?.toLowerCase().includes(filter.toLowerCase()) || c.outcome?.includes(filter)
  })

  const exportCSV = () => {
    const rows = [['ID','Prospect','Phone','Status','Outcome','Interest','Duration','Date']]
    filtered.forEach(c => {
      const p = prospects[c.prospect_id]
      rows.push([c.id, p?.name || '', p?.phone || '', c.status, c.outcome, c.interest_level || '', c.duration_seconds || '', c.created_at])
    })
    const csv = rows.map(r => r.join(',')).join('\n')
    const a = document.createElement('a'); a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv); a.download = 'call_logs.csv'; a.click()
  }

  return (
    <div className="p-8">
      <div className="flex items-center gap-4 mb-8">
        <Link to={`/campaigns/${campaignId}`} className="text-gray-400 hover:text-gray-600"><ArrowLeft size={20} /></Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">Call Logs</h1>
          <p className="text-gray-500 text-sm">{campaign?.name}</p>
        </div>
        <button onClick={exportCSV} className="btn-secondary flex items-center gap-2">
          <Download size={16} /> Export CSV
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          {[
            { label: 'Total', value: stats.total_calls, cls: 'text-gray-700' },
            { label: 'Completed', value: stats.completed_calls, cls: 'text-blue-600' },
            { label: 'Failed', value: stats.failed_calls, cls: 'text-red-600' },
            { label: 'Interested', value: stats.interested, cls: 'text-green-600' },
            { label: 'Site Visits', value: stats.site_visit_requested, cls: 'text-yellow-600' },
          ].map(s => (
            <div key={s.label} className="card text-center py-3">
              <p className={`text-xl font-bold ${s.cls}`}>{s.value}</p>
              <p className="text-xs text-gray-400">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Hot Prospects */}
      {hotProspects.length > 0 && (
        <div className="card mb-6 border-l-4 border-yellow-400">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-3">
            <Star size={16} className="text-yellow-500" fill="currentColor" /> Hot Prospects ({hotProspects.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
            {hotProspects.map(hp => (
              <div key={hp.call_id} className="flex items-center justify-between bg-yellow-50 p-2 rounded-lg text-sm">
                <div>
                  <p className="font-medium text-gray-800">{hp.prospect.name || hp.prospect.phone}</p>
                  <p className="text-xs text-gray-400">{hp.prospect.phone}</p>
                </div>
                <OutcomeBadge outcome={hp.outcome} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter */}
      <div className="mb-4">
        <input className="input max-w-sm" placeholder="Search by name, phone, outcome..." value={filter} onChange={e => setFilter(e.target.value)} />
      </div>

      {/* Call logs table */}
      <div className="card">
        {filtered.length === 0 ? (
          <div className="text-center py-12">
            <Phone size={40} className="text-gray-300 mx-auto mb-3" />
            <p className="text-gray-400">No calls yet. Start calling from the campaign page.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map(call => {
              const p = prospects[call.prospect_id]
              const expanded = expandedCall === call.id
              return (
                <div key={call.id} className="border border-gray-100 rounded-xl overflow-hidden">
                  <div
                    className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50"
                    onClick={() => setExpandedCall(expanded ? null : call.id)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                        <Phone size={14} className="text-gray-500" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-800">{p?.name || 'Unknown'}</p>
                        <p className="text-xs text-gray-400">{p?.phone} • {call.duration_seconds ? `${Math.floor(call.duration_seconds/60)}m ${call.duration_seconds%60}s` : '—'} • {new Date(call.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {call.interest_level && (
                        <div className="flex">
                          {[1,2,3,4,5].map(n => <Star key={n} size={12} className={n <= call.interest_level ? 'text-yellow-400' : 'text-gray-200'} fill="currentColor" />)}
                        </div>
                      )}
                      <StatusBadge status={call.status} />
                      <OutcomeBadge outcome={call.outcome} />
                      {expanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                    </div>
                  </div>
                  {expanded && (
                    <div className="px-4 pb-4 border-t border-gray-50 bg-gray-50">
                      <p className="text-xs font-semibold text-gray-500 mt-3 mb-2 uppercase tracking-wide">Transcript</p>
                      {call.transcript ? (
                        <pre className="text-xs text-gray-700 whitespace-pre-wrap bg-white p-3 rounded-lg border border-gray-100 max-h-64 overflow-y-auto">{
                          typeof call.transcript === 'string' ? call.transcript : JSON.stringify(JSON.parse(call.transcript), null, 2)
                        }</pre>
                      ) : (
                        <p className="text-xs text-gray-400">No transcript available</p>
                      )}
                      {call.notes && <p className="text-xs text-gray-500 mt-2"><strong>Notes:</strong> {call.notes}</p>}
                      {call.elevenlabs_conversation_id && <p className="text-xs text-gray-400 mt-1">Conversation ID: {call.elevenlabs_conversation_id}</p>}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

function StatusBadge({ status }) {
  const map = { completed: 'badge-green', failed: 'badge-red', in_progress: 'badge-yellow', queued: 'badge-blue', no_answer: 'badge-gray', busy: 'badge-gray' }
  return <span className={map[status] || 'badge-gray'}>{status?.replace('_', ' ')}</span>
}

function OutcomeBadge({ outcome }) {
  if (!outcome || outcome === 'unknown') return null
  const map = { interested: 'badge-blue', site_visit_requested: 'badge-green', not_interested: 'badge-red', callback_requested: 'badge-yellow', no_answer: 'badge-gray' }
  return <span className={map[outcome] || 'badge-gray'}>{outcome?.replace(/_/g, ' ')}</span>
}
