import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import ThemeSelector from './ThemeSelector'
import './Layout.css'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Link to="/">
              <h1>eBook Manager</h1>
            </Link>
          </div>
          <nav className="nav">
            <div className="nav-actions">
              <Link 
                to="/add-book" 
                className={`nav-button add-button ${location.pathname === '/add-book' ? 'active' : ''}`}
              >
                Add Book
              </Link>
              <Link 
                to="/add-category" 
                className={`nav-button add-button ${location.pathname === '/add-category' ? 'active' : ''}`}
              >
                Add Category
              </Link>
              <ThemeSelector />
            </div>
          </nav>
        </div>
      </header>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default Layout
