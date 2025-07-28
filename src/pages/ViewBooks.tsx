import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import './ViewBooks.css'

interface Book {
  id: number
  title: string
  author: string
  category: string
  cover: string
  rating: number
  progress: number
  dateAdded: string
}

const ViewBooks: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState('all')

  // Sample book data with web images
  const books: Book[] = [
    {
      id: 1,
      title: 'The Great Gatsby',
      author: 'F. Scott Fitzgerald',
      category: 'Fiction',
      cover: 'https://covers.openlibrary.org/b/id/8225261-L.jpg',
      rating: 4.5,
      progress: 100,
      dateAdded: '2024-01-15'
    },
    {
      id: 2,
      title: 'To Kill a Mockingbird',
      author: 'Harper Lee',
      category: 'Fiction',
      cover: 'https://covers.openlibrary.org/b/id/7222246-L.jpg',
      rating: 4.8,
      progress: 45,
      dateAdded: '2024-01-20'
    },
    {
      id: 3,
      title: '1984',
      author: 'George Orwell',
      category: 'Dystopian',
      cover: 'https://covers.openlibrary.org/b/id/8739161-L.jpg',
      rating: 4.7,
      progress: 0,
      dateAdded: '2024-01-25'
    },
    {
      id: 4,
      title: 'Pride and Prejudice',
      author: 'Jane Austen',
      category: 'Romance',
      cover: 'https://covers.openlibrary.org/b/id/8091016-L.jpg',
      rating: 4.6,
      progress: 78,
      dateAdded: '2024-02-01'
    },
    {
      id: 5,
      title: 'The Catcher in the Rye',
      author: 'J.D. Salinger',
      category: 'Fiction',
      cover: 'https://covers.openlibrary.org/b/id/8231436-L.jpg',
      rating: 4.2,
      progress: 23,
      dateAdded: '2024-02-05'
    },
    {
      id: 6,
      title: 'Dune',
      author: 'Frank Herbert',
      category: 'Science Fiction',
      cover: 'https://covers.openlibrary.org/b/id/8279808-L.jpg',
      rating: 4.9,
      progress: 67,
      dateAdded: '2024-02-10'
    }
  ]

  const categories = ['all', 'Fiction', 'Romance', 'Science Fiction', 'Dystopian']

  const filteredBooks = books.filter(book => {
    const matchesSearch = book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         book.author.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = filterCategory === 'all' || book.category === filterCategory
    return matchesSearch && matchesCategory
  })

  const renderStars = (rating: number) => {
    const stars = []
    for (let i = 1; i <= 5; i++) {
      if (i <= rating) {
        stars.push(<span key={i} className="star filled">★</span>)
      } else if (i - 0.5 <= rating) {
        stars.push(<span key={i} className="star half">★</span>)
      } else {
        stars.push(<span key={i} className="star empty">☆</span>)
      }
    }
    return stars
  }

  return (
    <div className="view-books">
      <div className="page-header">
        <h2>Book Collection</h2>
        <Link to="/add-book" className="add-book-btn">
          Add New Book
        </Link>
      </div>

      <div className="filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search books or authors..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="category-filter">
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="category-select"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="books-stats">
        <span>{filteredBooks.length} books found</span>
      </div>

      <div className="books-grid">
        {filteredBooks.map(book => (
          <div key={book.id} className="book-card">
            <div className="book-cover">
              <img src={book.cover} alt={book.title} />
              <div className="book-overlay">
                <button className="read-btn">📖 Read</button>
                <button className="edit-btn">✏️ Edit</button>
              </div>
            </div>
            <div className="book-info">
              <h3 className="book-title">{book.title}</h3>
              <p className="book-author">{book.author}</p>
              <div className="book-category">{book.category}</div>
              <div className="book-rating">
                {renderStars(book.rating)}
                <span className="rating-number">({book.rating})</span>
              </div>
              <div className="book-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${book.progress}%` }}
                  ></div>
                </div>
                <span className="progress-text">{book.progress}% complete</span>
              </div>
              <div className="book-date">Added: {book.dateAdded}</div>
            </div>
          </div>
        ))}
      </div>

      {filteredBooks.length === 0 && (
        <div className="no-books">
          <h3>No books found</h3>
          <p>Try adjusting your search or filter criteria</p>
        </div>
      )}
    </div>
  )
}

export default ViewBooks
