import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import './AddBook.css'

const AddBook: React.FC = () => {
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    isbn: '',
    category: '',
    description: '',
    publisher: '',
    publishedDate: '',
    pages: '',
    language: 'English',
    format: 'PDF',
    filePath: '',
    coverUrl: '',
    tags: '',
    rating: '',
    notes: ''
  })

  const [dragActive, setDragActive] = useState(false)

  const categories = [
    'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Romance', 
    'Mystery', 'Thriller', 'Biography', 'History', 'Self-Help', 
    'Business', 'Technology', 'Science', 'Philosophy', 'Art', 'Other'
  ]

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      setFormData(prev => ({
        ...prev,
        filePath: file.name
      }))
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setFormData(prev => ({
        ...prev,
        filePath: file.name
      }))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Book data:', formData)
    // Here you would typically send the data to your backend
    alert('Book added successfully!')
  }

  const fetchBookInfo = async () => {
    if (!formData.isbn) {
      alert('Please enter an ISBN first')
      return
    }
    
    // Mock book data fetch
    setFormData(prev => ({
      ...prev,
      title: 'Sample Book Title',
      author: 'Sample Author',
      publisher: 'Sample Publisher',
      publishedDate: '2024-01-01',
      pages: '300',
      description: 'This is a sample book description that would be fetched from a book database API.',
      coverUrl: 'https://covers.openlibrary.org/b/id/8225261-L.jpg'
    }))
  }

  return (
    <div className="add-book">
      <div className="page-header">
        <h2>Add New Book</h2>
        <Link to="/books" className="back-btn">
          ← Back to Books
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="book-form">
        <div className="form-section">
          <h3>Basic Information</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
                placeholder="Enter book title"
              />
            </div>
            <div className="form-group">
              <label htmlFor="author">Author *</label>
              <input
                type="text"
                id="author"
                name="author"
                value={formData.author}
                onChange={handleInputChange}
                required
                placeholder="Enter author name"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="isbn">ISBN</label>
              <div className="isbn-input">
                <input
                  type="text"
                  id="isbn"
                  name="isbn"
                  value={formData.isbn}
                  onChange={handleInputChange}
                  placeholder="Enter ISBN (optional)"
                />
                <button type="button" onClick={fetchBookInfo} className="fetch-btn">
                  🔍 Fetch Info
                </button>
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="category">Category *</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                required
              >
                <option value="">Select a category</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={4}
              placeholder="Enter book description"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Publication Details</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="publisher">Publisher</label>
              <input
                type="text"
                id="publisher"
                name="publisher"
                value={formData.publisher}
                onChange={handleInputChange}
                placeholder="Enter publisher name"
              />
            </div>
            <div className="form-group">
              <label htmlFor="publishedDate">Published Date</label>
              <input
                type="date"
                id="publishedDate"
                name="publishedDate"
                value={formData.publishedDate}
                onChange={handleInputChange}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="pages">Pages</label>
              <input
                type="number"
                id="pages"
                name="pages"
                value={formData.pages}
                onChange={handleInputChange}
                placeholder="Number of pages"
                min="1"
              />
            </div>
            <div className="form-group">
              <label htmlFor="language">Language</label>
              <select
                id="language"
                name="language"
                value={formData.language}
                onChange={handleInputChange}
              >
                <option value="English">English</option>
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
                <option value="German">German</option>
                <option value="Italian">Italian</option>
                <option value="Portuguese">Portuguese</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>File & Format</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="format">Format</label>
              <select
                id="format"
                name="format"
                value={formData.format}
                onChange={handleInputChange}
              >
                <option value="PDF">PDF</option>
                <option value="EPUB">EPUB</option>
                <option value="MOBI">MOBI</option>
                <option value="TXT">TXT</option>
                <option value="DOCX">DOCX</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>File Upload</label>
            <div 
              className={`file-drop-zone ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="drop-zone-content">
                <div className="drop-icon">File</div>
                <p>Drag and drop your eBook file here</p>
                <p>or</p>
                <input
                  type="file"
                  id="file-input"
                  onChange={handleFileSelect}
                  accept=".pdf,.epub,.mobi,.txt,.docx"
                  style={{ display: 'none' }}
                />
                <label htmlFor="file-input" className="file-select-btn">
                  Choose File
                </label>
                {formData.filePath && (
                  <p className="selected-file">Selected: {formData.filePath}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Cover & Metadata</h3>
          <div className="form-row">
            <div className="form-group cover-preview">
              <label htmlFor="coverUrl">Cover Image URL</label>
              <input
                type="url"
                id="coverUrl"
                name="coverUrl"
                value={formData.coverUrl}
                onChange={handleInputChange}
                placeholder="Enter cover image URL"
              />
              {formData.coverUrl && (
                <div className="cover-preview-img">
                  <img src={formData.coverUrl} alt="Book cover preview" />
                </div>
              )}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tags">Tags</label>
              <input
                type="text"
                id="tags"
                name="tags"
                value={formData.tags}
                onChange={handleInputChange}
                placeholder="Enter tags separated by commas"
              />
            </div>
            <div className="form-group">
              <label htmlFor="rating">Rating</label>
              <select
                id="rating"
                name="rating"
                value={formData.rating}
                onChange={handleInputChange}
              >
                <option value="">No rating</option>
                <option value="1">⭐ 1 Star</option>
                <option value="2">⭐⭐ 2 Stars</option>
                <option value="3">⭐⭐⭐ 3 Stars</option>
                <option value="4">⭐⭐⭐⭐ 4 Stars</option>
                <option value="5">⭐⭐⭐⭐⭐ 5 Stars</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="notes">Personal Notes</label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              placeholder="Add your personal notes about this book"
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="cancel-btn">
            Cancel
          </button>
          <button type="submit" className="submit-btn">
            Add Book
          </button>
        </div>
      </form>
    </div>
  )
}

export default AddBook
