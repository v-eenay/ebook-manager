import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>eBook Manager</h1>
        <p>
          A desktop application for managing your eBook collection
        </p>
        
        <div className="card">
          <button onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button>
          <p>
            Edit <code>src/App.tsx</code> and save to test HMR
          </p>
        </div>

        <div className="features">
          <h2>Features Coming Soon:</h2>
          <ul>
            <li>📚 Import and organize eBooks</li>
            <li>🔍 Search and filter your collection</li>
            <li>📖 Built-in eBook reader</li>
            <li>🏷️ Tag and categorize books</li>
            <li>📊 Reading progress tracking</li>
          </ul>
        </div>
      </header>
    </div>
  )
}

export default App
