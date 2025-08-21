"use client"

import { useState, useEffect } from "react"
import { BotControlPanel } from "@/components/bot-control-panel"
import { ConfigSidebar } from "@/components/config-sidebar"
import { ConfigDetailPanel } from "@/components/config-detail-panel"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { BotConfig } from "@/types/bot-config"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { Bot, Settings } from "lucide-react"

export default function HomePage() {
  const [currentConfig, setCurrentConfig] = useState<BotConfig | null>(null)
  const [selectedConfig, setSelectedConfig] = useState<BotConfig | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [loading, setLoading] = useState(true)
  const [configKey, setConfigKey] = useState(0) // Force re-render of sidebar
  const { toast } = useToast()

  useEffect(() => {
    loadCurrentConfig()
  }, [])

  const loadCurrentConfig = async () => {
    try {
      const config = await apiClient.getBotConfig()
      setCurrentConfig(config)
    } catch (error) {
      console.log("No current config found or backend not available")
    } finally {
      setLoading(false)
    }
  }

  const handleConfigChange = () => {
    setConfigKey((prev) => prev + 1)
    loadCurrentConfig()
  }

  const handleSetConfig = async (config: BotConfig) => {
    try {
      const updatedConfig = await apiClient.setBotConfig(config)
      setCurrentConfig(updatedConfig)
      toast({
        title: "Success",
        description: "Bot configuration updated successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update bot configuration.",
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Bot className="h-12 w-12 mx-auto mb-4 animate-pulse" />
          <p>Loading bot dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-8 w-8" />
              <div>
                <h1 className="text-xl font-bold">Bot Configuration Dashboard</h1>
                <p className="text-sm text-muted-foreground">Manage your bot settings and configurations</p>
              </div>
            </div>

            {/* Current Config Status */}
            {currentConfig && (
              <Card className="w-64">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Active Configuration</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{currentConfig.name}</span>
                    <div className="flex items-center gap-2">
                      <div className={`h-2 w-2 rounded-full ${isRunning ? "bg-green-500" : "bg-gray-400"}`} />
                      <span className="text-xs text-muted-foreground">{isRunning ? "Running" : "Stopped"}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-120px)]">
        {/* Sidebar */}
        <ConfigSidebar
          key={configKey}
          selectedConfig={selectedConfig}
          onSelectConfig={setSelectedConfig}
          onConfigChange={handleConfigChange}
        />

        {/* Main Panel */}
        <div className="flex-1 flex flex-col">
          <Tabs defaultValue="config" className="flex-1 flex flex-col">
            <div className="border-b px-6 py-2">
              <TabsList>
                <TabsTrigger value="config" className="flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  Configuration
                </TabsTrigger>
                <TabsTrigger value="control" className="flex items-center gap-2">
                  <Bot className="h-4 w-4" />
                  Control Panel
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="config" className="flex-1 m-0">
              <ConfigDetailPanel selectedConfig={selectedConfig} onConfigUpdate={handleConfigChange} />
            </TabsContent>

            <TabsContent value="control" className="flex-1 m-0 p-6">
              <div className="max-w-4xl mx-auto space-y-6">
                <BotControlPanel isRunning={isRunning} onStatusChange={setIsRunning} />

                {currentConfig && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Current Active Configuration</CardTitle>
                      <CardDescription>Settings currently being used by the bot</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div className="flex justify-between">
                          <span className="font-medium">Name:</span>
                          <span>{currentConfig.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="font-medium">Lowest Price:</span>
                          <span>{currentConfig.lowest_price}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="font-medium">Volume:</span>
                          <span>{currentConfig.volume}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="font-medium">Screenshot Delay:</span>
                          <span>{currentConfig.screenshot_delay}ms</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="font-medium">Debug Mode:</span>
                          <span>{currentConfig.debug_mode ? "Enabled" : "Disabled"}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="font-medium">Schema Index:</span>
                          <span>{currentConfig.target_schema_index}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
