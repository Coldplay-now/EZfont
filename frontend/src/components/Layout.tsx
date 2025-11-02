import { ReactNode } from 'react'
import Sidebar from './Sidebar'

interface LayoutProps {
  children: ReactNode
  showHeader?: boolean
  headerContent?: ReactNode
}

export default function Layout({ children, showHeader = false, headerContent }: LayoutProps) {
  return (
    <div className="relative flex min-h-screen w-full bg-[#f8f8f8]">
      <Sidebar />
      
      <div className="flex flex-col flex-1 ml-64 min-h-screen">
        {showHeader && (
          <header className="flex items-center justify-end whitespace-nowrap px-10 py-4 h-16 border-b border-gray-200 bg-white sticky top-0 left-64 right-0 z-30">
            {headerContent || (
              <div className="flex items-center gap-4">
                <div 
                  className="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 h-10" 
                  style={{
                    backgroundImage: 'url("https://ui-avatars.com/api/?name=User&background=1a1a1a&color=fff")'
                  }}
                />
              </div>
            )}
          </header>
        )}
        
        <main className={`flex flex-1 justify-center py-8 ${showHeader ? '' : 'pt-8'}`}>
          <div className="flex flex-col w-full max-w-7xl px-4 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

