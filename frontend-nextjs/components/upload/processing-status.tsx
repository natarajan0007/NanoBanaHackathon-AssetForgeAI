"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Loader2, Brain, Palette, FileImage, Zap } from "lucide-react"

interface ProcessingStatusProps {
  step: "analyzing" | "generating"
}

export function ProcessingStatus({ step }: ProcessingStatusProps) {
  const [progress, setProgress] = useState(0)
  const [currentTask, setCurrentTask] = useState("")

  useEffect(() => {
    const tasks =
      step === "analyzing"
        ? [
            { name: "Analyzing image composition...", duration: 1000 },
            { name: "Extracting color palette...", duration: 800 },
            { name: "Detecting text elements...", duration: 700 },
            { name: "Identifying brand elements...", duration: 500 },
          ]
        : [
            { name: "Generating Instagram formats...", duration: 1200 },
            { name: "Creating Facebook variants...", duration: 1000 },
            { name: "Optimizing for Twitter...", duration: 800 },
            { name: "Finalizing LinkedIn versions...", duration: 1000 },
          ]

    let currentProgress = 0
    let taskIndex = 0

    const runTasks = () => {
      if (taskIndex < tasks.length) {
        setCurrentTask(tasks[taskIndex].name)

        const increment = 100 / tasks.length
        const targetProgress = (taskIndex + 1) * increment

        const progressInterval = setInterval(() => {
          currentProgress += 2
          setProgress(Math.min(currentProgress, targetProgress))

          if (currentProgress >= targetProgress) {
            clearInterval(progressInterval)
            taskIndex++
            setTimeout(runTasks, 200)
          }
        }, tasks[taskIndex].duration / 50)
      }
    }

    runTasks()
  }, [step])

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-foreground mb-2">
          {step === "analyzing" ? "Analyzing Your Asset" : "Generating Formats"}
        </h2>
        <p className="text-muted-foreground">
          {step === "analyzing"
            ? "Our AI is analyzing your asset to understand its composition and optimize transformations"
            : "Creating optimized versions of your asset for different platforms"}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Loader2 className="h-5 w-5 animate-spin text-accent" />
            <span>Processing Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          <div className="space-y-1">
            <p className="text-sm font-medium text-foreground">{currentTask}</p>
            <p className="text-xs text-muted-foreground">This may take a few moments...</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center space-y-2">
              <div className="rounded-full bg-blue-100 dark:bg-blue-900 p-3 w-12 h-12 mx-auto flex items-center justify-center">
                <Brain className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="text-xs text-muted-foreground">AI Analysis</div>
            </div>
            <div className="text-center space-y-2">
              <div className="rounded-full bg-purple-100 dark:bg-purple-900 p-3 w-12 h-12 mx-auto flex items-center justify-center">
                <Palette className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="text-xs text-muted-foreground">Color Extraction</div>
            </div>
            <div className="text-center space-y-2">
              <div className="rounded-full bg-green-100 dark:bg-green-900 p-3 w-12 h-12 mx-auto flex items-center justify-center">
                <FileImage className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="text-xs text-muted-foreground">Format Generation</div>
            </div>
            <div className="text-center space-y-2">
              <div className="rounded-full bg-orange-100 dark:bg-orange-900 p-3 w-12 h-12 mx-auto flex items-center justify-center">
                <Zap className="h-6 w-6 text-orange-600 dark:text-orange-400" />
              </div>
              <div className="text-xs text-muted-foreground">Optimization</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
