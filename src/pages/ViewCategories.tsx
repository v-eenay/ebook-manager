import React from 'react'
import { Link } from 'react-router-dom'
import './ViewCategories.css'

interface Category {
  id: number
  name: string
  description: string
  bookCount: number
  color: string
  icon: string
  sampleBooks: string[]
}

const ViewCategories: React.FC = () => {
  const categories: Category[] = [
    {
      id: 1,
      name: 'Fiction',
      description: 'Imaginative literature including novels and short stories',
      bookCount: 45,
      color: '#E91E63',
      icon: '📚',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8225261-S.jpg',
        'https://covers.openlibrary.org/b/id/7222246-S.jpg',
        'https://covers.openlibrary.org/b/id/8231436-S.jpg'
      ]
    },
    {
      id: 2,
      name: 'Science Fiction',
      description: 'Stories that deal with futuristic concepts and advanced technology',
      bookCount: 23,
      color: '#2196F3',
      icon: '🚀',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8279808-S.jpg',
        'https://covers.openlibrary.org/b/id/8739161-S.jpg',
        'https://covers.openlibrary.org/b/id/8134490-S.jpg'
      ]
    },
    {
      id: 3,
      name: 'Romance',
      description: 'Stories centered around love and romantic relationships',
      bookCount: 18,
      color: '#FF5722',
      icon: '💕',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8091016-S.jpg',
        'https://covers.openlibrary.org/b/id/8142464-S.jpg',
        'https://covers.openlibrary.org/b/id/8200280-S.jpg'
      ]
    },
    {
      id: 4,
      name: 'Mystery',
      description: 'Suspenseful stories involving crimes or puzzles to solve',
      bookCount: 12,
      color: '#9C27B0',
      icon: '🔍',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8156819-S.jpg',
        'https://covers.openlibrary.org/b/id/8174521-S.jpg',
        'https://covers.openlibrary.org/b/id/8190847-S.jpg'
      ]
    },
    {
      id: 5,
      name: 'Non-Fiction',
      description: 'Factual books including biographies, history, and self-help',
      bookCount: 31,
      color: '#4CAF50',
      icon: '📖',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8210954-S.jpg',
        'https://covers.openlibrary.org/b/id/8195632-S.jpg',
        'https://covers.openlibrary.org/b/id/8180349-S.jpg'
      ]
    },
    {
      id: 6,
      name: 'Fantasy',
      description: 'Magical worlds with supernatural elements and creatures',
      bookCount: 27,
      color: '#FF9800',
      icon: '🐉',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8165743-S.jpg',
        'https://covers.openlibrary.org/b/id/8201846-S.jpg',
        'https://covers.openlibrary.org/b/id/8187529-S.jpg'
      ]
    },
    {
      id: 7,
      name: 'Biography',
      description: 'Life stories of notable people and historical figures',
      bookCount: 14,
      color: '#795548',
      icon: '👤',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8173640-S.jpg',
        'https://covers.openlibrary.org/b/id/8198275-S.jpg',
        'https://covers.openlibrary.org/b/id/8154392-S.jpg'
      ]
    },
    {
      id: 8,
      name: 'Dystopian',
      description: 'Stories set in societies where life is miserable and oppressive',
      bookCount: 8,
      color: '#607D8B',
      icon: '🌆',
      sampleBooks: [
        'https://covers.openlibrary.org/b/id/8739161-S.jpg',
        'https://covers.openlibrary.org/b/id/8162847-S.jpg',
        'https://covers.openlibrary.org/b/id/8185430-S.jpg'
      ]
    }
  ]

  const totalBooks = categories.reduce((sum, category) => sum + category.bookCount, 0)

  return (
    <div className="view-categories">
      <div className="page-header">
        <h2>🏷️ Book Categories</h2>
        <Link to="/add-category" className="add-category-btn">
          ➕ Add New Category
        </Link>
      </div>

      <div className="categories-stats">
        <div className="stat-card">
          <span className="stat-number">{categories.length}</span>
          <span className="stat-label">Categories</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{totalBooks}</span>
          <span className="stat-label">Total Books</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{Math.round(totalBooks / categories.length)}</span>
          <span className="stat-label">Avg per Category</span>
        </div>
      </div>

      <div className="categories-grid">
        {categories.map(category => (
          <div key={category.id} className="category-card">
            <div className="category-header" style={{ borderLeftColor: category.color }}>
              <div className="category-icon" style={{ backgroundColor: category.color }}>
                {category.icon}
              </div>
              <div className="category-title">
                <h3>{category.name}</h3>
                <span className="book-count">{category.bookCount} books</span>
              </div>
            </div>
            
            <p className="category-description">{category.description}</p>
            
            <div className="sample-books">
              <span className="sample-label">Recent books:</span>
              <div className="sample-covers">
                {category.sampleBooks.map((cover, index) => (
                  <img 
                    key={index} 
                    src={cover} 
                    alt={`Sample book ${index + 1}`}
                    className="sample-cover"
                  />
                ))}
              </div>
            </div>
            
            <div className="category-actions">
              <button className="view-books-btn" style={{ backgroundColor: category.color }}>
                View Books
              </button>
              <button className="edit-category-btn">
                Edit Category
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="category-distribution">
        <h3>Category Distribution</h3>
        <div className="distribution-chart">
          {categories.map(category => (
            <div key={category.id} className="distribution-bar">
              <div className="bar-label">
                <span className="bar-icon" style={{ color: category.color }}>
                  {category.icon}
                </span>
                <span className="bar-name">{category.name}</span>
                <span className="bar-count">{category.bookCount}</span>
              </div>
              <div className="bar-container">
                <div 
                  className="bar-fill" 
                  style={{ 
                    width: `${(category.bookCount / Math.max(...categories.map(c => c.bookCount))) * 100}%`,
                    backgroundColor: category.color 
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ViewCategories
