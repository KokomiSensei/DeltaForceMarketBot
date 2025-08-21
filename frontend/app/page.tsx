"use client"

import { useState, useEffect } from "react"
import { BotControlPanel } from "@/components/bot-control-panel"
import { ConfigSidebar } from "@/components/config-sidebar"
import { ConfigDetailPanel } from "@/components/config-detail-panel"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogFooter, DialogTitle } from "@/components/ui/dialog"
import type { BotConfig, BotConfigOpt } from "@/types/bot-config"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { Bot, Settings, Save } from "lucide-react"

export default function HomePage() {
  const [currentConfig, setCurrentConfig] = useState<BotConfig | null>(null)
  const [selectedConfig, setSelectedConfig] = useState<BotConfig | null>(null)
  const [tempConfig, setTempConfig] = useState<BotConfigOpt | null>(null)
  const [isDirty, setIsDirty] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [loading, setLoading] = useState(true)
  const [configKey, setConfigKey] = useState(0) // Force re-render of sidebar
  const [activeTab, setActiveTab] = useState("config") // Track active tab - config or control
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState(false)
  const [isSaveAsDialogOpen, setIsSaveAsDialogOpen] = useState(false)
  const [newConfigName, setNewConfigName] = useState("")
  const { toast } = useToast()

  useEffect(() => {
    loadCurrentConfig()
  }, [])

  // Initialize tempConfig when currentConfig changes
  useEffect(() => {
    if (currentConfig) {
      setTempConfig(currentConfig)
      setIsDirty(false)
    }
  }, [currentConfig])

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

  // Handle sidebar config selection based on active tab
  const handleSelectConfig = (config: BotConfig) => {
    setSelectedConfig(config)

    // If we're on the Control Panel tab, also load this config to the bot
    if (activeTab === "control") {
      handleSetConfig(config)
    }
  }

  // Handle changes to temporary configuration
  const handleTempConfigChange = (field: keyof BotConfigOpt, value: any) => {
    if (!tempConfig || !currentConfig) return

    const updatedConfig = { ...tempConfig, [field]: value }
    setTempConfig(updatedConfig)

    // Check if any field is different from the current config
    const isDifferent = Object.keys(updatedConfig).some((key) => {
      const k = key as keyof BotConfigOpt
      return updatedConfig[k] !== currentConfig[k as keyof BotConfig]
    })

    setIsDirty(isDifferent)
  }

  // Apply temporary configuration to the bot
  const handleApplyTempConfig = async () => {
    if (!tempConfig || !isDirty) return

    try {
      await apiClient.setBotConfig(tempConfig as BotConfig)

      // Check if name has changed, which requires a save as operation
      if (tempConfig.name !== currentConfig?.name) {
        setIsSaveAsDialogOpen(true)
        setNewConfigName(tempConfig.name || "")
      } else {
        // Name hasn't changed, just load the new config
        await loadCurrentConfig()
        setIsDirty(false)

        toast({
          title: "Success",
          description: "Bot configuration applied successfully.",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to apply configuration.",
        variant: "destructive",
      })
    }
  }

  // Handle saving the current configuration
  const handleSaveConfig = async () => {
    if (!tempConfig || !currentConfig) return

    try {
      // If name is the same, update the existing config
      if (tempConfig.name === currentConfig.name) {
        await apiClient.updateConfig(currentConfig.name, tempConfig as BotConfig)
        toast({
          title: "Success",
          description: "Configuration saved successfully.",
        })
      } else {
        // If name is different, create a new config
        await apiClient.createConfig(tempConfig as BotConfig)
        toast({
          title: "Success",
          description: "New configuration created successfully.",
        })
      }

      setIsSaveDialogOpen(false)
      setIsDirty(false)
      handleConfigChange() // Refresh configs list
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save configuration.",
        variant: "destructive",
      })
    }
  }

  // Handle saving the config with a new name
  const handleSaveAsConfig = async () => {
    if (!tempConfig) return

    try {
      const configToSave = { ...tempConfig, name: newConfigName }
      await apiClient.createConfig(configToSave as BotConfig)

      toast({
        title: "Success",
        description: "New configuration created successfully.",
      })

      setIsSaveAsDialogOpen(false)
      setIsDirty(false)
      handleConfigChange() // Refresh configs list
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save configuration.",
        variant: "destructive",
      })
    }
  }

  const handleSetConfig = async (config: BotConfig) => {
    try {
      const updatedConfig = await apiClient.setBotConfig(config)
      setCurrentConfig(updatedConfig)
      setTempConfig(updatedConfig)
      setIsDirty(false)
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
            {/* {currentConfig && (
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
            )} */}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-120px)]">
        {/* Sidebar */}
        <ConfigSidebar
          key={configKey}
          selectedConfig={selectedConfig}
          onSelectConfig={handleSelectConfig}
          onConfigChange={handleConfigChange}
        />

        {/* Main Panel */}
        <div className="flex-1 flex flex-col">
          <Tabs
            defaultValue="config"
            className="flex-1 flex flex-col"
            value={activeTab}
            onValueChange={setActiveTab}
          >
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
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                      <div>
                        <CardTitle>Current Active Configuration: { currentConfig.name }</CardTitle>
                        <CardDescription>Adjust and apply settings to the bot</CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleApplyTempConfig}
                          disabled={!isDirty || !tempConfig}
                        >
                          Apply Changes
                        </Button>
                        <Button
                          variant="default"
                          size="sm"
                          onClick={() => {
                            // If name is changed, open Save As dialog, otherwise open Save dialog
                            if (tempConfig?.name !== currentConfig?.name) {
                              setNewConfigName(tempConfig?.name || "")
                              setIsSaveAsDialogOpen(true)
                            } else {
                              setIsSaveDialogOpen(true)
                            }
                          }}
                          disabled={!isDirty || !tempConfig}
                        >
                          Save
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Basic Settings */}
                        <div className="space-y-4">
                          {/* <div className="space-y-1.5">
                            <Label htmlFor="config-name">Configuration Name</Label>
                            <Input
                              id="config-name"
                              value={tempConfig?.name || currentConfig.name}
                              onChange={(e) => handleTempConfigChange('name', e.target.value)}
                            />
                          </div> */}
                          <div className="space-y-1.5">
                            <Label htmlFor="lowest-price">Lowest Price</Label>
                            <Input
                              id="lowest-price"
                              type="number"
                              value={tempConfig?.lowest_price ?? currentConfig.lowest_price}
                              onChange={(e) => handleTempConfigChange('lowest_price', Number(e.target.value))}
                            />
                          </div>
                          <div className="space-y-1.5">
                            <Label htmlFor="volume">Volume</Label>
                            <Input
                              id="volume"
                              type="number"
                              value={tempConfig?.volume ?? currentConfig.volume}
                              onChange={(e) => handleTempConfigChange('volume', Number(e.target.value))}
                            />
                          </div>
                        </div>

                        {/* Advanced Settings */}
                        <div className="space-y-4">
                          <div className="space-y-1.5">
                            <Label htmlFor="screenshot-delay">Screenshot Delay (ms)</Label>
                            <Input
                              id="screenshot-delay"
                              type="number"
                              value={tempConfig?.screenshot_delay ?? currentConfig.screenshot_delay}
                              onChange={(e) => handleTempConfigChange('screenshot_delay', Number(e.target.value))}
                            />
                          </div>
                          <div className="space-y-1.5">
                            <div className="flex items-center justify-between">
                              <Label htmlFor="debug-mode" className="cursor-pointer">Debug Mode</Label>
                              <Switch
                                id="debug-mode"
                                checked={tempConfig?.debug_mode ?? currentConfig.debug_mode}
                                onCheckedChange={(checked) => handleTempConfigChange('debug_mode', checked)}
                              />
                            </div>
                          </div>
                          <div className="space-y-1.5">
                            <div>
                              <div className="flex justify-between">
                                <Label htmlFor="schema-index">Target Schema Index</Label>
                                <span className="text-sm text-muted-foreground">
                                  {tempConfig?.target_schema_index ?? currentConfig.target_schema_index}
                                </span>
                              </div>
                              <Slider
                                id="schema-index"
                                min={0}
                                max={4}
                                step={1}
                                value={[(tempConfig?.target_schema_index ?? currentConfig.target_schema_index)]}
                                onValueChange={(value) => handleTempConfigChange('target_schema_index', value[0])}
                                className="py-4"
                              />
                              <div className="flex justify-between text-xs text-muted-foreground">
                                <span>0</span>
                                <span>1</span>
                                <span>2</span>
                                <span>3</span>
                                <span>4</span>
                              </div>
                            </div>
                          </div>
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

      {/* Save Dialog */}
      <Dialog open={isSaveDialogOpen} onOpenChange={setIsSaveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save Configuration</DialogTitle>
            <DialogDescription>
              Do you want to save the current changes to the configuration?
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p>Your changes will be saved to the configuration "{tempConfig?.name}".</p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsSaveDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSaveConfig}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Save As Dialog */}
      <Dialog open={isSaveAsDialogOpen} onOpenChange={setIsSaveAsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save As New Configuration</DialogTitle>
            <DialogDescription>
              Enter a name for the new configuration.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="space-y-1.5">
              <Label htmlFor="new-config-name">Configuration Name</Label>
              <Input
                id="new-config-name"
                value={newConfigName}
                onChange={(e) => setNewConfigName(e.target.value)}
                autoFocus
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsSaveAsDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSaveAsConfig} disabled={!newConfigName}>Save As</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
