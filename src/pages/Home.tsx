import React from 'react'
import { Link } from 'react-router-dom'
import './Home.css'

const Home: React.FC = () => {
  return (
    <div className="home">
      <div className="welcome-section">
        <h2>Welcome to your Digital Library</h2>
        <p>Organize, categorize, and enjoy your eBook collection</p>
      </div>

      <div className="home-grid">
        <Link to="/books" className="home-card books-card">
          <div className="card-icon">Books</div>
          <h3>View Books</h3>
          <p>Browse and manage your entire eBook collection</p>
          <div className="card-stats">
            <span>127 Books Available</span>
          </div>
        </Link>

        <Link to="/categories" className="home-card categories-card">
          <div className="card-icon">Categories</div>
          <h3>View Categories</h3>
          <p>Organize your books by genres and topics</p>
          <div className="card-stats">
            <span>15 Categories</span>
          </div>
        </Link>

        <Link to="/folders" className="home-card folders-card">
          <div className="card-icon">Folders</div>
          <h3>View Folders</h3>
          <p>Access books organized by folder structure</p>
          <div className="card-stats">
            <span>8 Folders</span>
          </div>
        </Link>
      </div>

      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          <div className="activity-item">
            <img src="https://covers.openlibrary.org/b/id/8225261-M.jpg" alt="Recent book" className="activity-image" />
            <div className="activity-details">
              <h4>The Great Gatsby</h4>
              <p>Added to Fiction category</p>
              <span className="activity-time">2 hours ago</span>
            </div>
          </div>
          <div className="activity-item">
            <img src="https://covers.openlibrary.org/b/id/7222246-M.jpg" alt="Recent book" className="activity-image" />
            <div className="activity-details">
              <h4>To Kill a Mockingbird</h4>
              <p>Reading progress: 45%</p>
              <span className="activity-time">1 day ago</span>
            </div>
          </div>
          <div className="activity-item">
            <img src="https://covers.openlibrary.org/b/id/8739161-M.jpg" alt="Recent book" className="activity-image" />
            <div className="activity-details">
              <h4>1984</h4>
              <p>Added to Dystopian category</p>
              <span className="activity-time">3 days ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
