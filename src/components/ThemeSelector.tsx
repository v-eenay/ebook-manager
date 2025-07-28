import React from 'react'
import { useTheme, ThemeMode } from '../contexts/ThemeContext'
import './ThemeSelector.css'

const ThemeSelector: React.FC = () => {
  const { theme, setTheme } = useTheme()

  const themes: { mode: ThemeMode; label: string; icon: string }[] = [
    { mode: 'light', label: 'Light', icon: '☀️' },
    { mode: 'dark', label: 'Dark', icon: '🌙' },
    { mode: 'high-contrast', label: 'High Contrast', icon: '⚫' },
    { mode: 'night', label: 'Night', icon: '🌌' }
  ]

  return (
    <div className="theme-selector">
      <select 
        value={theme} 
        onChange={(e) => setTheme(e.target.value as ThemeMode)}
        className="theme-select"
      >
        {themes.map(({ mode, label, icon }) => (
          <option key={mode} value={mode}>
            {icon} {label}
          </option>
        ))}
      </select>
    </div>
  )
}

export default ThemeSelector
