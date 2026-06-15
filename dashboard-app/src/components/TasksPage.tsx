import React from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Search, Plus, Trash2, Calendar, Clock, CheckCircle2, Circle, GripVertical } from 'lucide-react'

interface TasksPageProps {
  isDark?: boolean
}

interface Task {
  id: number
  title: string
  completed: boolean
  priority: 'high' | 'medium' | 'low'
  dueDate?: string
  group: 'today' | 'tomorrow' | 'week' | 'done'
}

const initialTasks: Task[] = [
  { id: 1, title: '完成高数第三章练习题', completed: false, priority: 'high', dueDate: '今天', group: 'today' },
  { id: 2, title: '背诵英语单词50个', completed: false, priority: 'medium', dueDate: '今天', group: 'today' },
  { id: 3, title: '整理政治笔记', completed: true, priority: 'low', group: 'done' },
  { id: 4, title: '专业课第三章视频学习', completed: false, priority: 'medium', dueDate: '明天', group: 'tomorrow' },
  { id: 5, title: '英语听力训练', completed: false, priority: 'low', dueDate: '明天', group: 'tomorrow' },
  { id: 6, title: '高数第四章预习', completed: false, priority: 'medium', dueDate: '本周', group: 'week' },
  { id: 7, title: '完成政治刷题', completed: false, priority: 'high', dueDate: '本周', group: 'week' },
]

const priorityColors = { high: 'bg-red-100 text-red-700', medium: 'bg-amber-100 text-amber-700', low: 'bg-slate-100 text-slate-600' }
const priorityLabels = { high: '高', medium: '中', low: '低' }

export function TasksPage({ isDark = false }: TasksPageProps) {
  const [tasks, setTasks] = React.useState(initialTasks)
  const [selectedTask, setSelectedTask] = React.useState<Task | null>(null)
  const [searchQuery, setSearchQuery] = React.useState('')
  const [filter, setFilter] = React.useState<'all' | 'today' | 'week'>('all')

  const toggleTask = (id: number) => {
    setTasks(prev => prev.map(task => task.id === id ? { ...task, completed: !task.completed } : task))
  }

  const deleteTask = (id: number) => {
    setTasks(prev => prev.filter(task => task.id !== id))
    if (selectedTask?.id === id) setSelectedTask(null)
  }

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filter === 'all' || (filter === 'today' && task.group === 'today') || (filter === 'week' && (task.group === 'week' || task.group === 'tomorrow'))
    return matchesSearch && matchesFilter
  })

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>待办任务</h1>
        <Button className="gap-2 shadow-lg shadow-emerald-200"><Plus className="w-4 h-4" />新建任务</Button>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Task List */}
        <Card className={cn("col-span-7 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex gap-3 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input placeholder="搜索任务..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className={cn("pl-9", isDark && "bg-slate-700 border-slate-600")} />
            </div>
            <div className="flex gap-1">
              {(['all', 'today', 'week'] as const).map((f) => (
                <Button key={f} size="sm" variant={filter === f ? 'default' : 'outline'} onClick={() => setFilter(f)} className={filter === f ? 'bg-emerald-500' : ''}>
                  {f === 'all' ? '全部' : f === 'today' ? '今日' : '本周'}
                </Button>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            {(['today', 'tomorrow', 'week', 'done'] as const).map((group) => {
              const groupTasks = filteredTasks.filter(t => group === 'done' ? t.completed : t.group === group && !t.completed)
              if (groupTasks.length === 0) return null
              const labels = { today: { title: '今日', color: 'text-red-600' }, tomorrow: { title: '明日', color: 'text-amber-600' }, week: { title: '本周', color: 'text-blue-600' }, done: { title: '已完成', color: isDark ? 'text-slate-400' : 'text-slate-500' } }

              return (
                <div key={group}>
                  <h3 className={cn("text-sm font-semibold mb-2 flex items-center gap-2", labels[group].color)}>
                    <Clock className="w-4 h-4" />{labels[group].title}
                    <Badge variant="outline" className="ml-auto text-xs">{groupTasks.length}</Badge>
                  </h3>
                  <div className="space-y-2">
                    {groupTasks.map((task) => (
                      <div key={task.id} onClick={() => setSelectedTask(task)}
                        className={cn("flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all",
                          selectedTask?.id === task.id ? "border-emerald-500 bg-emerald-50" : isDark ? "border-slate-600 hover:border-slate-500" : "border-slate-200 hover:border-slate-300")}>
                        <GripVertical className={cn("w-4 h-4 cursor-grab", isDark ? "text-slate-600" : "text-slate-300")} />
                        <button onClick={(e) => { e.stopPropagation(); toggleTask(task.id) }}>
                          {task.completed ? <CheckCircle2 className="w-5 h-5 text-emerald-500" /> : <Circle className={cn("w-5 h-5", isDark ? "text-slate-500" : "text-slate-300")} />}
                        </button>
                        <div className="flex-1 min-w-0">
                          <p className={cn("text-sm font-medium truncate", task.completed && "line-through", isDark ? "text-white" : "text-slate-900")}>{task.title}</p>
                          {task.dueDate && <p className={cn("text-xs flex items-center gap-1 mt-0.5", isDark ? "text-slate-500" : "text-slate-500")}><Calendar className="w-3 h-3" />{task.dueDate}</p>}
                        </div>
                        <Badge className={cn("text-xs", priorityColors[task.priority])}>{priorityLabels[task.priority]}</Badge>
                        <button onClick={(e) => { e.stopPropagation(); deleteTask(task.id) }} className={cn("p-1", isDark ? "text-slate-500 hover:text-red-400" : "text-slate-400 hover:text-red-500")}><Trash2 className="w-4 h-4" /></button>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </Card>

        {/* Task Detail */}
        <Card className={cn("col-span-5 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          {selectedTask ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className={cn("font-semibold", isDark ? "text-white" : "")}>任务详情</h3>
                <Badge className={priorityColors[selectedTask.priority]}>{priorityLabels[selectedTask.priority]}优先级</Badge>
              </div>
              <div>
                <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>任务标题</label>
                <Input defaultValue={selectedTask.title} className={cn(isDark ? "bg-slate-700 border-slate-600" : "")} />
              </div>
              <div>
                <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>任务描述</label>
                <textarea className={cn("w-full h-24 px-3 py-2 rounded-lg border text-sm resize-none", isDark ? "bg-slate-700 border-slate-600 text-white" : "border-input")} placeholder="添加任务描述..." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>截止日期</label>
                  <Input type="date" defaultValue={selectedTask.dueDate} className={cn(isDark ? "bg-slate-700 border-slate-600" : "")} />
                </div>
                <div>
                  <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>优先级</label>
                  <select className={cn("w-full h-10 px-3 rounded-lg border text-sm", isDark ? "bg-slate-700 border-slate-600" : "border-input")} defaultValue={selectedTask.priority}>
                    <option value="high">高优先级</option><option value="medium">中优先级</option><option value="low">低优先级</option>
                  </select>
                </div>
              </div>
              <div>
                <label className={cn("text-sm mb-2 block", isDark ? "text-slate-300" : "")}>关联番茄钟</label>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="gap-1"><Clock className="w-3.5 h-3.5" />添加番茄</Button>
                  <span className={cn("text-xs self-center", isDark ? "text-slate-500" : "text-slate-500")}>暂无关联</span>
                </div>
              </div>
              <div className="flex gap-2 pt-4 border-t">
                <Button className="flex-1">保存</Button>
                <Button variant="outline" className="text-red-500 hover:text-red-600 hover:bg-red-50">删除</Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-96 text-slate-400">
              <Circle className="w-12 h-12 mb-3" />
              <p>选择一个任务查看详情</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
