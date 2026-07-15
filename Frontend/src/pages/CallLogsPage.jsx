import { useEffect, useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Phone, Star, ChevronDown, ChevronUp, Download, Bot, User, Play, Pause, Volume2 } from 'lucide-react'
import { callsApi, campaignsApi, prospectsApi } from '../services/api'

// ── Chat Transcript ───────────────────────────────────────────────────────────
function ChatTranscript({ messages = [], prospectName }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return <p className="text-xs text-gray-400 py-4 text-center">No transcript available</p>
  }

  return (
    <div className="flex flex-col gap-2 max-h-72 overflow-y-auto bg-gray-950 rounded-xl p-3">
      {messages.map((msg, i) => {
        const isAgent = msg.role === 'agent' || msg.role === 'assistant' || msg.role === 'ai'
        const text = msg.message || msg.text || ''
        if (!text) return null
        return (
          <div key={i} className={`flex gap-2 ${isAgent ? 'flex-row' : 'flex-row-reverse'}`}>
            <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${isAgent ? 'bg-indigo-600' : 'bg-emerald-600'}`}>
              {isAgent ? <Bot size={12} className="text-white" /> : <User size={12} className="text-white" />}
            </div>
            <div className={`flex flex-col max-w-[75%] ${isAgent ? 'items-start' : 'items-end'}`}>
              <span className={`text-[10px] font-semibold mb-0.5 ${isAgent ? 'text-indigo-400' : 'text-emerald-400'}`}>
                {isAgent ? 'AI Agent' : (prospectName || 'Prospect')}
                {msg.time_in_call_secs != null && (
                  <span className="text-gray-600 font-normal ml-1">
                    {Math.floor(msg.time_in_call_secs / 60)}:{String(Math.floor(msg.time_in_call_secs % 60)).padStart(2, '0')}
                  </span>
                )}
              </span>
              <div className={`px-3 py-2 rounded-2xl text-xs leading-relaxed ${isAgent ? 'bg-gray-800 text-gray-100 rounded-tl-sm' : 'bg-emerald-900/50 text-emerald-50 rounded-tr-sm'}`}>
                {text}
              </div>
            </div>
          </div>
        )
      })}
      <div ref={bottomRef} />
    </div>
  )
}

export default function CallLogsPage() {
  const { campaignId } = useParams()
  const [campaign, setCampaign] = useState(null)
  const [calls, setCalls] = useState([])
  const [prospects, setProspects] = useState({})
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState('')
  const [expandedCall, setExpandedCall] = useState(null)
  const [hotProspects, setHotProspects] = useState([])
  const [chatData, setChatData] = useState({})       // { [call_id]: { messages, loading, error } }
  const [audioState, setAudioState] = useState({})   // { [call_id]: { playing, loading, error } }
  const audioRefs = useRef({})                        // { [call_id]: HTMLAudioElement }

  useEffect(() => {
    campaignsApi.get(campaignId).then(r => setCampaign(r.data))
    loadLogs()
    callsApi.hotProspects(campaignId).then(r => setHotProspects(r.data))

    // Refresh all outcomes first, then load stats so numbers are accurate
    callsApi.refreshOutcomes(campaignId)
      .catch(() => {}) // silent fail
      .finally(() => {
        callsApi.stats(campaignId).then(r => setStats(r.data))
      })
  }, [campaignId])

  const handleExpand = async (call) => {
    const isExpanding = expandedCall !== call.id
    setExpandedCall(isExpanding ? call.id : null)

    if (isExpanding && !chatData[call.id] && call.elevenlabs_conversation_id) {
      setChatData(prev => ({ ...prev, [call.id]: { messages: [], loading: true, error: null } }))
      try {
        const r = await callsApi.chat(call.elevenlabs_conversation_id)
        setChatData(prev => ({ ...prev, [call.id]: { messages: r.data.messages || [], loading: false, error: null } }))
        // ── Refresh stats so updated outcome/conversion shows immediately ──
        callsApi.stats(campaignId).then(r => setStats(r.data))
        callsApi.hotProspects(campaignId).then(r => setHotProspects(r.data))
      } catch (e) {
        setChatData(prev => ({ ...prev, [call.id]: { messages: [], loading: false, error: 'Could not load transcript' } }))
      }
    }
  }

  const handlePlayAudio = (call) => {
    if (!call.elevenlabs_conversation_id) return
    const callId = call.id

    // If already playing, pause it
    const existing = audioRefs.current[callId]
    if (existing) {
      if (!existing.paused) {
        existing.pause()
        setAudioState(prev => ({ ...prev, [callId]: { ...prev[callId], playing: false } }))
      } else {
        existing.play()
        setAudioState(prev => ({ ...prev, [callId]: { ...prev[callId], playing: true } }))
      }
      return
    }

    // First time — build URL with auth token and create audio element
    const token = localStorage.getItem('token')
    setAudioState(prev => ({ ...prev, [callId]: { playing: false, loading: true, error: null } }))

    // Fetch audio as blob (need auth header)
    fetch(`/api/v1/calls/audio/${call.elevenlabs_conversation_id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error(`Audio fetch failed: ${res.status}`)
        return res.blob()
      })
      .then(blob => {
        const url = URL.createObjectURL(blob)
        const audio = new Audio(url)
        audioRefs.current[callId] = audio

        audio.onended = () => setAudioState(prev => ({ ...prev, [callId]: { ...prev[callId], playing: false } }))
        audio.onerror = () => setAudioState(prev => ({ ...prev, [callId]: { playing: false, loading: false, error: 'Playback failed' } }))

        audio.play()
        setAudioState(prev => ({ ...prev, [callId]: { playing: true, loading: false, error: null } }))
      })
      .catch(e => {
        setAudioState(prev => ({ ...prev, [callId]: { playing: false, loading: false, error: 'Audio not available' } }))
      })
  }


  const loadLogs = async () => {
    const r = await callsApi.logs(campaignId)
    setCalls(r.data)
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
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 mb-8">
          {[
            { label: 'Total Calls',    value: stats.total_calls,                cls: 'text-gray-700' },
            { label: 'Completed',      value: stats.completed_calls,            cls: 'text-blue-600' },
            { label: 'Failed',         value: stats.failed_calls,               cls: 'text-red-500' },
            { label: 'Answered',       value: stats.answered ?? 0,              cls: 'text-cyan-600' },
            { label: 'Not Answered',   value: stats.not_answered ?? 0,          cls: 'text-orange-500' },
            { label: 'Interested',     value: stats.interested,                 cls: 'text-green-600' },
            { label: 'Site Visits',    value: stats.site_visit_requested,       cls: 'text-yellow-600' },
            { label: 'Conversion',     value: `${stats.conversion_rate ?? 0}%`, cls: 'text-purple-600' },
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

      {/* Call logs */}
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
              const chat = chatData[call.id]
              const msgCount = chat?.messages?.length || 0

              return (
                <div key={call.id} className="border border-gray-100 rounded-xl overflow-hidden">
                  <div
                    className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50"
                    onClick={() => handleExpand(call)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                        <Phone size={14} className="text-gray-500" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-800">{p?.name || 'Unknown'}</p>
                        <p className="text-xs text-gray-400">
                          {p?.phone} • {call.duration_seconds ? `${Math.floor(call.duration_seconds/60)}m ${call.duration_seconds%60}s` : '—'} • {new Date(call.created_at).toLocaleString()}
                          {msgCount > 0 && <span className="ml-2 text-indigo-400">{msgCount} messages</span>}
                        </p>
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
                      {/* Chat header with Play button */}
                      <div className="flex items-center justify-between mt-3 mb-2">
                        <div className="flex items-center gap-4">
                          <div className="flex items-center gap-1.5">
                            <div className="w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center"><Bot size={11} className="text-white" /></div>
                            <span className="text-xs font-semibold text-indigo-600">AI Agent</span>
                          </div>
                          <span className="text-gray-300 text-xs">↔</span>
                          <div className="flex items-center gap-1.5">
                            <div className="w-5 h-5 rounded-full bg-emerald-600 flex items-center justify-center"><User size={11} className="text-white" /></div>
                            <span className="text-xs font-semibold text-emerald-600">{p?.name || 'Prospect'}</span>
                          </div>
                        </div>

                        {/* Audio play button */}
                        {call.elevenlabs_conversation_id && (
                          <div className="flex items-center gap-2">
                            {audioState[call.id]?.error && (
                              <span className="text-xs text-red-400">{audioState[call.id].error}</span>
                            )}
                            <button
                              onClick={e => { e.stopPropagation(); handlePlayAudio(call) }}
                              disabled={audioState[call.id]?.loading}
                              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                                audioState[call.id]?.playing
                                  ? 'bg-indigo-600 text-white'
                                  : 'bg-white border border-gray-200 text-gray-600 hover:border-indigo-300 hover:text-indigo-600'
                              } ${audioState[call.id]?.loading ? 'opacity-60 cursor-not-allowed' : ''}`}
                            >
                              {audioState[call.id]?.loading ? (
                                <><Volume2 size={12} className="animate-pulse" /> Loading...</>
                              ) : audioState[call.id]?.playing ? (
                                <><Pause size={12} /> Pause</>
                              ) : (
                                <><Play size={12} /> Play Recording</>
                              )}
                            </button>
                          </div>
                        )}
                      </div>

                      {/* Chat messages */}
                      {!call.elevenlabs_conversation_id ? (
                        <p className="text-xs text-gray-400 text-center py-4">No conversation recorded</p>
                      ) : chat?.loading ? (
                        <p className="text-xs text-gray-400 text-center py-4 animate-pulse">Loading transcript...</p>
                      ) : chat?.error ? (
                        <p className="text-xs text-red-400 text-center py-4">{chat.error}</p>
                      ) : (
                        <ChatTranscript messages={chat?.messages || []} prospectName={p?.name} />
                      )}

                      {call.notes && <p className="text-xs text-gray-500 mt-2"><strong>Notes:</strong> {call.notes}</p>}
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