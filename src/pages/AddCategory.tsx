import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import './AddCategory.css'

const AddCategory: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#667eea',
    icon: '📚',
    parentCategory: '',
    isPublic: true,
    tags: '',
    sortOrder: '',
    coverImage: ''
  })

  const [previewMode, setPreviewMode] = useState(false)

  const predefinedCategories = [
    'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Romance',
    'Mystery', 'Thriller', 'Biography', 'History', 'Self-Help',
    'Business', 'Technology', 'Science', 'Philosophy', 'Art'
  ]

  const iconOptions = [
    '📚', '📖', '📕', '📗', '📘', '📙', '📔', '📓', '📒', '📑',
    '🔬', '🎨', '💼', '🏛️', '⚡', '🌟', '🔥', '💡', '🎯', '🚀',
    '🌍', '🎭', '🎵', '📊', '💻', '🔧', '🏆', '💎', '🌺', '🦋'
  ]

  const colorOptions = [
    '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
    '#43e97b', '#fa709a', '#fee140', '#a8edea', '#d299c2',
    '#89f7fe', '#66a6ff', '#f78ca0', '#96deda', '#c3cfe2'
  ]

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setFormData(prev => ({
        ...prev,
        [name]: checked
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }))
    }
  }

  const handleIconSelect = (icon: string) => {
    setFormData(prev => ({
      ...prev,
      icon
    }))
  }

  const handleColorSelect = (color: string) => {
    setFormData(prev => ({
      ...prev,
      color
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Category data:', formData)
    // Here you would typically send the data to your backend
    alert('Category added successfully!')
  }

  const generateSlug = () => {
    const slug = formData.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
    return slug
  }

  return (
    <div className="add-category">
      <div className="page-header">
        <h2>Add New Category</h2>
        <Link to="/categories" className="back-btn">
          ← Back to Categories
        </Link>
      </div>

      <div className="form-container">
        <form onSubmit={handleSubmit} className="category-form">
          <div className="form-section">
            <h3>Basic Information</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="name">Category Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter category name"
                />
                {formData.name && (
                  <div className="slug-preview">
                    Slug: <code>{generateSlug()}</code>
                  </div>
                )}
              </div>
              <div className="form-group">
                <label htmlFor="parentCategory">Parent Category</label>
                <select
                  id="parentCategory"
                  name="parentCategory"
                  value={formData.parentCategory}
                  onChange={handleInputChange}
                >
                  <option value="">None (Top Level)</option>
                  {predefinedCategories.map(category => (
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
                placeholder="Describe what types of books belong in this category"
              />
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
                <label htmlFor="sortOrder">Sort Order</label>
                <input
                  type="number"
                  id="sortOrder"
                  name="sortOrder"
                  value={formData.sortOrder}
                  onChange={handleInputChange}
                  placeholder="Display order (optional)"
                  min="0"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Appearance</h3>
            <div className="appearance-controls">
              <div className="form-group">
                <label>Category Icon</label>
                <div className="icon-selector">
                  {iconOptions.map(icon => (
                    <button
                      key={icon}
                      type="button"
                      className={`icon-option ${formData.icon === icon ? 'selected' : ''}`}
                      onClick={() => handleIconSelect(icon)}
                    >
                      {icon}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Category Color</label>
                <div className="color-selector">
                  {colorOptions.map(color => (
                    <button
                      key={color}
                      type="button"
                      className={`color-option ${formData.color === color ? 'selected' : ''}`}
                      style={{ backgroundColor: color }}
                      onClick={() => handleColorSelect(color)}
                    />
                  ))}
                </div>
                <input
                  type="color"
                  value={formData.color}
                  onChange={(e) => handleColorSelect(e.target.value)}
                  className="custom-color-picker"
                />
              </div>

              <div className="form-group">
                <label htmlFor="coverImage">Cover Image URL</label>
                <input
                  type="url"
                  id="coverImage"
                  name="coverImage"
                  value={formData.coverImage}
                  onChange={handleInputChange}
                  placeholder="Enter cover image URL (optional)"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Settings</h3>
            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="isPublic"
                  checked={formData.isPublic}
                  onChange={handleInputChange}
                />
                <span className="checkmark"></span>
                Make this category public
                <small>Other users can see and use this category</small>
              </label>
            </div>
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="preview-btn"
              onClick={() => setPreviewMode(!previewMode)}
            >
              {previewMode ? 'Edit' : 'Preview'}
            </button>
            <button type="button" className="cancel-btn">
              Cancel
            </button>
            <button type="submit" className="submit-btn">
              Add Category
            </button>
          </div>
        </form>

        {previewMode && (
          <div className="category-preview">
            <h3>📋 Preview</h3>
            <div className="preview-card" style={{ background: `linear-gradient(135deg, ${formData.color}, ${formData.color}cc)` }}>
              <div className="preview-icon">{formData.icon}</div>
              <div className="preview-content">
                <h4>{formData.name || 'Category Name'}</h4>
                <p>{formData.description || 'Category description will appear here'}</p>
                {formData.parentCategory && (
                  <div className="preview-parent">
                    Parent: {formData.parentCategory}
                  </div>
                )}
                {formData.tags && (
                  <div className="preview-tags">
                    {formData.tags.split(',').map((tag, index) => (
                      <span key={index} className="preview-tag">
                        {tag.trim()}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
            
            {formData.coverImage && (
              <div className="preview-cover">
                <img src={formData.coverImage} alt="Category cover" />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default AddCategory
