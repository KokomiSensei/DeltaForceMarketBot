"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Trash2, Edit, Plus } from "lucide-react"
import type { BotConfig } from "@/types/bot-config"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { BotConfigForm } from "./bot-config-form"

export function ConfigManager() {
  const [configs, setConfigs] = useState<BotConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedConfig, setSelectedConfig] = useState<BotConfig | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      const data = await apiClient.getAllConfigs()
      setConfigs(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load configurations.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateConfig = async (config: BotConfig) => {
    try {
      await apiClient.createConfig(config as BotConfig)
      await loadConfigs()
      setIsDialogOpen(false)
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
    }
  }

  const handleUpdateConfig = async (config: BotConfig) => {
    if (!selectedConfig) return

    try {
      await apiClient.updateConfig(selectedConfig.name, config as BotConfig)
      await loadConfigs()
      setIsDialogOpen(false)
      setSelectedConfig(null)
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
    }
  }

  const handleDeleteConfig = async (name: string) => {
    try {
      await apiClient.deleteConfig(name)
      await loadConfigs()
      toast({
        title: "Success",
        description: "Configuration deleted successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete configuration.",
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading configurations...</div>
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Configuration Manager</CardTitle>
            <CardDescription>Manage your bot configurations</CardDescription>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => setIsCreating(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Config
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>{isCreating ? "Create New Configuration" : "Edit Configuration"}</DialogTitle>
                <DialogDescription>
                  {isCreating ? "Create a new bot configuration" : "Modify the selected configuration"}
                </DialogDescription>
              </DialogHeader>
              <BotConfigForm
                config={isCreating ? undefined : selectedConfig || undefined}
                onSubmit={isCreating ? handleCreateConfig : handleUpdateConfig}
              />
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {configs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No configurations found. Create your first configuration to get started.
            </div>
          ) : (
            configs.map((config) => (
              <div key={config.name} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-medium">{config.name}</h3>
                    {config.debug_mode && <Badge variant="outline">Debug</Badge>}
                  </div>
                  <div className="text-sm text-muted-foreground grid grid-cols-2 md:grid-cols-4 gap-2">
                    <span>Price: {config.lowest_price}</span>
                    <span>Volume: {config.volume}</span>
                    <span>Delay: {config.screenshot_delay}ms</span>
                    <span>Schema: {config.target_schema_index}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setSelectedConfig(config)
                      setIsCreating(false)
                      setIsDialogOpen(true)
                    }}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleDeleteConfig(config.name)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
