import { type NextRequest, NextResponse } from "next/server"
import type { BotConfig } from "@/types/bot-config"

// Mock configurations storage (shared with other routes)
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

export async function POST(request: NextRequest, { params }: { params: { configName: string; newName: string } }) {
  try {
    const { configName, newName } = params

    // Find existing configuration
    const existingIndex = savedConfigs.findIndex((c) => c.name === configName)
    if (existingIndex === -1) {
      return NextResponse.json({ error: "Configuration not found" }, { status: 404 })
    }

    // Check if new name already exists
    const nameExists = savedConfigs.some((c) => c.name === newName)
    if (nameExists) {
      return NextResponse.json({ error: "Configuration with new name already exists" }, { status: 409 })
    }

    // Rename configuration
    savedConfigs[existingIndex].name = newName

    return NextResponse.json({})
  } catch (error) {
    return NextResponse.json({ error: "Failed to rename configuration" }, { status: 500 })
  }
}
