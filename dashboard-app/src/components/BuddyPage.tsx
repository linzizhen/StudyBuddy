import React from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Search, Send, Smile, Users, Play } from 'lucide-react'

interface BuddyPageProps {
  isDark?: boolean
}

interface Message {
  id: number
  type: 'user' | 'buddy'
  content: string
  time: string
}

const buddies = [
  { id: 1, name: '小豆', avatar: '&#128150;', status: 'online', todayHours: 2.5 },
  { id: 2, name: '小火', avatar: '&#128293;', status: 'studying', todayHours: 3.2 },
  { id: 3, name: '小学霸', avatar: '&#128218;', status: 'online', todayHours: 4.1 },
  { id: 4, name: '小太阳', avatar: '&#127774;', status: 'offline', todayHours: 1.8 },
]

const messages: Message[] = [
  { id: 1, type: 'buddy', content: '嗨！今天学习怎么样？', time: '09:30' },
  { id: 2, type: 'user', content: '还不错，完成了高数第三章的练习', time: '09:31' },
  { id: 3, type: 'buddy', content: '太棒了！继续保持这个状态，你一定能成功的！&#128079;', time: '09:32' },
  { id: 4, type: 'buddy', content: '有什么不懂的地方可以问我哦~', time: '09:32' },
]

export function BuddyPage({ isDark = false }: BuddyPageProps) {
  const [selectedBuddy, setSelectedBuddy] = React.useState(buddies[0])
  const [inputMessage, setInputMessage] = React.useState('')
  const [chatMessages, setChatMessages] = React.useState(messages)
  const [searchQuery, setSearchQuery] = React.useState('')

  const handleSend = () => {
    if (!inputMessage.trim()) return
    const newMessage: Message = { id: Date.now(), type: 'user', content: inputMessage, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }
    setChatMessages([...chatMessages, newMessage])
    setInputMessage('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  const filteredBuddies = buddies.filter(b => b.name.toLowerCase().includes(searchQuery.toLowerCase()))

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className={cn("text-2xl font-bold", isDark ? "text-white" : "text-slate-900")}>学习搭子</h1>
        <Button variant="outline" className="gap-2"><Users className="w-4 h-4" />切换学习搭子</Button>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Buddy List */}
        <Card className={cn("col-span-4 p-4", isDark && "bg-slate-800/50 border-slate-700")}>
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input placeholder="搜索搭子..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className={cn("pl-9", isDark && "bg-slate-700 border-slate-600")} />
          </div>

          <div className="space-y-2">
            {filteredBuddies.map((buddy) => (
              <div key={buddy.id} onClick={() => setSelectedBuddy(buddy)}
                className={cn("p-3 rounded-xl cursor-pointer transition-all flex items-center gap-3",
                  selectedBuddy?.id === buddy.id ? (isDark ? "bg-emerald-900/50 border border-emerald-700" : "bg-emerald-50 border border-emerald-200")
                  : (isDark ? "hover:bg-slate-700 border border-transparent" : "hover:bg-slate-50 border border-transparent"))}>
                <div className="relative">
                  <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-500 flex items-center justify-center text-lg text-white">{buddy.avatar}</div>
                  <div className={cn("absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white",
                    buddy.status === 'online' && 'bg-emerald-500', buddy.status === 'studying' && 'bg-amber-500', buddy.status === 'offline' && 'bg-slate-400')} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={cn("font-medium text-sm", isDark ? "text-white" : "")}>{buddy.name}</span>
                    <Badge variant={buddy.status === 'online' ? 'emerald' : 'outline'} className="text-[10px]">{buddy.status === 'online' ? '在线' : buddy.status === 'studying' ? '学习中' : '离线'}</Badge>
                  </div>
                  <p className={cn("text-xs", isDark ? "text-slate-400" : "text-slate-500")}>今日学习 {buddy.todayHours}h</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Chat Area */}
        <Card className={cn("col-span-8 flex flex-col", isDark && "bg-slate-800/50 border-slate-700")} style={{ height: 'calc(100vh - 180px)' }}>
          <div className={cn("p-4 border-b flex items-center justify-between", isDark && "border-slate-700")}>
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-500 flex items-center justify-center text-lg text-white">{selectedBuddy.avatar}</div>
                <div className={cn("absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-white",
                  selectedBuddy.status === 'online' && 'bg-emerald-500', selectedBuddy.status === 'studying' && 'bg-amber-500')} />
              </div>
              <div>
                <p className={cn("font-medium text-sm", isDark ? "text-white" : "")}>{selectedBuddy.name}</p>
                <p className="text-xs text-emerald-600">{selectedBuddy.status === 'online' ? '在线' : '学习中'}</p>
              </div>
            </div>
            <Button size="sm" className="gap-2 bg-emerald-500 hover:bg-emerald-600"><Play className="w-3.5 h-3.5" />一起学习</Button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.map((msg) => (
              <div key={msg.id} className={cn("flex gap-2", msg.type === 'user' && "justify-end")}>
                {msg.type === 'buddy' && <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-500 flex items-center justify-center text-sm text-white shrink-0">{selectedBuddy.avatar}</div>}
                <div className={cn("max-w-[70%] px-4 py-2.5 rounded-2xl text-sm",
                  msg.type === 'user' ? "bg-emerald-500 text-white rounded-br-md" : isDark ? "bg-slate-700 text-slate-100 rounded-bl-md" : "bg-slate-100 text-slate-900 rounded-bl-md")}>
                  <p dangerouslySetInnerHTML={{ __html: msg.content }} />
                  <p className={cn("text-[10px] mt-1", msg.type === 'user' ? "text-emerald-200" : isDark ? "text-slate-500" : "text-slate-400")}>{msg.time}</p>
                </div>
              </div>
            ))}
          </div>

          <div className={cn("p-4 border-t", isDark && "border-slate-700")}>
            <div className="flex gap-2">
              <Button variant="ghost" size="icon" className="shrink-0"><Smile className={cn("w-5 h-5", isDark ? "text-slate-400" : "text-slate-400")} /></Button>
              <Input placeholder="和搭子说点什么..." value={inputMessage} onChange={(e) => setInputMessage(e.target.value)} onKeyPress={handleKeyPress}
                className={cn("flex-1", isDark && "bg-slate-700 border-slate-600")} />
              <Button size="icon" className="shrink-0 bg-emerald-500 hover:bg-emerald-600" onClick={handleSend}><Send className="w-4 h-4" /></Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
