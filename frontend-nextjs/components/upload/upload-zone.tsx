'use client'

import type React from "react"
import { useState, useCallback } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Upload, FileImage, AlertCircle, CheckCircle, X } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface UploadZoneProps {
  onFileUpload: (projectName: string, files: File[]) => void;
}

export function UploadZone({ onFileUpload }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const { toast } = useToast();

  const handleFileValidation = (file: File): boolean => {
    const maxSize = 50 * 1024 * 1024; // 50MB
    const allowedTypes = ["image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"];

    if (!allowedTypes.includes(file.type)) {
      toast({
        title: "Invalid file type",
        description: `Skipping file ${file.name}: Invalid file type.`,
        variant: "destructive",
      });
      return false;
    }

    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: `Skipping file ${file.name}: File size exceeds 50MB.`,
        variant: "destructive",
      });
      return false;
    }

    return true;
  };

  const handleFilesSelect = (files: FileList) => {
    const newFiles = Array.from(files).filter(handleFileValidation);
    setSelectedFiles(prev => [...prev, ...newFiles]);
    if (!projectName && newFiles.length > 0) {
      setProjectName(newFiles[0].name.split('.').slice(0, -1).join('.'));
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    if (e.dataTransfer.files) handleFilesSelect(e.dataTransfer.files);
  }, [projectName]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) handleFilesSelect(e.target.files);
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  }

  const handleContinue = () => {
    if (!projectName) {
        toast({ title: "Project name required", description: "Please enter a name for your project.", variant: "destructive" });
        return;
    }
    if (selectedFiles.length === 0) {
        toast({ title: "No files selected", description: "Please choose at least one file to upload.", variant: "destructive" });
        return;
    }
    onFileUpload(projectName, selectedFiles);
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-foreground mb-2">Create Your Project</h2>
        <p className="text-muted-foreground">Start by giving your project a name and uploading your master assets.</p>
      </div>

      <Card>
        <CardContent className="p-6 space-y-4">
            <div>
                <Label htmlFor="project-name">Project Name</Label>
                <Input 
                    id="project-name"
                    placeholder="e.g., Summer Marketing Campaign"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                />
            </div>
            <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                isDragOver ? "border-accent bg-accent/5" : "border-muted-foreground/25"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <input type="file" id="file-upload" className="hidden" accept="image/*" onChange={handleInputChange} multiple />
                <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center justify-center space-y-4">
                    <div className="rounded-full bg-accent/10 p-4">
                        <Upload className="h-8 w-8 text-accent" />
                    </div>
                    <div className="text-center">
                        <h3 className="text-lg font-medium text-foreground">Drag & drop or click to upload</h3>
                        <p className="text-muted-foreground text-sm">Max file size 50MB. Supported formats: JPG, PNG, GIF.</p>
                    </div>
                </label>
            </div>
            {selectedFiles.length > 0 && (
                <div className="space-y-2">
                    <h4 className="font-medium">Selected Files:</h4>
                    <div className="grid gap-2">
                        {selectedFiles.map((file, index) => (
                            <div key={index} className="flex items-center justify-between p-2 bg-muted rounded-lg">
                                <div className="flex items-center space-x-2 overflow-hidden">
                                    <FileImage className="h-5 w-5 text-muted-foreground flex-shrink-0"/>
                                    <span className="text-sm font-medium truncate">{file.name}</span>
                                </div>
                                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => handleRemoveFile(index)}>
                                    <X className="h-4 w-4" />
                                </Button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleContinue} disabled={selectedFiles.length === 0 || !projectName} size="lg">
            Continue to Preview
        </Button>
      </div>
    </div>
  )
}