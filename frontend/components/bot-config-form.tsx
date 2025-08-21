"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { BotConfig, BotConfigOpt } from "@/types/bot-config"

interface BotConfigFormProps {
  config?: BotConfig
  onSubmit: (config: BotConfig | BotConfigOpt) => Promise<void>
  isPartialUpdate?: boolean
  loading?: boolean
}

export function BotConfigForm({ config, onSubmit, isPartialUpdate = false, loading = false }: BotConfigFormProps) {
  const [formData, setFormData] = useState<BotConfig | BotConfigOpt>({
    name: config?.name || "",
    lowest_price: config?.lowest_price || 0,
    volume: config?.volume || 0,
    screenshot_delay: config?.screenshot_delay || 1000,
    debug_mode: config?.debug_mode || false,
    target_schema_index: config?.target_schema_index || 0,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSubmit(formData)
  }

  const handleInputChange = (field: keyof BotConfig, value: string | number | boolean) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{isPartialUpdate ? "Update Bot Configuration" : "Bot Configuration"}</CardTitle>
        <CardDescription>
          {isPartialUpdate ? "Modify specific bot settings" : "Configure bot parameters and settings"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Bot Name</Label>
              <Input
                id="name"
                value={formData.name || ""}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Enter bot name"
                required={!isPartialUpdate}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="lowest_price">Lowest Price</Label>
              <Input
                id="lowest_price"
                type="number"
                value={formData.lowest_price || ""}
                onChange={(e) => handleInputChange("lowest_price", Number.parseInt(e.target.value) || 0)}
                placeholder="Enter lowest price"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="volume">Volume</Label>
              <Input
                id="volume"
                type="number"
                value={formData.volume || ""}
                onChange={(e) => handleInputChange("volume", Number.parseInt(e.target.value) || 0)}
                placeholder="Enter volume"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="screenshot_delay">Screenshot Delay (ms)</Label>
              <Input
                id="screenshot_delay"
                type="number"
                value={formData.screenshot_delay || ""}
                onChange={(e) => handleInputChange("screenshot_delay", Number.parseInt(e.target.value) || 1000)}
                placeholder="Enter delay in milliseconds"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <Label htmlFor="target_schema_index">Target Schema Index</Label>
                <span className="text-sm text-muted-foreground">{formData.target_schema_index}</span>
              </div>
              <Slider
                id="target_schema_index"
                min={0}
                max={4}
                step={1}
                value={[formData.target_schema_index || 0]}
                onValueChange={(value) => handleInputChange("target_schema_index", value[0])}
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

            <div className="flex items-center space-x-2">
              <Switch
                id="debug_mode"
                checked={formData.debug_mode || false}
                onCheckedChange={(checked) => handleInputChange("debug_mode", checked)}
              />
              <Label htmlFor="debug_mode">Debug Mode</Label>
            </div>
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Saving..." : isPartialUpdate ? "Update Configuration" : "Save Configuration"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
