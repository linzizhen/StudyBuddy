import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Timer,
  CheckSquare,
  BookOpen,
  MessageCircle,
  BarChart3,
  Target,
  Settings,
  Play,
  Moon,
  Sun
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { PageType } from '@/layouts/AppLayout'

interface SidebarProps {
  currentPage: string
  onNavigate: (page: PageType) => void
  isDark: boolean
  onToggleTheme: () => void
}

const navItems = [
  { icon: LayoutDashboard, label: '仪表盘', id: 'dashboard' as PageType },
  { icon: Timer, label: '番茄专注', id: 'pomodoro' as PageType },
  { icon: CheckSquare, label: '待办任务', id: 'tasks' as PageType },
  { icon: BookOpen, label: '学习日记', id: 'diary' as PageType },
  { icon: MessageCircle, label: '学习搭子', id: 'buddy' as PageType },
  { icon: BarChart3, label: '数据统计', id: 'stats' as PageType },
  { icon: Target, label: '考研目标', id: 'goal' as PageType },
]

export function Sidebar({ currentPage, onNavigate, isDark, onToggleTheme }: SidebarProps) {
  return (
    <aside className={cn(
      "w-[240px] h-screen flex flex-col border-r shrink-0",
      isDark ? "bg-slate-900 border-slate-700" : "bg-white border-slate-200"
    )}>
      {/* Logo & User Profile Section */}
      <div className={cn(
        "p-5 border-b",
        isDark ? "border-slate-700" : "border-slate-100"
      )}>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-500 flex items-center justify-center text-xl shadow-lg shadow-emerald-200">
            &#128218;
          </div>
          <div>
            <h1 className={cn("font-bold text-lg", isDark ? "text-white" : "text-slate-900")}>StudyPal</h1>
            <p className={cn("text-xs", isDark ? "text-slate-400" : "text-slate-500")}>学习伴侣</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-500 flex items-center justify-center text-lg text-white shadow-lg shadow-emerald-200">
              &#128150;
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white"></div>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className={cn("font-semibold text-sm", isDark ? "text-white" : "text-slate-900")}>戏精</span>
              <Badge variant="emerald" className="text-[10px] px-1.5 py-0">Lv.1</Badge>
            </div>
            <p className={cn("text-xs truncate", isDark ? "text-slate-400" : "text-slate-500")}>休息中~</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = currentPage === item.id
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                isActive
                  ? isDark
                    ? "bg-emerald-900/50 text-emerald-400"
                    : "bg-emerald-50 text-emerald-600"
                  : isDark
                    ? "text-slate-300 hover:bg-slate-800 hover:text-white"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              )}
            >
              <item.icon className={cn(
                "w-5 h-5",
                isActive ? "text-emerald-500" : isDark ? "text-slate-400" : "text-slate-400"
              )} />
              {item.label}
            </button>
          )
        })}
      </nav>

      {/* Quick Pomodoro Button */}
      <div className={cn(
        "p-4 border-t",
        isDark ? "border-slate-700" : "border-slate-100"
      )}>
        <Button 
          className="w-full gap-2 h-10 shadow-lg shadow-emerald-200"
          onClick={() => onNavigate('pomodoro')}
        >
          <Play className="w-4 h-4" />
          一键番茄
        </Button>
        
        <div className="flex gap-2 mt-3">
          <button 
            onClick={onToggleTheme}
            className={cn(
              "flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg border text-xs transition-colors",
              isDark
                ? "border-slate-600 text-slate-300 hover:bg-slate-800"
                : "border-slate-200 text-slate-600 hover:bg-slate-50"
            )}
          >
            {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
            {isDark ? '浅色' : '深色'}
          </button>
          <button className={cn(
            "flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg border text-xs transition-colors",
            isDark
              ? "border-slate-600 text-slate-300 hover:bg-slate-800"
              : "border-slate-200 text-slate-600 hover:bg-slate-50"
          )}>
            <Settings className="w-3.5 h-3.5" />
            设置
          </button>
        </div>
      </div>
    </aside>
  )
}
