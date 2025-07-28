import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import ViewBooks from './pages/ViewBooks'
import ViewCategories from './pages/ViewCategories'
import ViewFolders from './pages/ViewFolders'
import AddBook from './pages/AddBook'
import AddCategory from './pages/AddCategory'
import './styles/themes.css'
import './App.css'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="App">
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/books" element={<ViewBooks />} />
              <Route path="/categories" element={<ViewCategories />} />
              <Route path="/folders" element={<ViewFolders />} />
              <Route path="/add-book" element={<AddBook />} />
              <Route path="/add-category" element={<AddCategory />} />
            </Routes>
          </Layout>
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App
