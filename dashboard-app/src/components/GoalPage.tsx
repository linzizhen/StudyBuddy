import React from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { GraduationCap, Edit3, BookOpen, ArrowRight } from 'lucide-react'

interface GoalPageProps {
  isDark?: boolean
}

const phases = [
  { name: '基础阶段', progress: 65, tasks: [{ name: '数学第一轮复习', completed: true }, { name: '英语单词背诵', completed: true }, { name: '政治基础知识', completed: false }] },
  { name: '强化阶段', progress: 30, tasks: [{ name: '数学专题突破', completed: false }, { name: '英语真题练习', completed: false }, { name: '政治刷题', completed: false }] },
  { name: '冲刺阶段', progress: 5, tasks: [{ name: '全真模拟', completed: false }, { name: '查漏补缺', completed: false }, { name: '考前调整', completed: false }] },
]

export function GoalPage({ isDark = false }: GoalPageProps) {
  const [goalData, setGoalData] = React.useState({
    school: '清华大学', major: '计算机科学与技术', totalScore: 380,
    mathScore: 130, englishScore: 75, politicsScore: 70, majorScore: 105, examDate: '2026-12-21',
  })

  const totalProgress = Math.round(phases.reduce((sum, p) => sum + p.progress, 0) / phases.length)

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>考研目标</h1>
        <Button className="gap-2 shadow-lg shadow-emerald-200"><Edit3 className="w-4 h-4" />编辑目标</Button>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Goal Settings */}
        <Card className={cn("col-span-5 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <h3 className={cn("font-semibold mb-4 flex items-center gap-2", isDark ? "text-white" : "")}>
            <GraduationCap className="w-5 h-5 text-emerald-500" />目标设置
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>目标院校</label>
              <Input value={goalData.school} onChange={(e) => setGoalData({...goalData, school: e.target.value})} className={isDark ? "bg-slate-700 border-slate-600" : ""} />
            </div>
            <div>
              <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>目标专业</label>
              <Input value={goalData.major} onChange={(e) => setGoalData({...goalData, major: e.target.value})} className={isDark ? "bg-slate-700 border-slate-600" : ""} />
            </div>
            <div>
              <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>总分目标</label>
              <Input type="number" value={goalData.totalScore} onChange={(e) => setGoalData({...goalData, totalScore: parseInt(e.target.value) || 0})} className={isDark ? "bg-slate-700 border-slate-600" : ""} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>数学</label>
                <Input type="number" value={goalData.mathScore} onChange={(e) => setGoalData({...goalData, mathScore: parseInt(e.target.value) || 0})} className={isDark ? "bg-slate-700 border-slate-600" : ""} />
              </div>
              <div>
                <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>英语</label>
                <Input type="number" value={goalData.englishScore} onChange={(e) => setGoalData({...goalData, englishScore: parseInt(e.target.value) || 0})} className={isDark ? "bg-slate-700 border-slate-600" : ""} />
              </div>
              <div>
                <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>政治</label>
                <Input type="number" value={goalData.politicsScore} onChange={(e) => setGoalData({...goalData, politicsScore: parseInt(e.target.value) || 0})} className={isDark ? "bg-slate-700 border-slate-600" : ""} />
              </div>
              <div>
                <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>专业课</label>
                <Input type="number" value={goalData.majorScore} onChange={(e) => setGoalData({...goalData, majorScore: parseInt(e.target.value) || 0})} className={isDark ? "bg-slate-700 border-slate-600" : ""} />
              </div>
            </div>

            <div>
              <label className={cn("text-sm mb-1 block", isDark ? "text-slate-300" : "")}>考试日期</label>
              <Input type="date" value={goalData.examDate} onChange={(e) => setGoalData({...goalData, examDate: e.target.value})} className={isDark ? "bg-slate-700 border-slate-600" : ""} />
            </div>
          </div>
        </Card>

        {/* Study Plan */}
        <Card className={cn("col-span-7 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex items-center justify-between mb-4">
            <h3 className={cn("font-semibold flex items-center gap-2", isDark ? "text-white" : "")}>
              <BookOpen className="w-5 h-5 text-blue-500" />学习计划
            </h3>
            <div className="flex items-center gap-2">
              <span className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>整体进度</span>
              <span className="text-lg font-bold text-emerald-600">{totalProgress}%</span>
            </div>
          </div>
          <Progress value={totalProgress} className="h-2 mb-4" />

          <div className="space-y-4">
            {phases.map((phase, i) => (
              <div key={i} className={cn("p-4 rounded-xl", isDark ? "bg-slate-700" : "bg-slate-50")}>
                <div className="flex items-center justify-between mb-2">
                  <span className={cn("font-medium", isDark ? "text-white" : "")}>{phase.name}</span>
                  <span className={cn("text-sm font-medium", phase.progress === 100 ? "text-emerald-600" : isDark ? "text-slate-400" : "text-slate-500")}>{phase.progress}%</span>
                </div>
                <Progress value={phase.progress} className="h-1.5 mb-2" />
                <div className="space-y-1.5">
                  {phase.tasks.map((task, j) => (
                    <div key={j} className="flex items-center gap-2 text-sm">
                      {task.completed ? (
                        <div className="w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center"><span className="text-white text-[10px]">✓</span></div>
                      ) : (
                        <div className="w-4 h-4 rounded-full border-2" style={{ borderColor: isDark ? '#475569' : '#cbd5e1' }} />
                      )}
                      <span className={task.completed ? (isDark ? 'text-slate-500 line-through' : 'text-slate-400 line-through') : (isDark ? 'text-slate-200' : 'text-slate-700')}>{task.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <Button variant="outline" className="w-full mt-4 gap-2"><ArrowRight className="w-4 h-4" />查看详细计划</Button>
        </Card>
      </div>
    </div>
  )
}
