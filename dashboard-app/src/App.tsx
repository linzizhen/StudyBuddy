import React from 'react'
import { AppLayout, PageType } from '@/layouts/AppLayout'
import { Dashboard } from '@/components/Dashboard'
import { PomodoroPage } from '@/components/PomodoroPage'
import { TasksPage } from '@/components/TasksPage'
import { DiaryPage } from '@/components/DiaryPage'
import { BuddyPage } from '@/components/BuddyPage'
import { StatsPage } from '@/components/StatsPage'
import { GoalPage } from '@/components/GoalPage'

function App() {
  const [currentPage, setCurrentPage] = React.useState<PageType>('dashboard')
  const [isDark, setIsDark] = React.useState(false)

  const renderPage = () => {
    switch (currentPage) {
      case 'pomodoro':
        return <PomodoroPage isDark={isDark} />
      case 'tasks':
        return <TasksPage isDark={isDark} />
      case 'diary':
        return <DiaryPage isDark={isDark} />
      case 'buddy':
        return <BuddyPage isDark={isDark} />
      case 'stats':
        return <StatsPage isDark={isDark} />
      case 'goal':
        return <GoalPage isDark={isDark} />
      default:
        return <Dashboard isDark={isDark} />
    }
  }

  return (
    <AppLayout
      currentPage={currentPage}
      onNavigate={setCurrentPage}
      isDark={isDark}
      onToggleTheme={() => setIsDark(!isDark)}
    >
      <div className="animate-fadeIn">
        {renderPage()}
      </div>
    </AppLayout>
  )
}

export default App
