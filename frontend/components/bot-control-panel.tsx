"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Play, Square, Settings } from "lucide-react"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface BotControlPanelProps {
  isRunning: boolean
  onStatusChange: (running: boolean) => void
}

export function BotControlPanel({ isRunning, onStatusChange }: BotControlPanelProps) {
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleStart = async () => {
    setLoading(true)
    try {
      await apiClient.startBot()
      onStatusChange(true)
      toast({
        title: "Bot Started",
        description: "The bot has been started successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start the bot.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    try {
      await apiClient.stopBot()
      onStatusChange(false)
      toast({
        title: "Bot Stopped",
        description: "The bot has been stopped successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to stop the bot.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Bot Control Panel
        </CardTitle>
        <CardDescription>Start, stop, and monitor your bot</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Status:</span>
            <Badge variant={isRunning ? "default" : "secondary"}>{isRunning ? "Running" : "Stopped"}</Badge>
          </div>
        </div>

        <div className="flex gap-2">
          <Button onClick={handleStart} disabled={loading || isRunning} className="flex-1" variant="default">
            <Play className="h-4 w-4 mr-2" />
            Start Bot
          </Button>
          <Button
            onClick={handleStop}
            disabled={loading || !isRunning}
            className="flex-1 bg-transparent"
            variant="outline"
          >
            <Square className="h-4 w-4 mr-2" />
            Stop Bot
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
