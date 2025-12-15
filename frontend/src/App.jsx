import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        setHealth(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to fetch health:', err)
        setLoading(false)
      })
  }, [])

  return (
    <div className="App">
      <header className="App-header">
        <h1>FastAPI + React Application</h1>
        {loading ? (
          <p>Loading...</p>
        ) : health ? (
          <div className="health-status">
            <p>✅ Backend Status: {health.status}</p>
            <p>{health.message}</p>
          </div>
        ) : (
          <p>❌ Failed to connect to backend</p>
        )}
      </header>
    </div>
  )
}

export default App
