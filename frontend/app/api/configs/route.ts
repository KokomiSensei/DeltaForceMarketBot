import { type NextRequest, NextResponse } from "next/server"
import type { BotConfig } from "@/types/bot-config"

// Mock configurations storage (in production, this would be a database)
const savedConfigs: BotConfig[] = [
  {
    name: "Production Config",
    lowest_price: 150,
    volume: 2000,
    screenshot_delay: 1500,
    debug_mode: false,
    target_schema_index: 1,
  },
  {
    name: "Development Config",
    lowest_price: 50,
    volume: 500,
    screenshot_delay: 3000,
    debug_mode: true,
    target_schema_index: 0,
  },
]

export async function GET() {
  try {
    return NextResponse.json(savedConfigs)
  } catch (error) {
    return NextResponse.json({ error: "Failed to get configurations" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const config: BotConfig = await request.json()

    // Validate required fields
    if (!config.name) {
      return NextResponse.json({ error: "Configuration name is required" }, { status: 400 })
    }

    // Check if config with same name already exists
    const existingIndex = savedConfigs.findIndex((c) => c.name === config.name)
    if (existingIndex !== -1) {
      return NextResponse.json({ error: "Configuration with this name already exists" }, { status: 409 })
    }

    // Add new configuration
    savedConfigs.push(config)

    return NextResponse.json(config)
  } catch (error) {
    return NextResponse.json({ error: "Failed to create configuration" }, { status: 500 })
  }
}
