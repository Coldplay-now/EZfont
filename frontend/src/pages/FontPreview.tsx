import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '@/components/Layout'
import { fontApi } from '@/services/api'

export default function FontPreview() {
  const { fontId } = useParams<{ fontId: string }>()
  const [customText, setCustomText] = useState('The quick brown fox jumps over the lazy dog.')
  const [fontUrl, setFontUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fontSize, setFontSize] = useState(36)
  const [fontWeight, setFontWeight] = useState(400)
  const [letterSpacing, setLetterSpacing] = useState(0)
  const [lineHeight, setLineHeight] = useState(1.5)

  useEffect(() => {
    if (!fontId) return

    const loadFont = async () => {
      try {
        const downloadUrl = fontApi.getDownloadUrl(fontId)
        
        const fontFace = new FontFace('GeneratedFont', `url(${downloadUrl})`)
        await fontFace.load()
        document.fonts.add(fontFace)
        
        setFontUrl(downloadUrl)
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : '字体加载失败')
        setLoading(false)
      }
    }

    loadFont()
  }, [fontId])

  const handleDownload = () => {
    if (fontUrl) {
      window.open(fontUrl, '_blank')
    }
  }

  const headerContent = (
    <div className="flex items-center gap-4">
      <div 
        className="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 h-10" 
        style={{
          backgroundImage: 'url("https://ui-avatars.com/api/?name=User&background=1a1a1a&color=fff")'
        }}
      />
    </div>
  )

  if (loading) {
    return (
      <Layout showHeader headerContent={headerContent}>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-[#1a1a1a] border-t-transparent"></div>
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout showHeader headerContent={headerContent}>
        <div className="text-center py-16">
          <p className="text-gray-600 mb-8">{error}</p>
          <Link to="/" className="px-6 py-2 bg-[#1a1a1a] text-white rounded-lg hover:bg-gray-800 transition-colors">
            返回首页
          </Link>
        </div>
      </Layout>
    )
  }

  return (
    <Layout showHeader headerContent={headerContent}>
      <div className="grid w-full grid-cols-1 gap-8 lg:grid-cols-[1fr_400px]">
        {/* Left Side - Preview Cards */}
        <div className="flex flex-col gap-8">
          {/* Live Preview */}
          <div className="flex flex-col gap-6 p-6 bg-white border border-gray-200 rounded-xl">
            <div className="flex justify-between items-center">
              <h3 className="text-gray-900 text-lg font-semibold leading-tight">Live Preview</h3>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Font Size:</span>
                <select
                  value={fontSize}
                  onChange={(e) => setFontSize(parseInt(e.target.value))}
                  className="form-select w-24 rounded-lg border-gray-200 bg-gray-50 text-gray-800 focus:ring-[#1a1a1a]/50 focus:border-[#1a1a1a] text-sm py-1"
                >
                  <option value="24">24px</option>
                  <option value="36">36px</option>
                  <option value="48">48px</option>
                  <option value="72">72px</option>
                </select>
              </div>
            </div>
            <div className="flex flex-col gap-4 p-4 rounded-lg bg-gray-100 min-h-[200px]">
              <div className="flex-grow">
                <p
                  style={{
                    fontFamily: 'GeneratedFont, sans-serif',
                    fontSize: `${fontSize}px`,
                    fontWeight: fontWeight,
                    letterSpacing: `${letterSpacing}px`,
                    lineHeight: lineHeight,
                    color: '#111827',
                  }}
                  className="text-gray-800 leading-snug"
                >
                  {customText}
                </p>
              </div>
              <div className="relative">
                <input
                  type="text"
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  className="form-input w-full rounded-lg text-gray-800 focus:outline-0 focus:ring-2 focus:ring-[#1a1a1a]/50 border border-gray-300 bg-white focus:border-[#1a1a1a] placeholder:text-gray-400 p-3 text-base"
                  placeholder="Type custom text to preview..."
                />
              </div>
            </div>
          </div>

          {/* Uppercase */}
          <div className="flex flex-col gap-6 p-6 bg-white border border-gray-200 rounded-xl">
            <h3 className="text-gray-900 text-lg font-semibold leading-tight">Uppercase (A-Z)</h3>
            <div className="p-4 rounded-lg bg-gray-100">
              <p
                style={{
                  fontFamily: 'GeneratedFont, sans-serif',
                }}
                className="text-3xl text-gray-800 break-words leading-relaxed"
              >
                ABCDEFGHIJKLMNOPQRSTUVWXYZ
              </p>
            </div>
          </div>

          {/* Lowercase */}
          <div className="flex flex-col gap-6 p-6 bg-white border border-gray-200 rounded-xl">
            <h3 className="text-gray-900 text-lg font-semibold leading-tight">Lowercase (a-z)</h3>
            <div className="p-4 rounded-lg bg-gray-100">
              <p
                style={{
                  fontFamily: 'GeneratedFont, sans-serif',
                }}
                className="text-3xl text-gray-800 break-words leading-relaxed"
              >
                abcdefghijklmnopqrstuvwxyz
              </p>
            </div>
          </div>

          {/* Numerals & Punctuation */}
          <div className="flex flex-col gap-6 p-6 bg-white border border-gray-200 rounded-xl">
            <h3 className="text-gray-900 text-lg font-semibold leading-tight">
              Numerals &amp; Punctuation
            </h3>
            <div className="p-4 rounded-lg bg-gray-100">
              <p
                style={{
                  fontFamily: 'GeneratedFont, sans-serif',
                }}
                className="text-3xl text-gray-800 break-words leading-relaxed"
              >
                0123456789 . , : ; ! ? ( ) &amp;
              </p>
            </div>
          </div>
        </div>

        {/* Right Side - Adjustments */}
        <div className="sticky top-24 h-fit flex flex-col gap-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-gray-900 text-lg font-semibold leading-tight mb-4">
              Font Adjustments
            </h3>
            <div className="flex flex-col gap-6">
              {/* Weight */}
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-gray-700">Weight</label>
                  <span className="text-sm text-gray-500">{fontWeight}</span>
                </div>
                <input
                  type="range"
                  min="100"
                  max="900"
                  step="100"
                  value={fontWeight}
                  onChange={(e) => setFontWeight(parseInt(e.target.value))}
                  className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              {/* Spacing */}
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-gray-700">Spacing</label>
                  <span className="text-sm text-gray-500">{letterSpacing}</span>
                </div>
                <input
                  type="range"
                  min="-50"
                  max="50"
                  step="1"
                  value={letterSpacing}
                  onChange={(e) => setLetterSpacing(parseInt(e.target.value))}
                  className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              {/* Line Height */}
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-gray-700">Line Height</label>
                  <span className="text-sm text-gray-500">{lineHeight.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="3"
                  step="0.1"
                  value={lineHeight}
                  onChange={(e) => setLineHeight(parseFloat(e.target.value))}
                  className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Export Button */}
          <div className="px-0 py-2">
            <button
              onClick={handleDownload}
              className="w-full flex items-center justify-center gap-2 rounded-xl h-14 px-6 bg-[#1a1a1a] text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-gray-700 transition-colors"
            >
              <span className="material-symbols-outlined">download</span>
              <span className="truncate">Export Font</span>
            </button>
          </div>
        </div>
      </div>
    </Layout>
  )
}
