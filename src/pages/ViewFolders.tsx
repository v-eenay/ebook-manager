import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import './ViewFolders.css'

interface Folder {
  id: number
  name: string
  path: string
  bookCount: number
  subfolders: number
  lastModified: string
  size: string
  icon: string
  sampleBooks: string[]
}

const ViewFolders: React.FC = () => {
  const [expandedFolders, setExpandedFolders] = useState<Set<number>>(new Set())

  const folders: Folder[] = [
    {
      id: 1,
      name: 'Fiction Collection',
      path: '/Documents/eBooks/Fiction',
      bookCount: 45,
      subfolders: 3,
      lastModified: '2024-02-15',
      size: '2.3 GB',
      icon: '📚',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8225261-S.jpg',
        'https://covers.openlibrary.org/b/id/7222246-S.jpg',
        'https://covers.openlibrary.org/b/id/8231436-S.jpg'
      ]
    },
    {
      id: 2,
      name: 'Science & Technology',
      path: '/Documents/eBooks/Science',
      bookCount: 28,
      subfolders: 5,
      lastModified: '2024-02-12',
      size: '1.8 GB',
      icon: '🔬',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8279808-S.jpg',
        'https://covers.openlibrary.org/b/id/8134490-S.jpg',
        'https://covers.openlibrary.org/b/id/8195632-S.jpg'
      ]
    },
    {
      id: 3,
      name: 'History & Biography',
      path: '/Documents/eBooks/History',
      bookCount: 32,
      subfolders: 2,
      lastModified: '2024-02-10',
      size: '1.5 GB',
      icon: '📜',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8210954-S.jpg',
        'https://covers.openlibrary.org/b/id/8173640-S.jpg',
        'https://covers.openlibrary.org/b/id/8198275-S.jpg'
      ]
    },
    {
      id: 4,
      name: 'Fantasy & Sci-Fi',
      path: '/Documents/eBooks/Fantasy',
      bookCount: 38,
      subfolders: 4,
      lastModified: '2024-02-08',
      size: '2.1 GB',
      icon: '🐉',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8165743-S.jpg',
        'https://covers.openlibrary.org/b/id/8201846-S.jpg',
        'https://covers.openlibrary.org/b/id/8187529-S.jpg'
      ]
    },
    {
      id: 5,
      name: 'Romance Collection',
      path: '/Documents/eBooks/Romance',
      bookCount: 22,
      subfolders: 1,
      lastModified: '2024-02-05',
      size: '1.2 GB',
      icon: '💕',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8091016-S.jpg',
        'https://covers.openlibrary.org/b/id/8142464-S.jpg',
        'https://covers.openlibrary.org/b/id/8200280-S.jpg'
      ]
    },
    {
      id: 6,
      name: 'Business & Self-Help',
      path: '/Documents/eBooks/Business',
      bookCount: 18,
      subfolders: 2,
      lastModified: '2024-02-03',
      size: '950 MB',
      icon: '💼',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8180349-S.jpg',
        'https://covers.openlibrary.org/b/id/8154392-S.jpg',
        'https://covers.openlibrary.org/b/id/8176521-S.jpg'
      ]
    },
    {
      id: 7,
      name: 'Mystery & Thriller',
      path: '/Documents/eBooks/Mystery',
      bookCount: 25,
      subfolders: 3,
      lastModified: '2024-02-01',
      size: '1.4 GB',
      icon: '🔍',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8156819-S.jpg',
        'https://covers.openlibrary.org/b/id/8174521-S.jpg',
        'https://covers.openlibrary.org/b/id/8190847-S.jpg'
      ]
    },
    {
      id: 8,
      name: 'Children\'s Books',
      path: '/Documents/eBooks/Children',
      bookCount: 15,
      subfolders: 1,
      lastModified: '2024-01-28',
      size: '680 MB',
      icon: '🧸',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8162847-S.jpg',
        'https://covers.openlibrary.org/b/id/8185430-S.jpg',
        'https://covers.openlibrary.org/b/id/8167293-S.jpg'
      ]
    }
  ]

  const toggleFolder = (folderId: number) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev)
      if (newSet.has(folderId)) {
        newSet.delete(folderId)
      } else {
        newSet.add(folderId)
      }
      return newSet
    })
  }

  const totalBooks = folders.reduce((sum, folder) => sum + folder.bookCount, 0)
  const totalSize = folders.reduce((sum, folder) => {
    const size = parseFloat(folder.size)
    const unit = folder.size.includes('GB') ? 1024 : 1
    return sum + (size * unit)
  }, 0)

  return (
    <div className="view-folders">
      <div className="page-header">
        <h2>📁 Folder Organization</h2>
        <div className="header-actions">
          <button className="scan-folders-btn">
            🔄 Scan Folders
          </button>
          <button className="add-folder-btn">
            ➕ Add Folder
          </button>
        </div>
      </div>

      <div className="folders-stats">
        <div className="stat-card">
          <span className="stat-number">{folders.length}</span>
          <span className="stat-label">Folders</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{totalBooks}</span>
          <span className="stat-label">Total Books</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{totalSize.toFixed(1)} MB</span>
          <span className="stat-label">Total Size</span>
        </div>
      </div>

      <div className="folders-list">
        {folders.map(folder => (
          <div key={folder.id} className="folder-card">
            <div className="folder-header" onClick={() => toggleFolder(folder.id)}>
              <div className="folder-main-info">
                <div className="folder-icon">{folder.icon}</div>
                <div className="folder-details">
                  <h3 className="folder-name">{folder.name}</h3>
                  <p className="folder-path">{folder.path}</p>
                </div>
              </div>
              <div className="folder-meta">
                <div className="folder-stats">
                  <span className="book-count">{folder.bookCount} books</span>
                  <span className="subfolder-count">{folder.subfolders} subfolders</span>
                  <span className="folder-size">{folder.size}</span>
                </div>
                <button className="expand-btn">
                  {expandedFolders.has(folder.id) ? '▲' : '▼'}
                </button>
              </div>
            </div>

            {expandedFolders.has(folder.id) && (
              <div className="folder-expanded">
                <div className="folder-info">
                  <div className="info-item">
                    <span className="info-label">Last Modified:</span>
                    <span className="info-value">{folder.lastModified}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Full Path:</span>
                    <span className="info-value">{folder.path}</span>
                  </div>
                </div>

                <div className="sample-books">
                  <h4>Sample Books:</h4>
                  <div className="sample-covers">
                    {folder.sampleBooks.map((cover, index) => (
                      <img 
                        key={index} 
                        src={cover} 
                        alt={`Sample book ${index + 1}`}
                        className="sample-cover"
                      />
                    ))}
                  </div>
                </div>

                <div className="folder-actions">
                  <button className="open-folder-btn">
                    📂 Open Folder
                  </button>
                  <button className="view-books-btn">
                    📚 View Books
                  </button>
                  <button className="sync-btn">
                    🔄 Sync
                  </button>
                  <button className="settings-btn">
                    ⚙️ Settings
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="folder-tree">
        <h3>📊 Folder Structure Overview</h3>
        <div className="tree-container">
          <div className="tree-item root">
            <span className="tree-icon">📁</span>
            <span className="tree-label">eBooks Root</span>
          </div>
          {folders.map(folder => (
            <div key={folder.id} className="tree-item">
              <span className="tree-connector">├─</span>
              <span className="tree-icon">{folder.icon}</span>
              <span className="tree-label">{folder.name}</span>
              <span className="tree-count">({folder.bookCount})</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ViewFolders
