# StudyBuddy Workspace Briefing

## SNAPSHOT

type: single  
langs: Python, HTML, CSS, JavaScript  
runtimes: Python 3.10+, Flask 3.0  
pkgManager: pip  
deliverables: Flask web app at localhost:5000  
rootConfigs: requirements.txt, config.py, app.py  

---

## STRUCTURE

`wee37/app.py` → Flask server, 43 routes, session management  
`wee37/config.py` → Global config, AI models, emotions, paths  
`wee37/requirements.txt` → Flask, requests  
`wee37/src/` → Python modules (ai, core, modules)  
`wee37/src/core/` → Buddy (emotion), Timer (study), Supervisor (monitoring)  
`wee37/src/ai/` → AI helper (Ollama/OpenAI, conversation mgmt)  
`wee37/src/modules/` → TaskManager, StudyCalendar, DataManager, AIMemory, Achievements, PlanGenerator  
`wee37/templates/` → index.html (main UI), ai-assistant.html component  
`wee37/data/` → JSON persistence (tasks, ai_history, user_settings, study_log)  

---

## ARCHITECTURE

### app.py (wee37/app.py)

entry: Flask app, port 5000  
routing:  
  - `GET /` → render index.html  
  - `POST /api/ask` → AI question answering  
  - `POST /api/study/start|pause|stop` → Timer control  
  - `POST /api/tasks` (GET/POST/PUT/DELETE) → Task CRUD  
  - `GET /api/calendar/*` → Study calendar stats  
  - `GET /api/achievements` → Achievement data  
  - `POST /api/plans/*` → Study plan management  
  - `GET|POST /api/motto`, `/api/favorite_quote` → User settings  

state: `Session` class per session_id; holds Buddy, StudySupervisor, StudyTimer, thread lock  
api: RESTful JSON, params via query string + request.json  
db: JSON files in data/  
auth: None (local app)  
build: Flask development server  
dirs: templates/→HTML, src/→modules, data/→persistence, docs/→reference  

### src/core/buddy.py → Emotion management

Buddy class: tracks emotion state (idle|happy|sad|study|thinking|angry|excited|sleepy|proud)  
Methods: set_emotion, update_by_action, update_by_supervisor, check_time_based_emotion  
Integrates: TaskManager, StudyCalendar  
Emojis: config.EMOJIS dict  

### src/core/timer.py → Study timing & monitoring

StudyTimer: start, stop, pause, get_current_duration, get_remaining  
StudySupervisor: pomodoro cycles, break tracking, daily goal monitoring, status_dict  
Methods: start_pomodoro, start_break, end_session, get_status  

### src/ai/ai_helper.py → LLM integration

StudyPalAI: ask_ai_with_context, conversation history management, context limiting  
Supports: Ollama (local) or OpenAI-compatible APIs  
Integrates: AIMemory for persistence  
System prompt: encouraging tutor persona  
Model config: dict in config.py, default qwen3.5:9b  

### src/modules/data_manager.py → Persistence layer

DataManager: load/save JSON, get/set motto, favorite_quote, daily_goal  
Files: data/user_settings.json (motto, quote, goal, timestamps)  
Singleton: get_data_manager() for global access  

### src/modules/task_manager.py → Task CRUD

Task class: id, title, description, deadline, completed flag, created_at  
TaskManager: create, get_all, mark_complete, delete, get_reminders  
Data: data/tasks.json  

### src/modules/study_calendar.py → Activity tracking

StudyCalendar: log_study_session, get_stats (total_time, streak, today_time)  
Heatmap data: data/study_log.json, data/calendar.json  

### src/modules/ai_memory.py → Conversation persistence

AIMemory: store/load conversation history  
File: data/ai_history.json  
Ops: new_conversation, get_conversations, add_message, delete_conversation  

### src/modules/achievements.py → Gamification

AchievementManager: unlock, check_achievements, get_achievements_data  
Categories: pomodoro, streak, study_time, consistency  
Triggers: automatic on session completion  

### src/modules/plan_generator.py → Study planning

PlanGenerator: generate_daily_plan, generate_study_schedule  
Input: subject, duration, study_level  
Output: structured plan with milestones  

### templates/index.html

Main SPA, ~3700 lines  
Sections: timer, buddy display, chat UI, task list, calendar, achievements  
Events: AJAX calls to /api/* endpoints  

---

## DEPENDENCY GRAPH

app.py → core (Buddy, StudyTimer, StudySupervisor) → modules (TaskManager, StudyCalendar)  
app.py → ai (ask_ai_with_context) → ai_memory (AIMemory)  
app.py → modules (DataManager, achievements, etc.)  
Buddy → TaskManager, StudyCalendar  
StudySupervisor → Buddy (update_by_supervisor)  

---

## STACK

Python 3.10+ | Flask 3.0 | requests 2.31.0  
AI: Ollama (local) or OpenAI-compatible APIs  
Frontend: Vanilla JS, HTML5, CSS3 (no frameworks)  
Persistence: JSON files  
Concurrency: threading for session management  

---

## STYLE

- naming: snake_case for functions/vars, PascalCase for classes  
- imports: full module paths, lazy loading for circular refs (e.g., AIMemory)  
- typing: sparse type hints, docstrings with param descriptions  
- errors: try/except with JSON error responses  
- patterns: Singleton for DataManager, StudySupervisor, AchievementManager  
- config: centralized in config.py (MODELS_CONFIG, paths, defaults)  

---

## BUILD

workspaceScripts: None (app.py is entry point)  
envFiles: None (.env optional)  
envPrefixes: None (config.py has hardcoded defaults)  
ci: None (local development)  
docker: None  

---

## KEY FILES

`wee37::app.py` → Flask server, 43 routes, all API endpoints, session orchestration | modify for new endpoints | Session class, route logic  
`wee37::config.py` → Global configuration, model selection, paths, emoji definitions | check before running | all modules import from here  
`wee37::src/core/buddy.py` → Emotion state machine, buddy interaction logic | emotion updates, state transitions | AI and UI responses depend on emotion  
`wee37::src/core/timer.py` → Study timing, pomodoro cycles, supervisor feedback | timer state, session completion | triggers achievement checks, emotion updates  
`wee37::src/ai/ai_helper.py` → LLM integration, conversation context management | model selection, prompt engineering | all AI responses flow through here  
`wee37::src/modules/data_manager.py` → User settings persistence | JSON I/O, default values | accessed by buddy, app routes  
`wee37::src/modules/task_manager.py` → Task CRUD operations | task storage, reminders, deadlines | buddy emotion responds to task state  
`wee37::src/modules/achievements.py` → Achievement unlock logic | scoring, criteria, serialization | triggered after study sessions  
`wee37::templates/index.html` → Frontend UI, AJAX client, realtime status display | DOM structure, event bindings | all user interactions originate here  

---

## LOOKUP

add AI model support → config.py (MODELS_CONFIG), src/ai/ai_helper.py (provider logic)  
add study session route → app.py (/api/study/* handlers), src/core/timer.py (logic)  
add emotion state → config.py (EMOJIS), src/core/buddy.py (state machine)  
add task reminder → src/modules/task_manager.py (get_reminders), app.py (/api/tasks/reminders)  
add UI feature → templates/index.html (DOM + event handler), app.py (matching /api/ endpoint)  
add data persistence field → src/modules/data_manager.py (DataManager.data dict), data/*.json file  
add achievement type → src/modules/achievements.py (AchievementManager), config.py (criteria)  
add session state tracking → app.py (Session class), src/core/buddy.py (tracking methods)  
