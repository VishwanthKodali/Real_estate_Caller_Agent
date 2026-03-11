import { useEffect, useState, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { ArrowLeft, Upload, FileText, Trash2, RefreshCw, Megaphone, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { projectsApi, documentsApi, campaignsApi } from '../services/api'

const DOC_TYPES = ['brochure', 'floor_plan', 'price_list', 'amenity_details', 'location_map', 'payment_plan', 'other']

export default function ProjectDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [docs, setDocs] = useState([])
  const [campaigns, setCampaigns] = useState([])
  const [uploading, setUploading] = useState(false)
  const [docType, setDocType] = useState('brochure')
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadAll() }, [id])

  // Poll every 3 seconds while any doc is pending/processing
  useEffect(() => {
    const hasPending = docs.some(d =>
      d.processing_status === 'pending' || d.processing_status === 'processing'
    )
    if (!hasPending) return

    const interval = setInterval(() => {
      documentsApi.list(id).then(r => setDocs(r.data))
    }, 3000)

    return () => clearInterval(interval)
  }, [docs, id])

  const loadAll = async () => {
    try {
      const [p, d, c] = await Promise.all([
        projectsApi.get(id),
        documentsApi.list(id),
        campaignsApi.list(id)
      ])
      setProject(p.data)
      setDocs(d.data)
      setCampaigns(c.data)
    } catch {
      navigate('/projects')
    } finally {
      setLoading(false)
    }
  }

  const onDrop = useCallback(async files => {
    if (!files.length) return
    setUploading(true)
    for (const file of files) {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('doc_type', docType)
      try {
        await documentsApi.upload(id, fd)
        toast.success(`${file.name} uploaded — processing with GPT-4o...`)
      } catch (err) {
        toast.error(`Failed to upload: ${file.name}`)
      }
    }
    setUploading(false)
    // Refresh doc list so polling picks up pending docs
    documentsApi.list(id).then(r => setDocs(r.data))
  }, [id, docType])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/*': ['.png', '.jpg', '.jpeg']
    }
  })

  const deleteDoc = async docId => {
    try {
      await documentsApi.delete(id, docId)
      setDocs(d => d.filter(x => x.id !== docId))
      toast.success('Document deleted')
    } catch {
      toast.error('Failed to delete document')
    }
  }

  const reprocess = async docId => {
    try {
      await documentsApi.reprocess(id, docId)
      toast.success('Reprocessing started...')
      // Mark as pending locally so polling kicks in immediately
      setDocs(d => d.map(doc =>
        doc.id === docId ? { ...doc, processing_status: 'pending' } : doc
      ))
    } catch {
      toast.error('Failed to reprocess document')
    }
  }

  const deleteProject = async () => {
    if (!confirm('Delete this project and all its data?')) return
    try {
      await projectsApi.delete(id)
      navigate('/projects')
    } catch {
      toast.error('Failed to delete project')
    }
  }

  if (loading) return <div className="p-8 text-gray-400">Loading...</div>
  if (!project) return null

  const doneCount = docs.filter(d => d.processing_status === 'done').length

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link to="/projects" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
          <p className="text-gray-500 text-sm">
            {project.location} • {project.project_type} • {project.status?.replace(/_/g, ' ')}
          </p>
        </div>
        <Link to={`/campaigns?project=${id}`} className="btn-primary flex items-center gap-2">
          <Megaphone size={16} /> Create Campaign
        </Link>
        <button onClick={deleteProject} className="btn-danger">Delete</button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left column — project info + campaigns */}
        <div className="lg:col-span-1 space-y-4">
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Project Details</h3>
            <dl className="space-y-2 text-sm">
              {project.total_units && <Row label="Total Units" value={project.total_units} />}
              {(project.price_range_min || project.price_range_max) && (
                <Row label="Price Range" value={`₹${(project.price_range_min / 1e5).toFixed(0)}L – ₹${(project.price_range_max / 1e5).toFixed(0)}L`} />
              )}
              {project.possession_date && <Row label="Possession" value={project.possession_date} />}
              {project.rera_id && <Row label="RERA ID" value={project.rera_id} />}
              {project.amenities && <Row label="Amenities" value={project.amenities} />}
            </dl>
          </div>

          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-3">Campaigns ({campaigns.length})</h3>
            {campaigns.length === 0 ? (
              <p className="text-gray-400 text-sm">No campaigns yet</p>
            ) : (
              <div className="space-y-2">
                {campaigns.map(c => (
                  <Link key={c.id} to={`/campaigns/${c.id}`} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium text-gray-800">{c.name}</span>
                    <CampaignStatusBadge status={c.status} />
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Knowledge base summary */}
          {docs.length > 0 && (
            <div className="card bg-blue-50 border border-blue-100">
              <h3 className="font-semibold text-blue-900 mb-2 text-sm">Knowledge Base Status</h3>
              <p className="text-blue-700 text-sm">
                {doneCount} of {docs.length} document{docs.length !== 1 ? 's' : ''} processed
              </p>
              <p className="text-blue-500 text-xs mt-1">
                Processed documents are injected into campaign agent prompts automatically.
              </p>
            </div>
          )}
        </div>

        {/* Right column — documents */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Knowledge Base Documents</h3>
              <select
                className="input w-44 text-sm"
                value={docType}
                onChange={e => setDocType(e.target.value)}
              >
                {DOC_TYPES.map(t => (
                  <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
                ))}
              </select>
            </div>

            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-8 text-center mb-4 cursor-pointer transition-colors ${
                isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input {...getInputProps()} />
              <Upload size={32} className="text-gray-400 mx-auto mb-2" />
              {uploading ? (
                <p className="text-blue-600 font-medium animate-pulse">Uploading...</p>
              ) : (
                <>
                  <p className="text-gray-600 font-medium">Drop brochures, floor plans, or price lists here</p>
                  <p className="text-gray-400 text-sm mt-1">PDF, DOCX, PNG, JPG • Processed by GPT-4o</p>
                </>
              )}
            </div>

            {/* Document list */}
            <div className="space-y-2">
              {docs.length === 0 && (
                <p className="text-center text-gray-400 text-sm py-6">
                  No documents uploaded yet. Upload a brochure to get started.
                </p>
              )}
              {docs.map(doc => (
                <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3 min-w-0">
                    <FileText size={18} className="text-blue-500 flex-shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">{doc.original_filename}</p>
                      <p className="text-xs text-gray-400">
                        {doc.doc_type?.replace(/_/g, ' ')} • {(doc.file_size / 1024).toFixed(0)} KB
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                    <ProcessingStatus status={doc.processing_status} />
                    <button
                      onClick={() => reprocess(doc.id)}
                      className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                      title="Reprocess"
                    >
                      <RefreshCw size={14} />
                    </button>
                    <button
                      onClick={() => deleteDoc(doc.id)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div className="flex flex-col">
      <dt className="text-gray-400 text-xs uppercase tracking-wide">{label}</dt>
      <dd className="text-gray-700 font-medium">{value}</dd>
    </div>
  )
}

function ProcessingStatus({ status }) {
  if (status === 'done') return (
    <span className="badge-green flex items-center gap-1">
      <CheckCircle size={10} /> Processed
    </span>
  )
  if (status === 'processing') return (
    <span className="badge-yellow flex items-center gap-1 animate-pulse">
      <Clock size={10} /> Processing
    </span>
  )
  if (status === 'failed') return (
    <span className="badge-red flex items-center gap-1">
      <AlertCircle size={10} /> Failed
    </span>
  )
  return (
    <span className="badge-gray flex items-center gap-1 animate-pulse">
      <Clock size={10} /> Pending
    </span>
  )
}

function CampaignStatusBadge({ status }) {
  const map = { active: 'badge-green', draft: 'badge-gray', paused: 'badge-yellow', completed: 'badge-blue' }
  return <span className={map[status] || 'badge-gray'}>{status}</span>
}