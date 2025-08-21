"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Switch } from "@/components/ui/switch"
import { Trash2, Edit2, Search, Plus } from "lucide-react"
import type { BotConfig, BotConfigOpt } from "@/types/bot-config"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { BotConfigForm } from "@/components/bot-config-form"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface ConfigSidebarProps {
  selectedConfig: BotConfig | null
  onSelectConfig: (config: BotConfig) => void
  onConfigChange: () => void
}

export function ConfigSidebar({ selectedConfig, onSelectConfig, onConfigChange }: ConfigSidebarProps) {
  const [configs, setConfigs] = useState<BotConfig[]>([])
  const [filteredConfigs, setFilteredConfigs] = useState<BotConfig[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [loading, setLoading] = useState(true)
  const [renameDialog, setRenameDialog] = useState<{ open: boolean; config: BotConfig | null }>({
    open: false,
    config: null,
  })
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; config: BotConfig | null }>({
    open: false,
    config: null,
  })
  const [createDialog, setCreateDialog] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [newConfig, setNewConfig] = useState<BotConfig>({
    name: "",
    lowest_price: 100,
    volume: 1000,
    screenshot_delay: 1000,
    debug_mode: false,
    target_schema_index: 0,
  })
  const [newName, setNewName] = useState("")
  const { toast } = useToast()

  useEffect(() => {
    loadConfigs()
  }, [])

  useEffect(() => {
    const filtered = configs.filter((config) => config.name.toLowerCase().includes(searchQuery.toLowerCase()))
    setFilteredConfigs(filtered)
  }, [configs, searchQuery])

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

  const handleRename = async () => {
    if (!renameDialog.config || !newName.trim()) return

    try {
      await apiClient.renameConfig(renameDialog.config.name, newName.trim())
      await loadConfigs()
      onConfigChange()
      setRenameDialog({ open: false, config: null })
      setNewName("")
      toast({
        title: "Success",
        description: "Configuration renamed successfully.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to rename configuration.",
        variant: "destructive",
      })
    }
  }

  const handleCreateConfig = async (config: BotConfig | BotConfigOpt) => {
    try {
      // 确保这是一个完整的 BotConfig 对象
      const fullConfig = config as BotConfig
      await apiClient.createConfig(fullConfig)
      await loadConfigs()
      onConfigChange()
      setIsCreating(false)
      setCreateDialog(false)
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

  const handleDelete = async () => {
    if (!deleteDialog.config) return

    try {
      await apiClient.deleteConfig(deleteDialog.config.name)
      await loadConfigs()
      onConfigChange()
      setDeleteDialog({ open: false, config: null })
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
    return (
      <div className="w-80 border-r bg-muted/10 p-4">
        <div className="text-center py-8">Loading configurations...</div>
      </div>
    )
  }

  return (
    <div className="w-80 border-r bg-muted/10 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold">Configurations</h2>
          <Button size="sm" onClick={() => setIsCreating(true)}>
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search configurations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Config List */}
      <ScrollArea className="flex-1">
        <div className="p-2">
          {filteredConfigs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground text-sm">
              {searchQuery ? "No configurations match your search." : "No configurations found."}
            </div>
          ) : (
            <div className="space-y-1">
              {filteredConfigs.map((config) => (
                <div
                  key={config.name}
                  className={`group p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedConfig?.name === config.name
                      ? "bg-primary/10 border border-primary/20"
                      : "hover:bg-muted/50"
                  }`}
                  onClick={() => onSelectConfig(config)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-sm truncate">{config.name}</h3>
                        {config.debug_mode && (
                          <Badge variant="outline" className="text-xs">
                            Debug
                          </Badge>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground space-y-1">
                        <div>Price: {config.lowest_price}</div>
                        <div>Volume: {config.volume}</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0"
                        onClick={(e) => {
                          e.stopPropagation()
                          setRenameDialog({ open: true, config })
                          setNewName(config.name)
                        }}
                      >
                        <Edit2 className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                        onClick={(e) => {
                          e.stopPropagation()
                          setDeleteDialog({ open: true, config })
                        }}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Rename Dialog */}
      <Dialog open={renameDialog.open} onOpenChange={(open) => setRenameDialog({ open, config: null })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename Configuration</DialogTitle>
            <DialogDescription>Enter a new name for "{renameDialog.config?.name}"</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Configuration name"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleRename()
                }
              }}
            />
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setRenameDialog({ open: false, config: null })}>
                Cancel
              </Button>
              <Button onClick={handleRename} disabled={!newName.trim()}>
                Rename
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <AlertDialog open={deleteDialog.open} onOpenChange={(open) => setDeleteDialog({ open, config: null })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Configuration</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deleteDialog.config?.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* 删除旧的注释代码以保持文件简洁 */}

      {/* Create Dialog - 使用 BotConfigForm 组件 */}
      <Dialog open={isCreating} onOpenChange={setIsCreating}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New Configuration</DialogTitle>
            <DialogDescription>Create a new bot configuration with your desired settings.</DialogDescription>
          </DialogHeader>
          <BotConfigForm onSubmit={handleCreateConfig} loading={loading} />
        </DialogContent>
      </Dialog>
    </div>
  )
}
