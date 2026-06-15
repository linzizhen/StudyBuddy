import React from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  MessageCircle,
  BookOpen,
  CheckSquare,
  TrendingUp,
  Clock,
  Cherry,
  ArrowRight,
  GraduationCap,
  Calendar,
  Users
} from 'lucide-react'

interface DashboardProps {
  isDark?: boolean
}

export function Dashboard({ isDark = false }: DashboardProps) {
  const [searchQuery, setSearchQuery] = React.useState('')

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return '早上好'
    if (hour < 18) return '下午好'
    return '晚上好'
  }

  return (
    <div className="p-6">
      {/* Header Row */}
      <div className="flex items-center justify-between mb-6">
        <h1 className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>
          {getGreeting()}，学习战士
        </h1>
        <Button className="gap-2 shadow-lg shadow-emerald-200">
          <Cherry className="w-4 h-4" />
          开始学习
        </Button>
      </div>

      {/* Search Input */}
      <Input
        placeholder="今天想学点什么？"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className={cn(
          "h-12 text-base mb-6",
          isDark && "bg-slate-800 border-slate-700 text-white placeholder:text-slate-400"
        )}
      />

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-4">
        {/* Row 1: Stats Cards */}
        <Card className={cn("col-span-3 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
              <Clock className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <p className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>2.5</p>
              <p className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>学习时长(h)</p>
            </div>
          </div>
        </Card>

        <Card className={cn("col-span-3 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <p className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>6</p>
              <p className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>番茄钟(个)</p>
            </div>
          </div>
        </Card>

        <Card className={cn("col-span-3 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
              <CheckSquare className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <p className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>3</p>
              <p className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>完成任务(项)</p>
            </div>
          </div>
        </Card>

        <Card className={cn("col-span-3 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center">
              <Users className="w-6 h-6 text-violet-600" />
            </div>
            <div>
              <p className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>5</p>
              <p className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>学习天数(天)</p>
            </div>
          </div>
        </Card>

        {/* Row 2: Progress Card */}
        <Card className={cn("col-span-12 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex items-center justify-between mb-3">
            <h3 className={cn("font-semibold", isDark ? "text-white" : "text-slate-900")}>今日目标</h3>
            <Badge variant="emerald" className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
              1天连续
            </Badge>
          </div>
          <div className="flex items-center gap-3 mb-4">
            <Progress value={35} className="flex-1 h-3" />
            <span className="text-sm font-semibold text-emerald-600 w-12">35%</span>
          </div>
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div className={cn("p-3 rounded-lg", isDark ? "bg-slate-700" : "bg-slate-100")}>
              <p className={cn("text-xs mb-1", isDark ? "text-slate-400" : "text-slate-500")}>学习时长</p>
              <p className={cn("font-semibold", isDark ? "text-white" : "")}>0.5/2h</p>
            </div>
            <div className={cn("p-3 rounded-lg", isDark ? "bg-slate-700" : "bg-slate-100")}>
              <p className={cn("text-xs mb-1", isDark ? "text-slate-400" : "text-slate-500")}>番茄钟</p>
              <p className={cn("font-semibold", isDark ? "text-white" : "")}>2/6个</p>
            </div>
            <div className={cn("p-3 rounded-lg", isDark ? "bg-slate-700" : "bg-slate-100")}>
              <p className={cn("text-xs mb-1", isDark ? "text-slate-400" : "text-slate-500")}>任务完成</p>
              <p className={cn("font-semibold", isDark ? "text-white" : "")}>1/3项</p>
            </div>
            <div className={cn("p-3 rounded-lg", isDark ? "bg-slate-700" : "bg-slate-100")}>
              <p className={cn("text-xs mb-1", isDark ? "text-slate-400" : "text-slate-500")}>日记</p>
              <p className={cn("font-semibold", isDark ? "text-white" : "")}>已记录</p>
            </div>
          </div>
        </Card>

        {/* Row 3: Quick Actions */}
        <Card 
          className={cn("col-span-4 p-5 cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all", isDark && "bg-slate-800/50 border-slate-700")}
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center">
              <MessageCircle className="w-6 h-6 text-orange-500" />
            </div>
            <div className="flex-1">
              <p className={cn("font-semibold mb-1", isDark ? "text-white" : "text-slate-900")}>和搭子聊聊</p>
              <p className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>AI智能陪伴</p>
            </div>
            <ArrowRight className={cn("w-5 h-5", isDark ? "text-slate-600" : "text-slate-300")} />
          </div>
        </Card>

        <Card 
          className={cn("col-span-4 p-5 cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all", isDark && "bg-slate-800/50 border-slate-700")}
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-blue-500" />
            </div>
            <div className="flex-1">
              <p className={cn("font-semibold mb-1", isDark ? "text-white" : "text-slate-900")}>写日记</p>
              <p className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>记录今日心情</p>
            </div>
            <ArrowRight className={cn("w-5 h-5", isDark ? "text-slate-600" : "text-slate-300")} />
          </div>
        </Card>

        <Card 
          className={cn("col-span-4 p-5 cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all", isDark && "bg-slate-800/50 border-slate-700")}
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center">
              <CheckSquare className="w-6 h-6 text-violet-500" />
            </div>
            <div className="flex-1">
              <p className={cn("font-semibold mb-1", isDark ? "text-white" : "text-slate-900")}>待办事项</p>
              <p className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>今日任务清单</p>
            </div>
            <ArrowRight className={cn("w-5 h-5", isDark ? "text-slate-600" : "text-slate-300")} />
          </div>
        </Card>

        {/* Row 4: Goal Card */}
        <Card className={cn("col-span-12 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex items-center justify-between mb-4">
            <h3 className={cn("font-semibold flex items-center gap-2", isDark ? "text-white" : "text-slate-900")}>
              <GraduationCap className="w-5 h-5 text-amber-500" />
              考研目标
            </h3>
            <Button variant="ghost" size="sm" className="text-slate-500 text-xs">编辑</Button>
          </div>
          <div className="grid grid-cols-4 gap-4">
            <div className="flex items-center gap-3">
              <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center text-lg", isDark ? "bg-slate-700" : "bg-slate-100")}>&#127891;</div>
              <div>
                <p className={cn("text-sm font-semibold", isDark ? "text-white" : "text-slate-900")}>清华大学</p>
                <p className={cn("text-xs", isDark ? "text-slate-500" : "text-slate-500")}>目标院校</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center text-lg", isDark ? "bg-slate-700" : "bg-slate-100")}>&#128218;</div>
              <div>
                <p className={cn("text-sm font-semibold", isDark ? "text-white" : "text-slate-900")}>计算机科学与技术</p>
                <p className={cn("text-xs", isDark ? "text-slate-500" : "text-slate-500")}>目标专业</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center text-lg", isDark ? "bg-slate-700" : "bg-slate-100")}>&#9889;</div>
              <div>
                <p className={cn("text-sm font-semibold", isDark ? "text-white" : "text-slate-900")}>380分</p>
                <p className={cn("text-xs", isDark ? "text-slate-500" : "text-slate-500")}>目标分数</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", isDark ? "bg-slate-700" : "bg-slate-100")}>
                <Calendar className="w-5 h-5 text-slate-500" />
              </div>
              <div>
                <p className={cn("text-sm font-semibold", isDark ? "text-white" : "text-slate-900")}>193天</p>
                <p className={cn("text-xs", isDark ? "text-slate-500" : "text-slate-500")}>剩余天数</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Row 5: Today Timeline */}
        <Card className={cn("col-span-12 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <h3 className={cn("font-semibold mb-4", isDark ? "text-white" : "text-slate-900")}>今日学习记录</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <div className="w-16 text-sm text-slate-500">09:00 - 09:25</div>
              <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
              <div className="flex-1">
                <p className={cn("text-sm", isDark ? "text-slate-200" : "text-slate-700")}>完成高数第一章复习</p>
                <p className={cn("text-xs", isDark ? "text-slate-500" : "text-slate-500")}>1个番茄 · 数学</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-16 text-sm text-slate-500">09:30 - 09:55</div>
              <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
              <div className="flex-1">
                <p className={cn("text-sm", isDark ? "text-slate-200" : "text-slate-700")}>英语单词背诵</p>
                <p className={cn("text-xs", isDark ? "text-slate-500" : "text-slate-500")}>1个番茄 · 英语</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
