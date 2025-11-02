import { Link, useLocation } from 'react-router-dom'

export default function Sidebar() {
  const location = useLocation()

  const menuItems = [
    { path: '/', icon: 'folder_managed', label: 'My Fonts' },
    { path: '/create', icon: 'auto_fix_high', label: 'AI Generator' },
  ]

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <aside className="flex flex-col w-64 bg-white border-r border-gray-200 p-4 fixed h-screen z-40">
      {/* Logo */}
      <div className="flex items-center gap-3 px-3 py-2 mb-6">
        <div className="w-8 h-8 flex-shrink-0 text-[#1a1a1a]">
          <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
            <path 
              d="M24 0.757355L47.2426 24L24 47.2426L0.757355 24L24 0.757355ZM21 35.7574V12.2426L9.24264 24L21 35.7574Z" 
              fill="currentColor"
            />
          </svg>
        </div>
        <h2 className="text-xl font-bold leading-tight tracking-[-0.015em] text-gray-900 whitespace-nowrap">
          Font Factory AI
        </h2>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-2">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-3 py-2 text-sm font-semibold rounded-lg transition-colors ${
              isActive(item.path)
                ? 'text-white bg-[#1a1a1a]'
                : 'text-gray-600 hover:bg-gray-100 hover:text-[#1a1a1a]'
            }`}
          >
            <span className="material-symbols-outlined text-xl">{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  )
}

