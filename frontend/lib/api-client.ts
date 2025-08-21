import type { BotConfig, BotConfigOpt, BotStatus } from "@/types/bot-config"

// Direct all API calls to Python backend
const API_BASE_URL = (endpoint: string): string => {
  return `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:9876"}${endpoint}`
}

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = API_BASE_URL(endpoint)

    try {
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("API request failed:", error)
      throw error
    }
  }

  // Bot Configuration APIs
  async getBotConfig(): Promise<BotConfig> {
    return this.request<BotConfig>("/api/bot/config")
  }

  async setBotConfig(config: BotConfig): Promise<BotConfig> {
    return this.request<BotConfig>("/api/bot/config", {
      method: "POST",
      body: JSON.stringify(config),
    })
  }

  async updateBotConfig(config: BotConfigOpt): Promise<BotConfig> {
    return this.request<BotConfig>("/api/bot/config", {
      method: "PATCH",
      body: JSON.stringify(config),
    })
  }

  async startBot(): Promise<BotStatus> {
    return this.request<BotStatus>("/api/bot/start", {
      method: "POST",
    })
  }

  async stopBot(): Promise<BotStatus> {
    return this.request<BotStatus>("/api/bot/stop", {
      method: "POST",
    })
  }

  // Config Management APIs
  async getAllConfigs(): Promise<BotConfig[]> {
    return this.request<BotConfig[]>("/api/configs")
  }

  async createConfig(config: BotConfig): Promise<BotConfig> {
    return this.request<BotConfig>("/api/configs", {
      method: "POST",
      body: JSON.stringify(config),
    })
  }

  async updateConfig(name: string, config: BotConfig): Promise<BotConfig> {
    return this.request<BotConfig>(`/api/configs/${name}`, {
      method: "PUT",
      body: JSON.stringify(config),
    })
  }

  async deleteConfig(name: string): Promise<void> {
    return this.request<void>(`/api/configs/${name}`, {
      method: "DELETE",
    })
  }

  async renameConfig(oldName: string, newName: string): Promise<void> {
    return this.request<void>(`/api/configs/${oldName}/rename/${newName}`, {
      method: "POST",
    })
  }
}

export const apiClient = new ApiClient()
