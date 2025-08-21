import { type NextRequest, NextResponse } from "next/server"
import type { BotConfig, BotConfigOpt } from "@/types/bot-config"

// Mock data storage (in production, this would be a database)
let currentBotConfig: BotConfig = {
  name: "Default Bot",
  lowest_price: 100,
  volume: 1000,
  screenshot_delay: 2000,
  debug_mode: false,
  target_schema_index: 0,
}

export async function GET() {
  try {
    return NextResponse.json(currentBotConfig)
  } catch (error) {
    return NextResponse.json({ error: "Failed to get bot configuration" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const config: BotConfig = await request.json()

    // Validate required fields
    if (!config.name) {
      return NextResponse.json({ error: "Bot name is required" }, { status: 400 })
    }

    // Complete replacement of configuration
    currentBotConfig = { ...config }

    return NextResponse.json(currentBotConfig)
  } catch (error) {
    return NextResponse.json({ error: "Failed to set bot configuration" }, { status: 500 })
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const configOpt: BotConfigOpt = await request.json()

    // Partial update of configuration
    const updatedConfig = { ...currentBotConfig }

    // Update only provided fields
    Object.keys(configOpt).forEach((key) => {
      const value = configOpt[key as keyof BotConfigOpt]
      if (value !== undefined && value !== null) {
        ;(updatedConfig as any)[key] = value
      }
    })

    currentBotConfig = updatedConfig

    return NextResponse.json(currentBotConfig)
  } catch (error) {
    return NextResponse.json({ error: "Failed to update bot configuration" }, { status: 500 })
  }
}
