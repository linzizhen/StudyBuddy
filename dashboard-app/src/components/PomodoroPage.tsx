import React from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Play, Pause, RotateCcw, Settings,
 Coffee, Umbrella, Volume2
} from 'lucide-react'

interface PomodoroPageProps {
  isDark?: boolean
}

export function PomodoroPage({ isDark = false }: PomodoroPageProps) {
  const [timeLeft, setTimeLeft] = React.useState(25 * 60)
  const [isRunning, setIsRunning] = React.useState(false)
  const [focusDuration, setFocusDuration] = React.useState(25)
  const [breakDuration, setBreakDuration] = React.useState(5)
  const [selectedNoise, setSelectedNoise] = React.useState<string | null>(null)
  const [focusMode, setFocusMode] = React.useState('normal')
  const [noiseEnabled, setNoiseEnabled] = React.useState(false)

  React.useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => setTimeLeft((prev) => prev - 1), 1000)
    }
    return () => { if (interval) clearInterval(interval) }
  }, [isRunning, timeLeft])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const progress = ((focusDuration * 60 - timeLeft) / (focusDuration * 60)) * 100
  const circumference = 2 * Math.PI * 120
  const strokeDashoffset = circumference - (progress / 100) * circumference

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>番茄专注</h1>
        <Button variant="outline" size="sm" className="gap-2">
          <Settings className="w-4 h-4" />
          专注设置
        </Button>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Timer Section */}
        <Card className={cn("col-span-8 p-8", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex flex-col items-center">
            {/* Timer Circle */}
            <div className="relative w-64 h-64 mb-6">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="128" cy="128" r="120" fill="none" stroke={isDark ? "#334155" : "#e2e8f0"} strokeWidth="12" />
                <circle cx="128" cy="128" r="120" fill="none" stroke="#10b981" strokeWidth="12" strokeLinecap="round"
                  strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} className="transition-all duration-500" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-5xl font-bold font-mono" style={{ color: isDark ? '#fff' : '#0f172a' }}>
                  {formatTime(timeLeft)}
                </span>
                <span className={cn("text-sm mt-2", isDark ? "text-slate-400" : "text-slate-500")}>
                  {isRunning ? '专注中...' : '准备开始'}
                </span>
              </div>
            </div>

            {/* Current Task */}
            <div className="text-center mb-6">
              <p className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>当前专注任务</p>
              <p className={cn("font-medium", isDark ? "text-white" : "text-slate-900")}>高等数学 - 第三章练习</p>
            </div>

            {/* Control Buttons */}
            <div className="flex gap-3">
              <Button size="lg" className="w-32 gap-2 shadow-lg shadow-emerald-200" onClick={() => setIsRunning(!isRunning)}>
                {isRunning ? <><Pause className="w-5 h-5" />暂停</> : <><Play className="w-5 h-5" />开始</>}
              </Button>
              <Button size="lg" variant="outline" className="w-24 gap-2" onClick={() => { setIsRunning(false); setTimeLeft(focusDuration * 60) }}>
                <RotateCcw className="w-4 h-4" />重置
              </Button>
            </div>
          </div>
        </Card>

        {/* Settings Panel */}
        <Card className={cn("col-span-4 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <h3 className={cn("font-semibold mb-4", isDark ? "text-white" : "")}>专注设置</h3>
          <div className="space-y-5">
            <div>
              <label className={cn("text-sm mb-2 block", isDark ? "text-slate-300" : "text-slate-600")}>专注时长：{focusDuration}分钟</label>
              <input type="range" min="5" max="60" step="5" value={focusDuration}
                onChange={(e) => { if (!isRunning) { setFocusDuration(Number(e.target.value)); setTimeLeft(Number(e.target.value) * 60) }}}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-500" disabled={isRunning} />
              <div className={cn("flex justify-between text-xs mt-1", isDark ? "text-slate-500" : "text-slate-400")}>
                <span>5分钟</span><span>60分钟</span>
              </div>
            </div>

            <div>
              <label className={cn("text-sm mb-2 block", isDark ? "text-slate-300" : "text-slate-600")}>休息时长：{breakDuration}分钟</label>
              <input type="range" min="1" max="15" value={breakDuration} onChange={(e) => setBreakDuration(Number(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-500" />
            </div>

            <div>
              <label className={cn("text-sm mb-2 block", isDark ? "text-slate-300" : "text-slate-600")}>专注任务</label>
              <select className={cn("w-full h-10 px-3 rounded-lg border text-sm", isDark ? "bg-slate-700 border-slate-600 text-white" : "bg-white border-input")}>
                <option>高等数学 - 第三章练习</option>
                <option>英语单词背诵</option>
                <option>政治理论复习</option>
                <option>专业课学习</option>
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className={cn("text-sm", isDark ? "text-slate-300" : "text-slate-600")}>白噪音</label>
                <button onClick={() => setNoiseEnabled(!noiseEnabled)}
                  className={cn("w-10 h-6 rounded-full transition-colors relative", noiseEnabled ? "bg-emerald-500" : isDark ? "bg-slate-600" : "bg-slate-200")}>
                  <div className={cn("w-4 h-4 rounded-full bg-white absolute top-1 transition-transform", noiseEnabled ? "translate-x-5" : "translate-x-1")} />
                </button>
              </div>
              {noiseEnabled && (
                <div className="flex gap-2 mt-2">
                  {[{ id: 'rain', icon: Umbrella, label: '雨声' }, { id: 'white', icon: Volume2, label: '白噪音' }, { id: 'cafe', icon: Coffee, label: '咖啡馆' }].map((noise) => (
                    <button key={noise.id} onClick={() => setSelectedNoise(noise.id)}
                      className={cn("flex-1 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-center gap-1",
                        selectedNoise === noise.id ? "bg-emerald-100 text-emerald-700" : isDark ? "bg-slate-700 text-slate-300" : "bg-slate-100 text-slate-600")}>
                      <noise.icon className="w-3.5 h-3.5" />{noise.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className={cn("text-sm mb-2 block", isDark ? "text-slate-300" : "text-slate-600")}>专注模式</label>
              <div className="grid grid-cols-3 gap-2">
                {[{ id: 'normal', label: '普通' }, { id: 'strict', label: '严格' }, { id: 'zen', label: '禅模式' }].map((mode) => (
                  <button key={mode.id} onClick={() => setFocusMode(mode.id)}
                    className={cn("py-2 rounded-lg text-xs font-medium transition-colors",
                      focusMode === mode.id ? "bg-emerald-500 text-white" : isDark ? "bg-slate-700 text-slate-300" : "bg-slate-100 text-slate-600")}>
                    {mode.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Card>

        {/* Today's Records */}
        <Card className={cn("col-span-12 p-5", isDark && "bg-slate-800/50 border-slate-700")}>
          <h3 className={cn("font-semibold mb-4", isDark ? "text-white" : "text-slate-900")}>今日完成记录</h3>
          <div className="grid grid-cols-4 gap-4">
            {[{ time: '09:00', task: '高数第一章', duration: 25 }, { time: '09:30', task: '英语单词', duration: 25 }, { time: '10:00', task: '政治复习', duration: 25 }].map((record, i) => (
              <div key={i} className={cn("p-4 rounded-lg", isDark ? "bg-slate-700" : "bg-slate-100")}>
                <div className="flex items-center justify-between mb-2">
                  <span className={cn("text-sm font-medium", isDark ? "text-white" : "")}>{record.time}</span>
                  <span className="text-xs text-emerald-600 font-medium">+{record.duration}分钟</span>
                </div>
                <p className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>{record.task}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
