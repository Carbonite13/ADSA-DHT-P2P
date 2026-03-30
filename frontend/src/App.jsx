import { useState, useEffect } from 'react'
import axios from 'axios'
import { Plus, Minus, Upload, Search, Trash2, Box, Cpu, FileText, Activity } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  const [state, setState] = useState({})
  const [nodeName, setNodeName] = useState('')
  const [removeNodeName, setRemoveNodeName] = useState('')
  const [fileName, setFileName] = useState('')
  const [peerName, setPeerName] = useState('')
  const [deleteFile, setDeleteFile] = useState('')
  const [searchKey, setSearchKey] = useState('')
  const [highlightKey, setHighlightKey] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchState = async (highlight = null) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/state`)
      setState(response.data)
      if (highlight) setHighlightKey(highlight)
    } catch (error) {
      console.error('Error fetching state:', error)
    }
  }

  useEffect(() => {
    fetchState()
    const interval = setInterval(() => fetchState(highlightKey), 5000)
    return () => clearInterval(interval)
  }, [highlightKey])

  const handleAction = async (endpoint, data, callback = null) => {
    setLoading(true)
    try {
      await axios.post(`${API_BASE_URL}/${endpoint}`, data)
      if (callback) callback()
      fetchState()
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`)
    }
    setLoading(false)
  }

  const handleSearch = async () => {
    if (!searchKey) return
    try {
      const response = await axios.get(`${API_BASE_URL}/download?file=${encodeURIComponent(searchKey)}`)
      if (response.data.peers && response.data.peers.length > 0) {
        alert(`✅ File found in peer(s): ${response.data.peers.join(', ')}`)
      } else {
        alert('❌ File not found.')
      }
      setHighlightKey(searchKey)
    } catch (error) {
      console.error(error)
      alert('❌ File not found.')
      setHighlightKey(null)
    }
  }

  // Derived stats
  const activeNodes = Object.keys(state).length
  const totalFiles = Object.values(state).reduce((acc, node) => acc + node.files.length, 0)
  const systemLoad = activeNodes > 0 ? (totalFiles / activeNodes).toFixed(1) : 0

  return (
    <div className="app-container">
      {/* HUD Overlay */}
      <div className="main-stage">
        <header className="header">
          <div className="logo">
            <Box color="#3b82f6" strokeWidth={2.5} />
            <h1>DHT SIMULATOR</h1>
            <span>v2.0</span>
          </div>
          <div className="stats-hud">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">Active Nodes</div>
                <div className="stat-value">{activeNodes}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">System Load</div>
                <div className="stat-value">{systemLoad}</div>
              </div>
            </div>
          </div>
        </header>

        <div className="viz">
          <svg width="600" height="600" viewBox="0 0 500 500">
            <defs>
              <radialGradient id="ring-gradient">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.1" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
              </radialGradient>
            </defs>
            <circle cx="250" cy="250" r="180" className="main-ring" />
            
            <AnimatePresence>
              {Object.entries(state).map(([name, data]) => {
                const angle = data.angle * Math.PI / 180
                const x = 250 + 180 * Math.cos(angle)
                const y = 250 + 180 * Math.sin(angle)

                return (
                  <g key={name}>
                    {/* Node Dot */}
                    <motion.circle
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                      cx={x} cy={y} r="6"
                      className="node-dot"
                      fill="#fff"
                    />
                    <text x={x + 10} y={y + 5} fill="#fff" fontSize="10" fontWeight="600">{name}</text>

                    {/* Files connected to this node */}
                    {data.files.map((file) => {
                      const fAngle = file.angle * Math.PI / 180
                      const fx = 250 + 180 * Math.cos(fAngle)
                      const fy = 250 + 180 * Math.sin(fAngle)
                      const isHighlighted = file.name === highlightKey

                      return (
                        <g key={file.name}>
                          <line x1={x} y1={y} x2={fx} y2={fy} className="line-connector" strokeWidth={isHighlighted ? 1 : 0.5} />
                          <motion.circle
                            animate={{ scale: isHighlighted ? 1.5 : 1 }}
                            cx={fx} cy={fy} r={isHighlighted ? 4 : 3}
                            className="file-point"
                            fill={isHighlighted ? '#3b82f6' : '#f59e0b'}
                          />
                          <text x={fx + 8} y={fy + 3} fill={isHighlighted ? '#3b82f6' : '#fff'} fontSize="8" fontWeight={isHighlighted ? '700' : '400'}>
                            {file.name}
                          </text>
                        </g>
                      )
                    })}
                  </g>
                )
              })}
            </AnimatePresence>
          </svg>
        </div>
      </div>

      <aside className="sidebar">
        <section>
          <div className="section-title"><Cpu size={12} /> Network Nodes</div>
          <div className="control-group">
            <div className="input-row">
              <input value={nodeName} onChange={e => setNodeName(e.target.value)} placeholder="Node Identifier" />
              <button disabled={loading} onClick={() => handleAction('add_node', { name: nodeName }, () => setNodeName(''))}>
                <Plus size={16} />
              </button>
            </div>
            <div className="input-row">
              <input value={removeNodeName} onChange={e => setRemoveNodeName(e.target.value)} placeholder="Drop Node" />
              <button disabled={loading} className="secondary" onClick={() => handleAction('remove_node', { name: removeNodeName }, () => setRemoveNodeName(''))}>
                <Minus size={16} />
              </button>
            </div>
          </div>
        </section>

        <section>
          <div className="section-title"><FileText size={12} /> File Operations</div>
          <div className="control-group">
            <input value={fileName} onChange={e => setFileName(e.target.value)} placeholder="Filename" />
            <input value={peerName} onChange={e => setPeerName(e.target.value)} placeholder="Peer Name" />
            <button disabled={loading} onClick={() => handleAction('upload', { file: fileName, peer: peerName }, () => { setFileName(''); setPeerName(''); })}>
              <Upload size={16} /> Share File
            </button>
            <hr style={{ opacity: 0.1, width: '100%', margin: '8px 0' }} />
            <div className="input-row">
              <input value={deleteFile} onChange={e => setDeleteFile(e.target.value)} placeholder="Filename" />
              <button disabled={loading} className="secondary" onClick={() => handleAction('delete', { file: deleteFile }, () => setDeleteFile(''))}>
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        </section>

        <section>
          <div className="section-title"><Search size={12} /> Global Lookup</div>
          <div className="control-group">
            <div className="input-row">
              <input value={searchKey} onChange={e => setSearchKey(e.target.value)} placeholder="Search for key..." />
              <button disabled={loading} onClick={handleSearch}>
                <Activity size={16} /> Find
              </button>
            </div>
          </div>
        </section>
      </aside>
    </div>
  )
}

export default App
