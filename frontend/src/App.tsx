import { useState, useEffect, useMemo, useRef } from 'react'
import './App.css'

interface LineData {
  id: string
  line_index: number
  bbox: [number, number, number, number]
  relative_bbox: [number, number, number, number]
  text: string
  label: string
}

interface ColumnData {
  id: string
  source_scan: string
  column_index: number
  bbox: [number, number, number, number]
  width: number
  height: number
  lines: LineData[]
}

interface SearchMatch {
  columnId: string
  columnIndex: number // index in columns array
  lineId: string
  lineIndex: number // line index in lines array
}

function App() {
  const [columns, setColumns] = useState<ColumnData[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  
  const [currentColIdx, setCurrentColIdx] = useState<number>(0)
  const [hoveredLineId, setHoveredLineId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState<string>('')
  
  // Ref to the active line card for scrolling into view
  const activeCardRef = useRef<HTMLDivElement | null>(null)
  
  // Load data
  useEffect(() => {
    fetch('/ocr_data.json')
      .then(res => {
        if (!res.ok) {
          throw new Error('Failed to load OCR data')
        }
        return res.json()
      })
      .then((data: ColumnData[]) => {
        setColumns(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Find all matches across all columns
  const searchMatches = useMemo<SearchMatch[]>(() => {
    if (!searchQuery.trim()) return []
    const term = searchQuery.toLowerCase()
    const matches: SearchMatch[] = []
    
    columns.forEach((col, colIdx) => {
      col.lines.forEach((line, lineIdx) => {
        if (
          line.text.toLowerCase().includes(term) ||
          line.label.toLowerCase().includes(term)
        ) {
          matches.push({
            columnId: col.id,
            columnIndex: colIdx,
            lineId: line.id,
            lineIndex: lineIdx
          })
        }
      })
    })
    
    return matches
  }, [columns, searchQuery])

  // Track active match index in searchMatches
  const [activeMatchIdx, setActiveMatchIndex] = useState<number>(-1)

  // Reset active match when search query changes
  useEffect(() => {
    if (searchMatches.length > 0) {
      setActiveMatchIndex(0)
      // Switch view to the first matching column
      setCurrentColIdx(searchMatches[0].columnIndex)
    } else {
      setActiveMatchIndex(-1)
    }
  }, [searchMatches])

  // Get current active column
  const currentCol = columns[currentColIdx]

  // Synchronize view when active match changes
  useEffect(() => {
    if (activeMatchIdx >= 0 && activeMatchIdx < searchMatches.length) {
      const match = searchMatches[activeMatchIdx]
      setCurrentColIdx(match.columnIndex)
      setHoveredLineId(match.lineId)
    }
  }, [activeMatchIdx, searchMatches])

  // Scroll active card into view
  useEffect(() => {
    if (hoveredLineId && activeCardRef.current) {
      activeCardRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
      })
    }
  }, [hoveredLineId])

  // Navigation handlers
  const handleNext = () => {
    if (searchMatches.length === 0) return
    setActiveMatchIndex(prev => (prev + 1) % searchMatches.length)
  }

  const handleBack = () => {
    if (searchMatches.length === 0) return
    setActiveMatchIndex(prev => (prev - 1 + searchMatches.length) % searchMatches.length)
  }

  const handleColumnChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const idx = parseInt(e.target.value, 10)
    if (idx >= 0 && idx < columns.length) {
      setCurrentColIdx(idx)
      setHoveredLineId(null)
    }
  }

  if (loading) {
    return (
      <div className="container" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <h1>Loading OCR Browser...</h1>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <h1>Error</h1>
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="title-row">
          <h1>Cherokee Phoenix OCR Column Browser</h1>
          <div className="meta-info">
            {columns.length} columns loaded | {currentCol ? currentCol.lines.length : 0} lines in current column
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <main className="main-layout">
        
        {/* Left Column: Column Scan Viewer */}
        <section className="column-left">
          {currentCol ? (
            <div 
              className="scan-wrapper"
              style={{
                width: `${currentCol.width * 0.4}px`, // scaled down slightly for browser view
                height: `${currentCol.height * 0.4}px`,
                position: 'relative'
              }}
            >
              {/* Represent scanned text dynamically using high fidelity borders and clean serif rendering */}
              <div 
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundColor: '#ffffff',
                  backgroundImage: 'radial-gradient(#dddddd 1px, transparent 1px)',
                  backgroundSize: '16px 16px',
                  opacity: 0.8
                }}
              />
              
              {currentCol.lines.map((line) => {
                const [lx1, ly1, lx2, ly2] = line.relative_bbox
                const width = (lx2 - lx1) * 0.4
                const height = (ly2 - ly1) * 0.4
                const left = lx1 * 0.4
                const top = ly1 * 0.4
                const isHovered = hoveredLineId === line.id
                
                // Highlight search matches on scan
                const isSearchMatch = searchMatches.some(m => m.lineId === line.id)
                const isActiveSearchMatch = activeMatchIdx >= 0 && searchMatches[activeMatchIdx]?.lineId === line.id

                let borderStyle = '1px dashed #cccccc'
                if (isActiveSearchMatch) {
                  borderStyle = '2.5px solid var(--active-highlight)'
                } else if (isHovered) {
                  borderStyle = '2px solid var(--active-highlight)'
                } else if (isSearchMatch) {
                  borderStyle = '1.5px solid #000000'
                }

                return (
                  <div
                    key={line.id}
                    className={`scan-line-bbox ${isHovered ? 'active' : ''}`}
                    style={{
                      left: `${left}px`,
                      top: `${top}px`,
                      width: `${width}px`,
                      height: `${height}px`,
                      border: borderStyle,
                      backgroundColor: isActiveSearchMatch 
                        ? 'rgba(0, 0, 0, 0.1)' 
                        : isHovered 
                        ? 'rgba(0, 0, 0, 0.04)' 
                        : isSearchMatch 
                        ? 'rgba(0, 0, 0, 0.02)' 
                        : 'transparent'
                    }}
                    onMouseEnter={() => setHoveredLineId(line.id)}
                    onMouseLeave={() => setHoveredLineId(null)}
                  >
                    <span 
                      className="scan-line-text"
                      style={{ 
                        fontSize: `${height * 0.55}px`,
                        fontFamily: 'Georgia, serif',
                        opacity: 0.8
                      }}
                    >
                      {line.text.slice(0, 15)}...
                    </span>
                  </div>
                )
              })}
            </div>
          ) : (
            <p>No column selected</p>
          )}
        </section>

        {/* Vertical Divider Line */}
        <div className="column-divider" />

        {/* Right Column: Controls, Search, Transcription */}
        <section className="column-right">
          
          {/* Column Selector */}
          <div className="selector-box">
            <span>Column:</span>
            <select 
              className="select-dropdown" 
              value={currentColIdx} 
              onChange={handleColumnChange}
              disabled={searchQuery.trim().length > 0}
            >
              {columns.map((col, idx) => (
                <option key={col.id} value={idx}>
                  {col.source_scan.split('/')[1] || col.source_scan} (Col {col.column_index})
                </option>
              ))}
            </select>
            {searchQuery.trim().length > 0 && (
              <span style={{ fontSize: '0.8rem', fontStyle: 'italic', marginLeft: 'auto' }}>
                Dropdown disabled during search
              </span>
            )}
          </div>

          {/* Search Controls Box */}
          <div className="search-controls-box">
            <h2>Search Transcription</h2>
            <div className="search-input-group">
              <input
                type="text"
                className="search-input"
                placeholder="Search Cherokee characters or IDs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              
              {/* Back Button */}
              <button
                className="button-icon-only"
                onClick={handleBack}
                disabled={searchMatches.length <= 1}
                title="Previous Match"
              >
                {/* Simple Left Arrow Icon */}
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="19" y1="12" x2="5" y2="12"></line>
                  <polyline points="12 19 5 12 12 5"></polyline>
                </svg>
              </button>

              {/* Next Button */}
              <button
                className="button-icon-only"
                onClick={handleNext}
                disabled={searchMatches.length <= 1}
                title="Next Match"
              >
                {/* Simple Right Arrow Icon */}
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </button>

              {/* Clear Search Button */}
              {searchQuery && (
                <button
                  className="button-icon-only"
                  onClick={() => setSearchQuery('')}
                  title="Clear Search"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              )}
            </div>

            <div className="results-summary-row">
              {searchQuery.trim() ? (
                <>
                  <span>
                    Found <strong>{searchMatches.length}</strong> {searchMatches.length === 1 ? 'match' : 'matches'}
                  </span>
                  {searchMatches.length > 0 && (
                    <span>
                      Match <strong>{activeMatchIdx + 1}</strong> of <strong>{searchMatches.length}</strong>
                    </span>
                  )}
                </>
              ) : (
                <span style={{ color: 'var(--text-secondary)' }}>Enter search term to locate across columns</span>
              )}
            </div>
          </div>

          {/* Transcription List */}
          <div className="transcription-list">
            {currentCol?.lines.map((line) => {
              const isHovered = hoveredLineId === line.id
              const isMatch = searchMatches.some(m => m.lineId === line.id)
              const isActiveMatch = activeMatchIdx >= 0 && searchMatches[activeMatchIdx]?.lineId === line.id

              return (
                <div
                  key={line.id}
                  ref={isActiveMatch || isHovered ? activeCardRef : null}
                  className={`transcription-card ${isHovered ? 'active' : ''} ${isMatch ? 'search-match' : ''} ${isActiveMatch ? 'active-match' : ''}`}
                  onMouseEnter={() => setHoveredLineId(line.id)}
                  onMouseLeave={() => setHoveredLineId(null)}
                >
                  <div className="card-header">
                    <span>Line {line.line_index}</span>
                    <span>BBox: {JSON.stringify(line.bbox)}</span>
                  </div>
                  <div className="card-text">
                    {line.text || <em style={{ opacity: 0.5 }}>Unrecognized/Blank</em>}
                  </div>
                  {line.label && (
                    <div className="card-label">
                      GT: {line.label}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

        </section>

      </main>
    </div>
  )
}

export default App
