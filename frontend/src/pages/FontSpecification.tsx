import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '@/components/Layout'
import axios from 'axios'
import type { FontWithSpec } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

export default function FontSpecification() {
  const { fontId } = useParams<{ fontId: string }>()
  const [fontData, setFontData] = useState<FontWithSpec | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [previewText, setPreviewText] = useState('The quick brown fox jumps over the lazy dog.')
  const [previewSize, setPreviewSize] = useState(36)

  useEffect(() => {
    if (!fontId) return
    loadFontData()
  }, [fontId])

  const loadFontData = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/fonts/${fontId}`)
      
      if (response.data.code === 200) {
        setFontData(response.data.data)
      } else {
        setError(response.data.message || '加载字体详情失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载字体详情失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    window.open(`${API_BASE_URL}/font/${fontId}/download`, '_blank')
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

  if (error || !fontData) {
    return (
      <Layout showHeader headerContent={headerContent}>
        <div className="text-center py-16">
          <p className="text-gray-600 mb-8">{error || '字体不存在'}</p>
          <Link to="/" className="px-6 py-2 bg-[#1a1a1a] text-white rounded-lg hover:bg-gray-800 transition-colors">
            返回列表
          </Link>
        </div>
      </Layout>
    )
  }

  const spec = fontData.spec
  const { basicInfo, designParameters, styleDefinition, technicalSpecs } = spec

  return (
    <Layout showHeader headerContent={headerContent}>
      {/* Page Header */}
      <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div className="flex flex-col gap-2">
          <p className="text-4xl font-bold leading-tight tracking-[-0.03em] text-gray-900">
            Font Specification: {fontData.font_name}
          </p>
          <p className="text-lg font-normal leading-normal text-gray-500">
            Generated based on your design prompt and parameters.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to={`/fonts/${fontId}/preview`}
            className="flex h-11 items-center justify-center gap-2 rounded-lg border border-gray-200 bg-white px-5 text-sm font-semibold leading-normal text-gray-700 transition-colors hover:bg-gray-100"
          >
            <span className="material-symbols-outlined text-base">edit</span>
            <span className="truncate">Edit</span>
          </Link>
          <button
            onClick={handleDownload}
            disabled={fontData.status !== 'completed'}
            className="flex h-11 items-center justify-center gap-2 rounded-lg bg-[#1a1a1a] px-5 text-sm font-semibold leading-normal tracking-[0.015em] text-white transition-colors hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined text-base">download</span>
            <span className="truncate">Download Font</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 gap-10 lg:grid-cols-[1fr_420px]">
        {/* Left Side - Specifications */}
        <div className="flex flex-col gap-8">
          {/* Basic Information */}
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h3 className="mb-4 text-lg font-semibold leading-tight text-gray-900">
              Basic Information
            </h3>
            <div className="grid grid-cols-2 gap-x-6 gap-y-4 text-sm md:grid-cols-3">
              <div>
                <dt className="text-gray-500">Font Name</dt>
                <dd className="mt-1 font-medium text-gray-800">{basicInfo.fontName}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Version</dt>
                <dd className="mt-1 font-medium text-gray-800">{basicInfo.version}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Format</dt>
                <dd className="mt-1 font-medium text-gray-800">
                  {technicalSpecs.format.join(', ')}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">Style</dt>
                <dd className="mt-1 font-medium text-gray-800 capitalize">{basicInfo.style}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Creation Date</dt>
                <dd className="mt-1 font-medium text-gray-800">
                  {new Date(fontData.created_at).toLocaleDateString()}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">Category</dt>
                <dd className="mt-1 font-medium text-gray-800 capitalize">{basicInfo.category}</dd>
              </div>
            </div>
          </div>

          {/* Design Parameters */}
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h3 className="mb-4 text-lg font-semibold leading-tight text-gray-900">
              Design Parameters
            </h3>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
              {/* Metrics */}
              <div className="space-y-4">
                <h4 className="text-base font-semibold text-gray-800">Metrics</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Ascender</span>
                    <span className="font-medium text-gray-800">
                      {designParameters.metrics.ascender}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Descender</span>
                    <span className="font-medium text-gray-800">
                      {designParameters.metrics.descender}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Cap Height</span>
                    <span className="font-medium text-gray-800">
                      {designParameters.metrics.capHeight}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">x-Height</span>
                    <span className="font-medium text-gray-800">
                      {designParameters.metrics.xHeight}
                    </span>
                  </div>
                </div>
              </div>

              {/* Spacing */}
              <div className="space-y-4">
                <h4 className="text-base font-semibold text-gray-800">Spacing</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Tracking</span>
                    <span className="font-medium text-gray-800">
                      {designParameters.spacing.tracking || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Kerning</span>
                    <span className="font-medium text-gray-800">
                      {designParameters.spacing.kerning ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Word Space</span>
                    <span className="font-medium text-gray-800">
                      {designParameters.spacing.wordSpacing}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Letter Spacing</span>
                    <span className="font-medium text-gray-800">
                      {designParameters.spacing.letterSpacing}
                    </span>
                  </div>
                </div>
              </div>

              {/* Proportions */}
              <div className="space-y-4">
                <h4 className="text-base font-semibold text-gray-800">Proportions</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Weight</span>
                    <span className="font-medium text-gray-800 capitalize">
                      {basicInfo.weight}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Contrast</span>
                    <span className="font-medium text-gray-800 capitalize">
                      {designParameters.proportions.contrast}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Width</span>
                    <span className="font-medium text-gray-800 capitalize">
                      {designParameters.proportions.aspectRatio}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Stroke</span>
                    <span className="font-medium text-gray-800">
                      {designParameters.proportions.strokeWidth}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Style Definition */}
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h3 className="mb-4 text-lg font-semibold leading-tight text-gray-900">
              Style Definition
            </h3>
            <div className="flex flex-wrap gap-2">
              {styleDefinition.characteristics.map((char: string, idx: number) => (
                <span
                  key={idx}
                  className="rounded-full bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700"
                >
                  {char}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Right Side - Preview */}
        <div className="sticky top-24 flex h-fit flex-col gap-6">
          {/* Live Preview */}
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold leading-tight text-gray-900">Live Preview</h3>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Size:</span>
                <select
                  value={previewSize}
                  onChange={(e) => setPreviewSize(parseInt(e.target.value))}
                  className="form-select w-24 rounded-lg border-gray-200 bg-gray-50 py-1 text-sm text-gray-800 focus:border-[#1a1a1a] focus:ring-[#1a1a1a]/50"
                >
                  <option value="24">24px</option>
                  <option value="36">36px</option>
                  <option value="48">48px</option>
                  <option value="72">72px</option>
                </select>
              </div>
            </div>
            <div className="mt-4 flex min-h-[160px] flex-col gap-4 rounded-lg bg-gray-100 p-4">
              <div className="flex-grow">
                <p
                  className="leading-snug text-gray-800"
                  style={{ fontSize: `${previewSize}px` }}
                >
                  {previewText}
                </p>
              </div>
              <div className="relative">
                <input
                  type="text"
                  value={previewText}
                  onChange={(e) => setPreviewText(e.target.value)}
                  className="form-input w-full rounded-lg border border-gray-300 bg-white p-3 text-base text-gray-800 placeholder:text-gray-400 focus:border-[#1a1a1a] focus:outline-0 focus:ring-2 focus:ring-[#1a1a1a]/50"
                  placeholder="Type custom text to preview..."
                />
              </div>
            </div>
          </div>

          {/* Character Set */}
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h3 className="mb-4 text-lg font-semibold leading-tight text-gray-900">
              Character Set
            </h3>
            <div className="break-words rounded-lg bg-gray-100 p-4 text-2xl leading-relaxed tracking-wider text-gray-800">
              ABCDEFGHIJKLMNOPQRSTUVWXYZ
              <br />
              abcdefghijklmnopqrstuvwxyz
              <br />
              0123456789 .,!?;:'"()-
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

