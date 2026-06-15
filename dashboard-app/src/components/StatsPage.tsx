import React from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts'

interface StatsPageProps {
  isDark?: boolean
}

const studyTrendData = [
  { month: '1月', hours: 42 }, { month: '2月', hours: 58 }, { month: '3月', hours: 75 },
  { month: '4月', hours: 68 }, { month: '5月', hours: 82 }, { month: '6月', hours: 91 },
]

const pomodoroData = [
  { day: '周一', count: 6 }, { day: '周二', count: 8 }, { day: '周三', count: 5 },
  { day: '周四', count: 7 }, { day: '周五', count: 9 }, { day: '周六', count: 4 }, { day: '周日', count: 3 },
]

const taskData = [
  { month: '1月', completed: 18, total: 25 }, { month: '2月', completed: 22, total: 28 },
  { month: '3月', completed: 28, total: 32 }, { month: '4月', completed: 25, total: 30 },
  { month: '5月', completed: 35, total: 38 }, { month: '6月', completed: 32, total: 35 },
]

const subjectData = [
  { name: '数学', value: 35, color: '#10b981' }, { name: '英语', value: 25, color: '#6366f1' },
  { name: '政治', value: 20, color: '#f59e0b' }, { name: '专业课', value: 20, color: '#ec4899' },
]

export function StatsPage({ isDark = false }: StatsPageProps) {
  const [timeRange, setTimeRange] = React.useState<'week' | 'month' | 'year'>('month')

  const tooltipStyle = { background: isDark ? '#1e293b' : '#fff', border: 'none', borderRadius: '8px', fontSize: '12px' }
  const axisStyle = { fontSize: 12, fill: '#94a3b8' }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>数据统计</h1>
        <div className={cn("flex gap-1 p-1 rounded-lg", isDark ? "bg-slate-800" : "bg-slate-100")}>
          {(['week', 'month', 'year'] as const).map((range) => (
            <Button key={range} size="sm" variant={timeRange === range ? 'default' : 'ghost'} onClick={() => setTimeRange(range)} className={timeRange === range ? 'bg-emerald-500' : ''}>
              {range === 'week' ? '本周' : range === 'month' ? '本月' : '今年'}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Study Trend */}
        <Card className={cn("col-span-8 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <h3 className={cn("font-semibold mb-4", isDark ? "text-white" : "")}>总学习时长趋势</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={studyTrendData}>
                <defs>
                  <linearGradient id="colorHours" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/><stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={axisStyle} />
                <YAxis axisLine={false} tickLine={false} tick={axisStyle} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="hours" stroke="#10b981" strokeWidth={2} fill="url(#colorHours)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Subject Distribution */}
        <Card className={cn("col-span-4 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <h3 className={cn("font-semibold mb-4", isDark ? "text-white" : "")}>科目占比</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={subjectData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value">
                  {subjectData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 mt-2">
            {subjectData.map((subject) => (
              <div key={subject.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: subject.color }} />
                <span className={cn("text-sm flex-1", isDark ? "text-slate-300" : "text-slate-600")}>{subject.name}</span>
                <span className={cn("text-sm font-medium", isDark ? "text-white" : "")}>{subject.value}%</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Pomodoro Stats */}
        <Card className={cn("col-span-6 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <h3 className={cn("font-semibold mb-4", isDark ? "text-white" : "")}>番茄钟完成统计</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={pomodoroData}>
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={axisStyle} />
                <YAxis axisLine={false} tickLine={false} tick={axisStyle} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Task Completion */}
        <Card className={cn("col-span-6 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <h3 className={cn("font-semibold mb-4", isDark ? "text-white" : "")}>任务完成率趋势</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={taskData}>
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={axisStyle} />
                <YAxis axisLine={false} tickLine={false} tick={axisStyle} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend />
                <Line type="monotone" dataKey="completed" name="已完成" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', strokeWidth: 0, r: 4 }} />
                <Line type="monotone" dataKey="total" name="总计" stroke={isDark ? '#475569' : '#e2e8f0'} strokeWidth={2} dot={{ fill: isDark ? '#475569' : '#e2e8f0', strokeWidth: 0, r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  )
}
