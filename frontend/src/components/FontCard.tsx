import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import type { FontListItem } from '@/types'

interface FontCardProps {
  font: FontListItem
  onDelete?: (fontId: string) => void
}

const PREVIEW_TEXTS = [
  'Sphinx of black quartz, judge my vow.',
  'Grumpy wizards make toxic brew.',
  'The quick brown fox jumps over the lazy dog.',
]

export default function FontCard({ font, onDelete }: FontCardProps) {
  // 使用稳定的随机选择（基于fontId）
  const textIndex = parseInt(font.font_id.split('_')[1] || '0') % PREVIEW_TEXTS.length
  const previewText = PREVIEW_TEXTS[textIndex]
  const [fontLoaded, setFontLoaded] = useState(false)
  const fontFamily = `Font_${font.font_id}`

  useEffect(() => {
    // 加载字体文件
    const loadFont = async () => {
      try {
        const downloadUrl = `/api/font/${font.font_id}/download`
        const fontFace = new FontFace(fontFamily, `url(${downloadUrl})`)
        await fontFace.load()
        document.fonts.add(fontFace)
        setFontLoaded(true)
      } catch (err) {
        console.error('字体加载失败:', err)
        // 即使加载失败也继续显示（用系统字体）
        setFontLoaded(true)
      }
    }

    if (font.status === 'completed') {
      loadFont()
    }
  }, [font.font_id, font.status, fontFamily])

  const handleDownload = () => {
    window.open(`/api/font/${font.font_id}/download`, '_blank')
  }

  const handleDelete = () => {
    if (window.confirm('确定要删除这个字体吗？')) {
      onDelete?.(font.font_id)
    }
  }

  return (
    <div className="flex flex-col gap-4 p-5 bg-white rounded-xl border border-gray-200">
      {/* Preview Area */}
      <div className="bg-gray-100 rounded-lg p-4 h-48 flex items-center justify-center">
        {font.status === 'completed' ? (
          <p 
            className="text-4xl leading-snug text-gray-800 break-all text-center"
            style={{ 
              fontFamily: fontLoaded ? `${fontFamily}, sans-serif` : 'sans-serif',
              opacity: fontLoaded ? 1 : 0.5
            }}
          >
            {previewText}
          </p>
        ) : (
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-[#1a1a1a] border-t-transparent mx-auto mb-2"></div>
            <p className="text-sm text-gray-500">Generating...</p>
          </div>
        )}
      </div>

      {/* Info and Actions */}
      <div className="flex flex-col gap-3">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{font.font_name}</h3>
            <p className="text-sm text-gray-500">
              Created on {new Date(font.created_at).toLocaleDateString()}
            </p>
          </div>
          
          {/* More Menu */}
          <div className="relative group">
            <button className="p-2 text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-full transition-colors">
              <span className="material-symbols-outlined">more_horiz</span>
            </button>
            <div className="absolute right-0 mt-1 w-36 bg-white border border-gray-200 rounded-lg shadow-lg z-10 opacity-0 group-hover:opacity-100 invisible group-hover:visible transition-all duration-200 transform-gpu scale-95 group-hover:scale-100">
              <Link
                to={`/fonts/${font.font_id}/spec`}
                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                View Spec
              </Link>
              <button
                onClick={handleDelete}
                className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <button
            onClick={handleDownload}
            disabled={font.status !== 'completed'}
            className="w-full flex items-center justify-center gap-2 rounded-lg h-10 px-4 bg-white text-[#1a1a1a] text-sm font-semibold border border-gray-200 hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined text-base">download</span>
            <span>Download</span>
          </button>
          <Link
            to={`/fonts/${font.font_id}/preview`}
            className="w-full flex items-center justify-center gap-2 rounded-lg h-10 px-4 bg-[#1a1a1a] text-white text-sm font-semibold hover:bg-gray-700 transition-colors"
          >
            <span className="material-symbols-outlined text-base">visibility</span>
            <span>Preview</span>
          </Link>
        </div>

        {/* Status Badge */}
        {font.status !== 'completed' && (
          <div className={`text-xs text-center py-1 rounded ${
            font.status === 'generating' 
              ? 'bg-blue-100 text-blue-700' 
              : 'bg-red-100 text-red-700'
          }`}>
            {font.status === 'generating' ? 'Generating...' : 'Failed'}
          </div>
        )}
      </div>
    </div>
  )
}

