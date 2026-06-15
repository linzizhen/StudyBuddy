import React from 'react'
import { cn } from '@/lib/utils'
import { Sidebar } from '@/components/Sidebar'
import { RightSidebar } from '@/components/RightSidebar'

export type PageType = 'dashboard' | 'pomodoro' | 'tasks' | 'diary' | 'buddy' | 'stats' | 'goal'

interface AppLayoutProps {
  children: React.ReactNode
  currentPage: PageType
  onNavigate: (page: PageType) => void
  isDark: boolean
  onToggleTheme: () => void
}

export function AppLayout({ 
  children, 
  currentPage, 
  onNavigate, 
  isDark, 
  onToggleTheme 
}: AppLayoutProps) {
  return (
    <div className={cn(
      "flex h-screen w-screen overflow-hidden",
      isDark ? "bg-slate-900" : "bg-slate-50"
    )}>
      {/* Left Sidebar - Fixed 240px */}
      <Sidebar 
        currentPage={currentPage}
        onNavigate={onNavigate}
        isDark={isDark}
        onToggleTheme={onToggleTheme}
      />

      {/* Main Content - Flexible */}
      <main className="flex-1 min-w-0 overflow-y-auto overflow-x-hidden">
        <div className="min-h-full">
          {children}
        </div>
      </main>

      {/* Right Sidebar - Fixed 320px */}
      <RightSidebar 
        currentPage={currentPage}
        isDark={isDark}
      />
    </div>
  )
}
