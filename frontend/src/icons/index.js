import { 
  House, List, Plus, DataLine, Monitor, ChatDotRound, 
  ArrowDown, ArrowRight, Cpu, DataAnalysis, Timer, 
  Setting, QuestionFilled, Delete, Search, Edit, 
  Connection, DocumentCopy, Goods, GoodsFilled, 
  ChatSquare, Upload, Microphone, Position, More, 
  User, Switch, Open, VideoPlay, Download, Picture, 
  Clock, Refresh, NewIcon
} from '@element-plus/icons-vue'

// 自定义图标组件映射
export const iconMap = {
  'icon-house': House,
  'icon-list': List,
  'icon-plus': Plus,
  'icon-data-line': DataLine,
  'icon-monitor': Monitor,
  'icon-chat-dot-round': ChatDotRound,
  'icon-arrow-down': ArrowDown,
  'icon-arrow-right': ArrowRight,
  'icon-cpu': Cpu,
  'icon-data-analysis': DataAnalysis,
  'icon-timer': Timer,
  'icon-setting': Setting,
  'icon-question-filled': QuestionFilled,
  'icon-delete': Delete,
  'icon-search': Search,
  'icon-edit': Edit,
  'icon-connection': Connection,
  'icon-document-copy': DocumentCopy,
  'icon-thumb-up': Goods,
  'icon-thumb-down': GoodsFilled,
  'icon-chat-square': ChatSquare,
  'icon-upload': Upload,
  'icon-microphone': Microphone,
  'icon-position': Position,
  'icon-more': More,
  'icon-user': User,
  'icon-switch': Switch,
  'icon-open': Open,
  'icon-video-play': VideoPlay,
  'icon-download': Download,
  'icon-picture': Picture,
  'icon-time': Clock,
  'icon-refresh': Refresh,
  'icon-new-name': NewIcon
}

// 注册所有图标
export function registerIcons(app) {
  for (const [name, component] of Object.entries(iconMap)) {
    app.component(name, component)
  }
} 