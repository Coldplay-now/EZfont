import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import FontList from './pages/FontList'
import RequirementInput from './pages/RequirementInput'
import FontSpecification from './pages/FontSpecification'
import FontPreview from './pages/FontPreview'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<FontList />} />
        <Route path="/create" element={<RequirementInput />} />
        <Route path="/fonts/:fontId/spec" element={<FontSpecification />} />
        <Route path="/fonts/:fontId/preview" element={<FontPreview />} />
      </Routes>
    </Router>
  )
}

export default App
