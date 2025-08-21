export interface BotConfig {
  lowest_price: number
  volume: number
  screenshot_delay: number
  debug_mode: boolean
  target_schema_index: number
  name: string
}

export interface BotConfigOpt {
  lowest_price?: number
  volume?: number
  screenshot_delay?: number
  debug_mode?: boolean
  target_schema_index?: number
  name?: string
}

export interface BotStatus {
  status: "started" | "stopped"
}

export interface ApiResponse<T = any> {
  data?: T
  error?: string
}
