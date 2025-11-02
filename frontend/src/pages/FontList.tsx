import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import FontCard from '@/components/FontCard'
import type { FontListItem } from '@/types'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

export default function FontList() {
  const navigate = useNavigate()
  const [fonts, setFonts] = useState<FontListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadFonts()
  }, [])

  const loadFonts = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/fonts`)
      
      if (response.data.code === 200) {
        setFonts(response.data.data.fonts)
      } else {
        setError(response.data.message || '加载字体列表失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载字体列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (fontId: string) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/fonts/${fontId}`)
      
      if (response.data.code === 200) {
        // 重新加载列表
        loadFonts()
      } else {
        alert(response.data.message || '删除失败')
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : '删除失败')
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
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadFonts}
            className="px-6 py-2 bg-[#1a1a1a] text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            重试
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout showHeader headerContent={headerContent}>
      {/* Page Header */}
      <div className="flex flex-wrap justify-between gap-4 items-center mb-8">
        <div className="flex flex-col gap-1">
          <h1 className="text-gray-900 text-3xl font-bold leading-tight tracking-[-0.02em]">
            My Font Creations
          </h1>
          <p className="text-gray-500 text-base font-normal leading-normal">
            Manage your previously generated fonts.
          </p>
        </div>
        <button
          onClick={() => navigate('/create')}
          className="flex items-center justify-center gap-2 rounded-xl h-11 px-5 bg-[#1a1a1a] text-white text-sm font-bold leading-normal tracking-[0.015em] hover:bg-gray-700 transition-colors"
        >
          <span className="material-symbols-outlined text-base">add</span>
          <span className="truncate">Create New Font</span>
        </button>
      </div>

      {/* Font Grid */}
      {fonts.length === 0 ? (
        <div className="text-center py-24">
          <div className="text-gray-400 mb-4">
            <span className="material-symbols-outlined text-6xl">font_download</span>
          </div>
          <p className="text-gray-500 mb-8">You haven't created any fonts yet.</p>
          <button
            onClick={() => navigate('/create')}
            className="px-8 py-3 bg-[#1a1a1a] text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            Create Your First Font
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {fonts.map((font) => (
            <FontCard key={font.font_id} font={font} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </Layout>
  )
}

