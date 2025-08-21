import { type NextRequest, NextResponse } from "next/server"
import type { BotConfig } from "@/types/bot-config"

// Mock configurations storage (shared with route.ts)
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

export async function PUT(request: NextRequest, { params }: { params: { configName: string } }) {
  try {
    const config: BotConfig = await request.json()
    const { configName } = params

    // Find existing configuration
    const existingIndex = savedConfigs.findIndex((c) => c.name === configName)
    if (existingIndex === -1) {
      return NextResponse.json({ error: "Configuration not found" }, { status: 404 })
    }

    // Update configuration
    savedConfigs[existingIndex] = { ...config, name: configName }

    return NextResponse.json(savedConfigs[existingIndex])
  } catch (error) {
    return NextResponse.json({ error: "Failed to update configuration" }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { configName: string } }) {
  try {
    const { configName } = params

    // Find existing configuration
    const existingIndex = savedConfigs.findIndex((c) => c.name === configName)
    if (existingIndex === -1) {
      return NextResponse.json({ error: "Configuration not found" }, { status: 404 })
    }

    // Remove configuration
    savedConfigs.splice(existingIndex, 1)

    return NextResponse.json({})
  } catch (error) {
    return NextResponse.json({ error: "Failed to delete configuration" }, { status: 500 })
  }
}
