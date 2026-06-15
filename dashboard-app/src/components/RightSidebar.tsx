import React from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { Lightbulb } from 'lucide-react'

interface RightSidebarProps {
  currentPage: string
  isDark?: boolean
}

const weeklyData = [
  { day: '周一', hours: 2.5 },
  { day: '周二', hours: 3.2 },
  { day: '周三', hours: 1.8 },
  { day: '周四', hours: 4.0 },
  { day: '周五', hours: 2.8 },
  { day: '周六', hours: 3.5 },
  { day: '周日', hours: 2.2 },
]

const todayTasks = [
  { id: 1, text: '完成高数第三章练习题', completed: false },
  { id: 2, text: '背诵英语单词50个', completed: false },
  { id: 3, text: '整理政治笔记', completed: true },
]

const tips = [
  '番茄工作法：专注25分钟，休息5分钟，效率翻倍！',
  '学习间隙活动一下，促进血液循环更清醒。',
  '每天睡前复习当天内容，记忆更持久。',
  '保持充足睡眠，第二天的学习效率会更高。',
]

export function RightSidebar({ currentPage, isDark = false }: RightSidebarProps) {
  const [tasks, setTasks] = React.useState(todayTasks)
  const [tipIndex] = React.useState(Math.floor(Math.random() * tips.length))

  const toggleTask = (id: number) => {
    setTasks(prev => prev.map(task => 
      task.id === id ? { ...task, completed: !task.completed } : task
    ))
  }

  const getSidebarContent = () => {
    switch (currentPage) {
      case 'pomodoro':
        return <PomodoroRightSidebar isDark={isDark} />
      case 'tasks':
        return <TasksRightSidebar isDark={isDark} />
      case 'diary':
        return <DiaryRightSidebar isDark={isDark} />
      case 'buddy':
        return <BuddyRightSidebar isDark={isDark} />
      case 'stats':
        return <StatsRightSidebar isDark={isDark} />
      case 'goal':
        return <GoalRightSidebar isDark={isDark} />
      default:
        return <DashboardRightSidebar isDark={isDark} tasks={tasks} toggleTask={toggleTask} tipIndex={tipIndex} />
    }
  }

  return (
    <aside className={cn(
      "w-[320px] h-screen flex flex-col border-l shrink-0 overflow-hidden",
      isDark ? "bg-slate-900 border-slate-700" : "bg-white border-slate-200"
    )}>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {getSidebarContent()}
      </div>
    </aside>
  )
}

function DashboardRightSidebar({ isDark, tasks, toggleTask, tipIndex }: {
  isDark: boolean
  tasks: typeof todayTasks
  toggleTask: (id: number) => void
  tipIndex: number
}) {
  return (
    <>
      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "bg-slate-50")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "text-slate-900")}>本周学习时长趋势</h3>
        <div className="h-[140px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={weeklyData}>
              <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: isDark ? '#94a3b8' : '#94a3b8' }} />
              <YAxis hide />
              <Tooltip contentStyle={{ background: isDark ? '#1e293b' : '#fff', border: 'none', borderRadius: '8px', fontSize: '12px' }} />
              <Line type="monotone" dataKey="hours" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', strokeWidth: 0, r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "bg-slate-50")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "text-slate-900")}>今日待办</h3>
        <div className="space-y-2.5">
          {tasks.map((task) => (
            <label key={task.id} className="flex items-center gap-2.5 cursor-pointer">
              <input type="checkbox" checked={task.completed} onChange={() => toggleTask(task.id)} className="w-4 h-4 rounded border-2 border-slate-300 text-emerald-500 cursor-pointer accent-emerald-500" />
              <span className={cn("text-sm", task.completed ? "text-slate-400 line-through" : isDark ? "text-slate-200" : "text-slate-700")}>{task.text}</span>
            </label>
          ))}
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-emerald-900/20" : "bg-emerald-50/50")}>
        <div className="flex items-center gap-3 mb-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-500 flex items-center justify-center text-lg text-white shadow-md">&#128150;</div>
            <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-white"></div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={cn("font-semibold text-sm", isDark ? "text-white" : "text-slate-900")}>小豆</span>
              <span className="text-[10px] text-emerald-600 font-medium">在线</span>
            </div>
            <p className={cn("text-xs", isDark ? "text-slate-400" : "text-slate-500")}>今天也要加油哦~</p>
          </div>
        </div>
        <button className="w-full py-2 bg-emerald-500 text-white rounded-lg text-sm font-medium hover:bg-emerald-600 transition-colors">和搭子聊聊</button>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-amber-900/20" : "bg-amber-50")}>
        <div className="flex items-start gap-2">
          <Lightbulb className={cn("w-4 h-4 mt-0.5 shrink-0", isDark ? "text-amber-400" : "text-amber-600")} />
          <p className={cn("text-sm leading-relaxed", isDark ? "text-amber-300" : "text-amber-800")}>{tips[tipIndex]}</p>
        </div>
      </Card>
    </>
  )
}

function PomodoroRightSidebar({ isDark }: { isDark: boolean }) {
  const weeklyData = [
    { day: '周一', count: 4 }, { day: '周二', count: 6 }, { day: '周三', count: 3 },
    { day: '周四', count: 5 }, { day: '周五', count: 2 }, { day: '周六', count: 0 }, { day: '周日', count: 1 },
  ]
  const maxCount = Math.max(...weeklyData.map(d => d.count))

  return (
    <>
      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>今日番茄统计</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-2 bg-slate-100 rounded-lg">
            <p className="text-xl font-bold text-emerald-600">3</p>
            <p className="text-xs text-slate-500">完成数</p>
          </div>
          <div className="text-center p-2 bg-slate-100 rounded-lg">
            <p className="text-xl font-bold text-slate-900">75</p>
            <p className="text-xs text-slate-500">总分钟</p>
          </div>
          <div className="text-center p-2 bg-slate-100 rounded-lg">
            <p className="text-xl font-bold text-slate-900">25</p>
            <p className="text-xs text-slate-500">平均分钟</p>
          </div>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>本周完成率</h3>
        <div className="flex items-end justify-between h-24 gap-1">
          {weeklyData.map((day) => (
            <div key={day.day} className="flex-1 flex flex-col items-center gap-1">
              <div className="w-full flex flex-col items-center">
                <div className="w-full bg-emerald-500 rounded-t transition-all" style={{ height: `${(day.count / maxCount) * 80}px`, minHeight: day.count > 0 ? '4px' : '0' }} />
              </div>
              <span className="text-[10px] text-slate-500">{day.day}</span>
            </div>
          ))}
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>专注成就</h3>
        <div className="space-y-2">
          {[{ icon: '🌱', label: '初次专注', desc: '完成第一个番茄钟' }, { icon: '🔥', label: '连续3天', desc: '连续三天完成番茄' }, { icon: '⭐', label: '10个番茄', desc: '累计完成10个番茄' }].map((badge, i) => (
            <div key={i} className="flex items-center gap-3 p-2 rounded-lg bg-slate-100">
              <span className="text-lg">{badge.icon}</span>
              <div>
                <p className="text-sm font-medium text-slate-900">{badge.label}</p>
                <p className="text-xs text-slate-500">{badge.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-amber-900/20" : "bg-amber-50")}>
        <div className="flex items-start gap-2">
          <Lightbulb className={cn("w-4 h-4 mt-0.5 shrink-0", isDark ? "text-amber-400" : "text-amber-600")} />
          <p className={cn("text-sm leading-relaxed", isDark ? "text-amber-300" : "text-amber-800")}>保持专注是关键，中途放弃会降低效率</p>
        </div>
      </Card>
    </>
  )
}

function TasksRightSidebar({ isDark }: { isDark: boolean }) {
  return (
    <>
      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>任务概览</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between"><span className="text-sm text-slate-600">待完成</span><span className="text-sm font-semibold text-slate-900">5</span></div>
          <div className="flex items-center justify-between"><span className="text-sm text-slate-600">进行中</span><span className="text-sm font-semibold text-amber-600">2</span></div>
          <div className="flex items-center justify-between"><span className="text-sm text-slate-600">已完成</span><span className="text-sm font-semibold text-emerald-600">1</span></div>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-red-900/20" : "bg-red-50/50")}>
        <h3 className={cn("text-sm font-semibold mb-3 flex items-center gap-2", isDark ? "text-red-400" : "text-red-600")}>
          <span>⚠️</span>今日到期
        </h3>
        <div className="space-y-2">
          {[{ id: 1, title: '完成高数第三章练习题' }, { id: 2, title: '背诵英语单词50个' }].map(task => (
            <div key={task.id} className="text-sm p-2 bg-white rounded-lg border border-red-100">
              <p className="font-medium text-slate-900">{task.title}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>本周完成率</h3>
        <div className="flex items-center gap-3">
          <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-emerald-500 rounded-full" style={{ width: '65%' }} /></div>
          <span className="text-sm font-semibold text-emerald-600">65%</span>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>快速添加</h3>
        <div className="flex gap-2">
          <input type="text" placeholder="快速添加任务..." className={cn("flex-1 px-3 py-2 rounded-lg border text-sm", isDark ? "bg-slate-700 border-slate-600 text-white placeholder:text-slate-400" : "bg-white border-input")} />
          <button className="px-3 py-2 bg-emerald-500 text-white rounded-lg text-sm">+</button>
        </div>
      </Card>
    </>
  )
}

function DiaryRightSidebar({ isDark }: { isDark: boolean }) {
  const moodData = [
    { mood: '很开心', emoji: '😄', count: 2, color: 'bg-emerald-500' },
    { mood: '还好', emoji: '🙂', count: 1, color: 'bg-blue-500' },
    { mood: '一般', emoji: '😐', count: 1, color: 'bg-slate-500' },
    { mood: '有点丧', emoji: '😔', count: 1, color: 'bg-amber-500' },
    { mood: '很难过', emoji: '😢', count: 0, color: 'bg-red-500' },
  ]
  const tags = ['学习', '数学', '英语', '政治', '效率', '休息', '心情', '计划']

  return (
    <>
      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>本月统计</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-2 bg-slate-100 rounded-lg"><p className="text-lg font-bold text-emerald-600">5</p><p className="text-xs text-slate-500">写作天数</p></div>
          <div className="text-center p-2 bg-slate-100 rounded-lg"><p className="text-lg font-bold text-slate-900">1180</p><p className="text-xs text-slate-500">总字数</p></div>
          <div className="text-center p-2 bg-slate-100 rounded-lg"><p className="text-lg font-bold text-slate-900">236</p><p className="text-xs text-slate-500">平均字数</p></div>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>心情分布</h3>
        <div className="space-y-2">
          {moodData.map((item) => (
            <div key={item.mood} className="flex items-center gap-2">
              <span className="text-sm w-6">{item.emoji}</span>
              <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden"><div className={cn("h-full rounded-full", item.color)} style={{ width: `${(item.count / 5) * 100}%` }} /></div>
              <span className="text-xs text-slate-500 w-6">{item.count}天</span>
            </div>
          ))}
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>标签云</h3>
        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (<span key={tag} className={cn("px-2.5 py-1 text-xs rounded-full cursor-pointer", isDark ? "bg-slate-700 text-slate-300 hover:bg-emerald-900" : "bg-slate-100 text-slate-600 hover:bg-emerald-100 hover:text-emerald-700")}>{tag}</span>))}
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-amber-900/20" : "bg-amber-50")}>
        <h3 className={cn("text-sm font-semibold mb-2", isDark ? "text-amber-300" : "text-amber-800")}>随机回顾</h3>
        <p className={cn("text-xs mb-2", isDark ? "text-amber-400" : "text-amber-700")}>2026年5月28日</p>
        <p className={cn("text-sm leading-relaxed line-clamp-4", isDark ? "text-amber-200" : "text-amber-900")}>今天完成了考研数学的基础复习，感觉进步了很多。学习搭子小豆一直在鼓励我...</p>
      </Card>
    </>
  )
}

function BuddyRightSidebar({ isDark }: { isDark: boolean }) {
  return (
    <>
      <Card className={cn("p-4", isDark ? "bg-emerald-900/20" : "bg-emerald-50/50")}>
        <div className="text-center mb-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-500 flex items-center justify-center text-3xl text-white mx-auto mb-3 shadow-lg">&#128150;</div>
          <h3 className={cn("font-semibold", isDark ? "text-white" : "")}>小豆</h3>
          <p className={cn("text-xs", isDark ? "text-slate-400" : "text-slate-500")}>温暖鼓励型</p>
          <div className="flex items-center justify-center gap-2 mt-2">
            <span className="px-2 py-0.5 bg-emerald-500 text-white text-xs rounded-full">Lv.3</span>
            <span className={cn("px-2 py-0.5 text-xs rounded-full border", isDark ? "border-slate-600 text-slate-300" : "border-slate-200 text-slate-600")}>累计学习 52h</span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="p-2 bg-white rounded-lg"><p className="text-lg font-bold text-emerald-600">17.5h</p><p className="text-[10px] text-slate-500">本周</p></div>
          <div className="p-2 bg-white rounded-lg"><p className="text-lg font-bold text-amber-600">14</p><p className="text-[10px] text-slate-500">番茄</p></div>
          <div className="p-2 bg-white rounded-lg"><p className="text-lg font-bold text-blue-600">5</p><p className="text-[10px] text-slate-500">共同天</p></div>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <div className="flex items-center justify-between">
          <div>
            <p className={cn("text-sm font-medium", isDark ? "text-white" : "")}>学习打卡提醒</p>
            <p className={cn("text-xs", isDark ? "text-slate-400" : "text-slate-500")}>搭子互相提醒</p>
          </div>
          <div className="w-10 h-6 rounded-full bg-emerald-500 relative"><div className="w-4 h-4 rounded-full bg-white absolute top-1 translate-x-5" /></div>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>本周成就</h3>
        <div className="space-y-2">
          {[{ icon: '👑', label: '坚持5天', desc: '连续学习5天' }, { icon: '⚡', label: '高效学习', desc: '单日完成6个番茄' }].map((item, i) => (
            <div key={i} className="flex items-center gap-3 p-2 rounded-lg bg-slate-100">
              <span className="text-lg">{item.icon}</span>
              <div><p className="text-sm font-medium text-slate-900">{item.label}</p><p className="text-xs text-slate-500">{item.desc}</p></div>
            </div>
          ))}
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>推荐搭子</h3>
        <div className="space-y-2">
          {[{ name: '小静', avatar: '👻', trait: '安静陪伴型' }, { name: '小博', avatar: '📚', trait: '博学指导型' }].map((buddy) => (
            <div key={buddy.name} className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50 cursor-pointer">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-slate-300 to-slate-400 flex items-center justify-center text-sm text-white">{buddy.avatar}</div>
              <div className="flex-1"><p className="text-sm font-medium text-slate-900">{buddy.name}</p><p className="text-xs text-slate-500">{buddy.trait}</p></div>
              <button className="text-xs text-emerald-600 hover:text-emerald-700">切换</button>
            </div>
          ))}
        </div>
      </Card>
    </>
  )
}

function StatsRightSidebar({ isDark }: { isDark: boolean }) {
  return (
    <>
      <Card className={cn("p-4", isDark ? "bg-emerald-900/20" : "bg-emerald-50/50")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>学习画像</h3>
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs rounded-full">🌌 早起学习者</span>
          <span className="px-2 py-1 bg-amber-100 text-amber-700 text-xs rounded-full">🔥 番茄达人</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">📚 数学爱好者</span>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>累计成就</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center p-3 bg-slate-100 rounded-xl"><p className="text-2xl font-bold text-emerald-600">376</p><p className="text-xs text-slate-500">累计小时</p></div>
          <div className="text-center p-3 bg-slate-100 rounded-xl"><p className="text-2xl font-bold text-amber-600">142</p><p className="text-xs text-slate-500">番茄总数</p></div>
          <div className="text-center p-3 bg-slate-100 rounded-xl"><p className="text-2xl font-bold text-blue-600">42</p><p className="text-xs text-slate-500">累计天数</p></div>
          <div className="text-center p-3 bg-slate-100 rounded-xl"><p className="text-2xl font-bold text-violet-600">85%</p><p className="text-xs text-slate-500">任务完成率</p></div>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-violet-900/20" : "bg-violet-50")}>
        <h3 className={cn("text-sm font-semibold mb-2", isDark ? "text-violet-300" : "text-violet-800")}>超越同阶段用户</h3>
        <div className="flex items-center gap-2">
          <span className="text-3xl font-bold text-violet-600">78%</span>
          <div><p className={cn("text-xs", isDark ? "text-violet-400" : "text-violet-600")}>用户</p><p className={cn("text-xs", isDark ? "text-violet-400" : "text-violet-600")}>超越</p></div>
        </div>
        <div className="mt-2 h-2 bg-violet-100 rounded-full overflow-hidden"><div className="h-full bg-violet-500 rounded-full" style={{ width: '78%' }} /></div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>学习建议</h3>
        <div className="space-y-2">
          {['建议增加早晨的学习时间，这段时间效率最高', '本周数学学习时间偏少，建议加强', '注意休息，每完成4个番茄后休息15分钟'].map((suggestion, i) => (
            <div key={i} className="flex items-start gap-2 text-sm">
              <span className="text-emerald-500 shrink-0">{i + 1}.</span>
              <p className={cn("leading-relaxed", isDark ? "text-slate-300" : "text-slate-600")}>{suggestion}</p>
            </div>
          ))}
        </div>
      </Card>
    </>
  )
}

function GoalRightSidebar({ isDark }: { isDark: boolean }) {
  const daysLeft = Math.ceil((new Date('2026-12-21').getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))

  return (
    <>
      <Card className="p-6 bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
        <div className="text-center">
          <p className="text-sm text-emerald-100 mb-1">距离考研初试</p>
          <div className="text-5xl font-bold mb-1">{daysLeft}</div>
          <p className="text-sm text-emerald-100">天</p>
          <div className="mt-4 pt-4 border-t border-emerald-400/30"><p className="text-xs text-emerald-100">2026年12月21日</p></div>
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>各科学习进度</h3>
        <div className="space-y-3">
          {[{ name: '数学', progress: 65, color: 'bg-emerald-500' }, { name: '英语', progress: 45, color: 'bg-blue-500' }, { name: '政治', progress: 30, color: 'bg-amber-500' }, { name: '专业课', progress: 40, color: 'bg-violet-500' }].map((subject) => (
            <div key={subject.name}>
              <div className="flex items-center justify-between mb-1"><span className="text-sm text-slate-600">{subject.name}</span><span className="text-sm font-medium text-slate-900">{subject.progress}%</span></div>
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden"><div className={cn("h-full rounded-full transition-all", subject.color)} style={{ width: `${subject.progress}%` }} /></div>
            </div>
          ))}
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>重要节点</h3>
        <div className="space-y-2">
          {[{ name: '考研初试', date: '2026-12-21', daysLeft, type: 'important' }, { name: '成绩公布', date: '2027-02-21', daysLeft: 245, type: 'normal' }, { name: '考研复试', date: '2027-03-25', daysLeft: 277, type: 'important' }].map((event, i) => (
            <div key={i} className={cn("p-3 rounded-lg", event.type === 'important' ? 'bg-amber-50 border border-amber-100' : 'bg-slate-100')}>
              <div className="flex items-center justify-between">
                <span className={cn("text-sm font-medium", event.type === 'important' ? 'text-amber-800' : 'text-slate-700')}>{event.name}</span>
                <span className={cn("px-2 py-0.5 text-xs rounded-full", event.type === 'important' ? 'bg-amber-500 text-white' : 'bg-slate-200 text-slate-600')}>{event.daysLeft}天</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">{event.date}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card className={cn("p-4", isDark ? "bg-slate-800/50" : "")}>
        <h3 className={cn("text-sm font-semibold mb-3", isDark ? "text-white" : "")}>目标院校历年分数线</h3>
        <div className="space-y-2">
          {[{ year: '2025', score: 365 }, { year: '2024', score: 358 }, { year: '2023', score: 352 }].map((item) => (
            <div key={item.year} className="flex items-center justify-between p-2 bg-slate-100 rounded-lg">
              <span className="text-sm text-slate-600">{item.year}年</span>
              <span className="text-sm font-semibold text-emerald-600">{item.score}分</span>
            </div>
          ))}
        </div>
        <div className="mt-3 p-3 bg-emerald-50 rounded-lg border border-emerald-100">
          <p className="text-xs text-emerald-700">目标分数 <span className="font-bold">380</span> 分，比去年分数线高 <span className="font-bold text-emerald-600">+15分</span></p>
        </div>
      </Card>
    </>
  )
}
