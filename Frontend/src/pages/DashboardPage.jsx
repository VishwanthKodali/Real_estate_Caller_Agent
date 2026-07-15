import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Building2, Megaphone, Users, Phone, TrendingUp, Star, ArrowRight } from 'lucide-react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { dashboardApi } from '../services/api'
import useAuthStore from '../store/authStore'

const COLORS = ['#22c55e', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6']

function StatCard({ icon: Icon, label, value, color = 'blue', sub }) {
  const colors = { blue: 'bg-blue-50 text-blue-600', green: 'bg-green-50 text-green-600', yellow: 'bg-yellow-50 text-yellow-600', purple: 'bg-purple-50 text-purple-600' }
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors[color]}`}>
        <Icon size={22} />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState(null)

  useEffect(() => {
    dashboardApi.stats().then(r => setData(r.data)).catch(() => {})
  }, [])

  const overview = data?.overview || {}
  const activity = data?.recent_activity || []

  const outcomeData = [
    { name: 'Site Visit', value: overview.site_visits_requested || 0 },
    { name: 'Interested', value: overview.interested_prospects || 0 },
    { name: 'Completed', value: Math.max(0, (overview.completed_calls || 0) - (overview.site_visits_requested || 0) - (overview.interested_prospects || 0)) },
    { name: 'Failed', value: overview.total_calls - overview.completed_calls || 0 },
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Good morning, {user?.full_name?.split(' ')[0]}! 👋</h1>
        <p className="text-gray-500 mt-1">{user?.company_name} • Here's your calling overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard icon={Building2} label="Total Projects" value={overview.total_projects ?? '—'} color="blue" />
        <StatCard icon={Megaphone} label="Active Campaigns" value={overview.active_campaigns ?? '—'} color="green" sub={`of ${overview.total_campaigns ?? 0} total`} />
        <StatCard icon={Users} label="Total Prospects" value={overview.total_prospects ?? '—'} color="purple" />
        <StatCard icon={Phone} label="Calls Made" value={overview.total_calls ?? '—'} color="yellow" sub={`${overview.conversion_rate ?? 0}% site visit rate`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Call Outcomes</h3>
          {overview.total_calls > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={outcomeData} cx="50%" cy="50%" outerRadius={70} dataKey="value" label={({name, value}) => value > 0 ? `${name}: ${value}` : ''}>
                  {outcomeData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-gray-400 text-sm">
              No calls made yet. Start a campaign to see data here.
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">Hot Prospects 🔥</h3>
            <span className="badge-green">{overview.site_visits_requested || 0} site visits</span>
          </div>
          <div className="space-y-2">
            {overview.site_visits_requested > 0 || overview.interested_prospects > 0 ? (
              <>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Star size={14} className="text-yellow-500" fill="currentColor" />
                    <span className="text-sm font-medium text-gray-700">Site Visit Requested</span>
                  </div>
                  <span className="font-bold text-green-700">{overview.site_visits_requested}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Interested Prospects</span>
                  <span className="font-bold text-blue-700">{overview.interested_prospects}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Conversion Rate</span>
                  <span className="font-bold text-gray-700">{overview.conversion_rate}%</span>
                </div>
              </>
            ) : (
              <p className="text-gray-400 text-sm text-center py-8">Start calling to see hot prospects here.</p>
            )}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Recent Activity</h3>
        </div>
        {activity.length > 0 ? (
          <div className="space-y-2">
            {activity.map(item => (
              <div key={item.call_id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-800">{item.prospect_name || item.prospect_phone}</p>
                  <p className="text-xs text-gray-400">{item.campaign_name}</p>
                </div>
                <div className="flex items-center gap-2">
                  <OutcomeBadge outcome={item.outcome} />
                  <StatusBadge status={item.status} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Phone size={32} className="text-gray-300 mx-auto mb-2" />
            <p className="text-gray-400 text-sm">No calls yet. <Link to="/projects" className="text-blue-600 hover:underline">Create a project</Link> to get started.</p>
          </div>
        )}
      </div>
    </div>
  )
}

function StatusBadge({ status }) {
  const map = { completed: 'badge-green', failed: 'badge-red', in_progress: 'badge-yellow', queued: 'badge-blue' }
  return <span className={map[status] || 'badge-gray'}>{status?.replace('_', ' ')}</span>
}

function OutcomeBadge({ outcome }) {
  if (!outcome || outcome === 'unknown') return null
  const map = { interested: 'badge-blue', site_visit_requested: 'badge-green', not_interested: 'badge-red', callback_requested: 'badge-yellow' }
  return <span className={map[outcome] || 'badge-gray'}>{outcome?.replace(/_/g, ' ')}</span>
}
