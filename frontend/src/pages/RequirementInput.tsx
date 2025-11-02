import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import { fontApi } from '@/services/api'
import type { UserRequirement, FontDesignSpec } from '@/types'

export default function RequirementInput() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [previewText, setPreviewText] = useState('The quick brown fox jumps over the lazy dog')
  const [previewSize, setPreviewSize] = useState(36)
  
  const [fontWeightValue, setFontWeightValue] = useState(400) // 100-900
  
  const [requirement, setRequirement] = useState<UserRequirement>({
    textDescription: '',
    fontType: 'sans-serif',
    fontWeight: 'normal',
    characterSet: {
      uppercase: true,
      lowercase: true,
      numbers: true,
      punctuation: true,
    },
  })

  const handleSubmit = async (e?: React.FormEvent | React.MouseEvent) => {
    if (e) e.preventDefault()
    
    // 验证输入
    if (requirement.textDescription.length < 10) {
      setError('描述长度必须至少10个字符')
      return
    }
    
    setError(null)
    setLoading(true)
    
    console.log('开始生成字体...', requirement)

    try {
      if (requirement.textDescription.length < 10 || requirement.textDescription.length > 500) {
        throw new Error('描述长度必须在10-500字符之间')
      }

      const analyzeResponse = await fontApi.analyzeRequirements(requirement)
      
      if (analyzeResponse.code !== 200) {
        throw new Error(analyzeResponse.message || '需求分析失败')
      }

      const designSpec = analyzeResponse.data as FontDesignSpec

      const generateResponse = await fontApi.generateFont(designSpec)
      
      if (generateResponse.code !== 200) {
        throw new Error(generateResponse.message || '字体生成失败')
      }

      // 跳转到规格详情页
      navigate(`/fonts/${generateResponse.data.fontId}/spec`)
    } catch (err) {
      console.error('字体生成失败:', err)
      const errorMessage = err instanceof Error ? err.message : '发生未知错误'
      setError(errorMessage)
    } finally {
      setLoading(false)
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

  return (
    <Layout showHeader headerContent={headerContent}>
      {/* Title */}
      <div className="flex flex-wrap justify-between gap-3 p-4 mb-8 text-center w-full max-w-3xl mx-auto">
        <div className="flex w-full flex-col gap-4">
          <p className="text-gray-900 text-5xl font-bold leading-tight tracking-[-0.03em]">
            Create Your Exclusive Font
          </p>
          <p className="text-gray-500 text-lg font-normal leading-normal">
            Describe your ideal font, and let our AI bring it to life.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_420px] gap-10">
        {/* Left Side - Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-8">
          {/* Description */}
          <div className="flex flex-col gap-3">
            <h3 className="text-gray-900 text-lg font-semibold leading-tight">
              1. Describe your font style
            </h3>
            <textarea
              rows={6}
              value={requirement.textDescription}
              onChange={(e) => setRequirement({ ...requirement, textDescription: e.target.value })}
              className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-gray-900 focus:outline-0 focus:ring-2 focus:ring-[#1a1a1a]/50 border border-gray-200 bg-white focus:border-[#1a1a1a] min-h-36 placeholder:text-gray-400 p-[15px] text-base font-normal leading-normal"
              placeholder="e.g. 'A retro handwritten script font with a slightly playful feel'"
              required
            />
          </div>

          {/* Font Type */}
          <div className="flex flex-col gap-3">
            <h3 className="text-gray-900 text-lg font-semibold leading-tight">
              2. Select font type
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { type: 'serif', label: 'Serif' },
                { type: 'sans-serif', label: 'Sans-serif' },
                { type: 'monospace', label: 'Monospace' },
              ].map(({ type, label }) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setRequirement({ ...requirement, fontType: type as any })}
                  className={`flex items-center justify-center rounded-lg py-3 px-4 text-sm font-semibold transition-colors border ${
                    requirement.fontType === type
                      ? 'bg-[#1a1a1a] text-white border-[#1a1a1a]'
                      : 'bg-white text-gray-700 hover:bg-gray-100 border-gray-200'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Font Weight - 使用滑块 */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h3 className="text-gray-900 text-lg font-semibold leading-tight">
                3. Select font weight
              </h3>
              <span className="text-sm font-semibold text-[#1a1a1a] bg-gray-100 px-3 py-1 rounded-lg">
                {fontWeightValue}
              </span>
            </div>
            <div className="flex flex-col gap-2 pt-2">
              <input
                type="range"
                min="100"
                max="900"
                step="100"
                value={fontWeightValue}
                onChange={(e) => {
                  const value = parseInt(e.target.value)
                  setFontWeightValue(value)
                  setRequirement({
                    ...requirement,
                    fontWeight: value >= 600 ? 'bold' : 'normal'
                  })
                }}
                className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 pt-1">
                <span>Thin</span>
                <span>Regular</span>
                <span>Medium</span>
                <span>Bold</span>
                <span>Black</span>
              </div>
            </div>
          </div>

          {/* Character Set */}
          <div className="flex flex-col gap-3">
            <h3 className="text-gray-900 text-lg font-semibold leading-tight">
              4. Select character set
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {[
                { key: 'uppercase', label: 'Basic Latin' },
                { key: 'punctuation', label: 'Punctuation' },
                { key: 'numbers', label: 'Currency Symbols' },
              ].map(({ key, label }) => (
                <label
                  key={key}
                  className="flex items-center gap-2 p-3 rounded-lg bg-white border border-gray-200 cursor-pointer has-[:checked]:bg-[#1a1a1a]/5 has-[:checked]:ring-1 has-[:checked]:ring-[#1a1a1a] has-[:checked]:border-[#1a1a1a] transition-all"
                >
                  <input
                    type="checkbox"
                    checked={requirement.characterSet[key as keyof typeof requirement.characterSet]}
                    onChange={(e) =>
                      setRequirement({
                        ...requirement,
                        characterSet: {
                          ...requirement.characterSet,
                          [key]: e.target.checked,
                        },
                      })
                    }
                    className="form-checkbox rounded border-gray-400 text-[#1a1a1a] focus:ring-[#1a1a1a]/50 bg-transparent"
                  />
                  <span className="text-sm font-medium text-gray-700">{label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="py-4 px-6 bg-red-50 border border-red-200 text-sm text-red-900 rounded-lg">
              {error}
            </div>
          )}
        </form>

        {/* Right Side - Preview */}
        <div className="sticky top-28 h-fit flex flex-col gap-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex justify-between items-center">
              <h3 className="text-gray-900 text-lg font-semibold leading-tight">Live Preview</h3>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Size:</span>
                <select
                  value={previewSize}
                  onChange={(e) => setPreviewSize(parseInt(e.target.value))}
                  className="form-select w-24 rounded-lg border-gray-200 bg-gray-50 text-gray-800 focus:ring-[#1a1a1a]/50 focus:border-[#1a1a1a] text-sm py-1"
                >
                  <option value="24">24px</option>
                  <option value="36">36px</option>
                  <option value="48">48px</option>
                  <option value="72">72px</option>
                </select>
              </div>
            </div>
            <div className="flex flex-col gap-4 p-4 mt-4 rounded-lg bg-gray-100 min-h-[200px]">
              <div className="flex-grow">
                <p
                  className="leading-snug text-gray-800"
                  style={{ 
                    fontSize: `${previewSize}px`,
                    fontWeight: fontWeightValue 
                  }}
                >
                  {previewText}
                </p>
              </div>
              <div className="relative">
                <input
                  type="text"
                  value={previewText}
                  onChange={(e) => setPreviewText(e.target.value)}
                  className="form-input w-full rounded-lg text-gray-800 focus:outline-0 focus:ring-2 focus:ring-[#1a1a1a]/50 border border-gray-300 bg-white focus:border-[#1a1a1a] placeholder:text-gray-400 p-3 text-base"
                  placeholder="Type custom text to preview..."
                />
              </div>
            </div>
            
            {/* Loading State */}
            {loading && (
              <div className="flex flex-col items-center justify-center gap-3 p-8 border-2 border-dashed border-transparent rounded-lg text-center bg-transparent mt-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#1a1a1a]"></div>
                <p className="text-sm font-medium text-gray-500">Generating your font...</p>
                <p className="text-xs text-gray-400">This might take a moment, the preview will update live.</p>
              </div>
            )}
          </div>
          
          {/* Generate Button */}
          <div className="px-0 py-2">
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading || requirement.textDescription.length < 10}
              className="w-full flex items-center justify-center gap-2 rounded-xl h-14 px-6 bg-[#1a1a1a] text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-gray-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  <span className="truncate">Generating...</span>
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined">auto_awesome</span>
                  <span className="truncate">Generate My Font</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </Layout>
  )
}
