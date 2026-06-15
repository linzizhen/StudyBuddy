import React from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ChevronLeft, ChevronRight, Search, BookOpen, Calendar, Clock, Tag, X } from 'lucide-react'

interface DiaryPageProps {
  isDark?: boolean
}

const emotions = ['😢', '😔', '😐', '🙂', '😄']

const diaryEntries = [
  { id: 1, date: '2026-06-11', weekday: '星期四', mood: 4, preview: '今天完成了高数第三章的练习，感觉对极限的概念理解更深入了...', wordCount: 256 },
  { id: 2, date: '2026-06-10', weekday: '星期三', mood: 3, preview: '英语单词背了50个，长难句分析还是有点吃力...', wordCount: 189 },
  { id: 3, date: '2026-06-09', weekday: '星期二', mood: 5, preview: '今天效率特别高！完成了两章专业课的内容复习...', wordCount: 312 },
  { id: 4, date: '2026-06-08', weekday: '星期一', mood: 2, preview: '学习状态不太好，总是走神...', wordCount: 145 },
]

export function DiaryPage({ isDark = false }: DiaryPageProps) {
  const [selectedDiary, setSelectedDiary] = React.useState(diaryEntries[0])
  const [selectedMood, setSelectedMood] = React.useState(4)
  const [content, setContent] = React.useState('今天完成了高数第三章的练习，感觉对极限的概念理解更深入了。虽然有些题目还是需要思考很久，但至少不再是完全无从下手了。\n\n英语单词背了50个，复习了之前学过的，感觉记忆效果还不错。\n\n明天要继续加油！')
  const [searchQuery, setSearchQuery] = React.useState('')
  const [currentMonth] = React.useState('2026年6月')

  const wordCount = content.length

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>学习日记</h1>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Diary List */}
        <Card className={cn("col-span-4 p-4", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="flex items-center justify-between mb-4">
            <Button variant="ghost" size="icon"><ChevronLeft className="w-4 h-4" /></Button>
            <span className={cn("font-semibold", isDark ? "text-white" : "")}>{currentMonth}</span>
            <Button variant="ghost" size="icon"><ChevronRight className="w-4 h-4" /></Button>
          </div>

          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input placeholder="搜索日记..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className={cn("pl-9", isDark && "bg-slate-700 border-slate-600")} />
          </div>

          <div className="space-y-2">
            {diaryEntries.map((entry) => (
              <div key={entry.id} onClick={() => setSelectedDiary(entry)}
                className={cn("p-3 rounded-xl cursor-pointer transition-all",
                  selectedDiary?.id === entry.id ? (isDark ? "bg-emerald-900/50 border border-emerald-700" : "bg-emerald-50 border border-emerald-200") 
                  : (isDark ? "hover:bg-slate-700 border border-transparent" : "hover:bg-slate-50 border border-transparent"))}>
                <div className="flex items-center justify-between mb-1">
                  <span className={cn("text-sm font-medium", isDark ? "text-white" : "")}>{entry.date} {entry.weekday}</span>
                  <span className="text-lg">{emotions[entry.mood - 1]}</span>
                </div>
                <p className={cn("text-xs line-clamp-2", isDark ? "text-slate-400" : "text-slate-500")}>{entry.preview}</p>
                <div className={cn("flex items-center gap-2 mt-1.5 text-xs", isDark ? "text-slate-500" : "text-slate-400")}>
                  <span>{entry.wordCount}字</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Editor */}
        <Card className={cn("col-span-8 p-6", isDark && "bg-slate-800/50 border-slate-700")}>
          {selectedDiary && (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-4 border-b">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Calendar className={cn("w-4 h-4", isDark ? "text-slate-400" : "text-slate-400")} />
                    <span className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-600")}>{selectedDiary.date} {selectedDiary.weekday}</span>
                  </div>
                </div>
              </div>

              <div>
                <label className={cn("text-sm mb-2 block", isDark ? "text-slate-300" : "")}>今天心情怎么样？</label>
                <div className="flex gap-2">
                  {emotions.map((emoji, i) => (
                    <button key={i} onClick={() => setSelectedMood(i + 1)}
                      className={cn("w-12 h-12 rounded-xl text-xl flex items-center justify-center transition-all",
                        selectedMood === i + 1 ? "bg-emerald-100 ring-2 ring-emerald-500 scale-110" : isDark ? "bg-slate-700 hover:bg-slate-600" : "bg-slate-100 hover:bg-slate-200")}>
                      {emoji}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className={cn("text-sm mb-2 block flex items-center gap-1", isDark && "text-slate-300")}>
                  <Tag className="w-4 h-4" />标签
                </label>
                <div className="flex flex-wrap gap-2">
                  <span className="px-2.5 py-1 bg-emerald-100 text-emerald-700 text-xs rounded-full flex items-center gap-1">学习 <X className="w-3 h-3 cursor-pointer" /></span>
                  <span className="px-2.5 py-1 bg-blue-100 text-blue-700 text-xs rounded-full flex items-center gap-1">数学 <X className="w-3 h-3 cursor-pointer" /></span>
                  <button className={cn("px-2.5 py-1 text-xs rounded-full", isDark ? "bg-slate-700 text-slate-300" : "bg-slate-100 text-slate-600 hover:bg-slate-200")}>+ 添加</button>
                </div>
              </div>

              <div>
                <label className={cn("text-sm mb-2 block", isDark ? "text-slate-300" : "")}>记录一下今天</label>
                <textarea value={content} onChange={(e) => setContent(e.target.value)}
                  className={cn("w-full h-64 px-4 py-3 rounded-xl border text-sm resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500 leading-relaxed",
                    isDark ? "bg-slate-700 border-slate-600 text-white" : "border-input bg-background")}
                  placeholder="今天发生了什么？有什么想对搭子说的？" />
              </div>

              <div className="flex items-center justify-between pt-4 border-t">
                <div className={cn("flex items-center gap-4 text-xs", isDark ? "text-slate-500" : "text-slate-500")}>
                  <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />最后编辑：刚刚</span>
                  <span>{wordCount} 字</span>
                </div>
                <Button className="gap-2 shadow-lg shadow-emerald-200"><BookOpen className="w-4 h-4" />保存日记</Button>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
