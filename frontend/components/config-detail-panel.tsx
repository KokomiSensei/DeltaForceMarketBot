"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Settings, Plus } from "lucide-react"
import type { BotConfig } from "@/types/bot-config"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { BotConfigForm } from "./bot-config-form"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface ConfigDetailPanelProps {
  selectedConfig: BotConfig | null
  onConfigUpdate: () => void
}

export function ConfigDetailPanel({ selectedConfig, onConfigUpdate }: ConfigDetailPanelProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleUpdateConfig = async (config: BotConfig) => {
    if (!selectedConfig) return

    setLoading(true)
    try {
      await apiClient.updateConfig(selectedConfig.name, config)
      onConfigUpdate()
      setIsEditing(false)
      toast({
        title: "Success",
        description: "Configuration updated successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update configuration.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateConfig = async (config: BotConfig) => {
    setLoading(true)
    try {
      await apiClient.createConfig(config)
      onConfigUpdate()
      setIsCreating(false)
      toast({
        title: "Success",
        description: "Configuration created successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create configuration.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSetAsActive = async () => {
    if (!selectedConfig) return

    setLoading(true)
    try {
      await apiClient.setBotConfig(selectedConfig)
      toast({
        title: "Success",
        description: "Configuration set as active.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to set configuration as active.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  if (!selectedConfig) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Settings className="h-16 w-16 mx-auto text-muted-foreground" />
          <div>
            <h3 className="text-lg font-medium mb-2">No Configuration Selected</h3>
            <p className="text-muted-foreground mb-4">
              Select a configuration from the sidebar to view and edit its settings.
            </p>
            <Dialog open={isCreating} onOpenChange={setIsCreating}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create New Configuration
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create New Configuration</DialogTitle>
                  <DialogDescription>Create a new bot configuration with your desired settings.</DialogDescription>
                </DialogHeader>
                <BotConfigForm onSubmit={handleCreateConfig} loading={loading} />
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold">{selectedConfig.name}</h1>
            {selectedConfig.debug_mode && <Badge variant="outline">Debug Mode</Badge>}
          </div>
          <p className="text-muted-foreground">Configure the bot settings and parameters</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleSetAsActive} disabled={loading}>
            Set as Active
          </Button>
          <Button onClick={() => setIsEditing(true)}>
            <Settings className="h-4 w-4 mr-2" />
            Edit Configuration
          </Button>
        </div>
      </div>

      {/* Configuration Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Basic Settings</CardTitle>
            <CardDescription>Core configuration parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="font-medium">Configuration Name</span>
              <span className="text-muted-foreground">{selectedConfig.name}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-medium">Lowest Price</span>
              <span className="text-muted-foreground">{selectedConfig.lowest_price}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-medium">Volume</span>
              <span className="text-muted-foreground">{selectedConfig.volume}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Advanced Settings</CardTitle>
            <CardDescription>Technical configuration options</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="font-medium">Screenshot Delay</span>
              <span className="text-muted-foreground">{selectedConfig.screenshot_delay}ms</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-medium">Target Schema Index</span>
              <span className="text-muted-foreground">{selectedConfig.target_schema_index}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-medium">Debug Mode</span>
              <Badge variant={selectedConfig.debug_mode ? "default" : "secondary"}>
                {selectedConfig.debug_mode ? "Enabled" : "Disabled"}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Edit Dialog */}
      <Dialog open={isEditing} onOpenChange={setIsEditing}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Configuration</DialogTitle>
            <DialogDescription>Modify the settings for "{selectedConfig.name}"</DialogDescription>
          </DialogHeader>
          <BotConfigForm config={selectedConfig} onSubmit={handleUpdateConfig} loading={loading} />
        </DialogContent>
      </Dialog>
    </div>
  )
}
