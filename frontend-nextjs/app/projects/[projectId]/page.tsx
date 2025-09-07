'use client'

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import { DashboardHeader } from '@/components/dashboard/dashboard-header';
import { ProcessingStatus } from '@/components/upload/processing-status';
import { FormatSelection } from '@/components/upload/format-selection';
import { GeneratedAssets } from '@/components/upload/generated-assets';
import { apiClient } from '@/lib/api-client';
import { useToast } from "@/hooks/use-toast";
import { Skeleton } from "@/components/ui/skeleton";

// This page is the main workspace for a single project.
// It fetches the project's status and displays the appropriate UI.

export default function ProjectPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const { toast } = useToast();

  // State to hold the current project data and its workflow status
  const [project, setProject] = useState<any>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [generatedAssets, setGeneratedAssets] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingRules, setEditingRules] = useState<any>(null);

  // --- DATA FETCHING AND POLLING LOGIC ---

  const fetchProjectAndResults = useCallback(async () => {
    if (!projectId) return;

    const projectStatusResponse = await apiClient.getProjectStatus(projectId);

    if (!projectStatusResponse.success || !projectStatusResponse.data) {
      setError("Could not load project details.");
      toast({ title: "Error", description: `Failed to get project status: ${projectStatusResponse.error}`, variant: "destructive" });
      setIsLoading(false);
      return;
    }

    const status = projectStatusResponse.data.status;
    setProject({ id: projectId, status });

    if (status === 'completed') {
        // If the project is already completed, we would need a way to get the last job ID.
        // For now, we will only show results if we polled for them in this session.
        console.log("Project already completed on load.");
    } else if (status === 'ready_for_review') {
        const previewResponse = await apiClient.getProjectPreview(projectId);
        if (previewResponse.success) {
            setProject((prev: any) => ({...prev, assets: previewResponse.data}));
        } else {
            setError("Failed to load asset previews.");
        }
    }
    setIsLoading(false);
  }, [projectId, toast]);

  // Initial data fetch
  useEffect(() => {
    fetchProjectAndResults();
    apiClient.getEditingRules().then(response => {
      if (response.success) {
        setEditingRules(response.data);
      }
    });
  }, [fetchProjectAndResults]);

  // Polling logic for processing and generation
  useEffect(() => {
    let interval: NodeJS.Timeout | undefined;

    const poll = async () => {
        if (project?.status === 'processing') {
            const res = await apiClient.getProjectStatus(projectId);
            if (res.success && res.data.status !== project.status) {
                if(res.data.status === 'ready_for_review') {
                    await fetchProjectAndResults(); // fetch preview data and update status
                } else {
                    setProject((p:any) => ({...p, status: res.data.status}));
                }
            }
        } else if (project?.status === 'generating' && jobId) {
            const res = await apiClient.getGenerationStatus(jobId);
            if (res.success && res.data.status === 'completed') {
                const resultsResponse = await apiClient.getGenerationResults(jobId);
                if (resultsResponse.success) {
                    setGeneratedAssets(resultsResponse.data);
                    setProject((p:any) => ({...p, status: 'completed'})); // Final state
                } else {
                    toast({ title: "Error", description: "Could not fetch generation results.", variant: "destructive" });
                    setProject((p:any) => ({...p, status: 'ready_for_review'}));
                }
            }
        }
    };

    if (project?.status === 'processing' || project?.status === 'generating') {
      interval = setInterval(poll, 3000);
    }

    return () => clearInterval(interval);
  }, [project, projectId, jobId, fetchProjectAndResults, toast]);


  // --- HANDLERS ---

  const handleStartGeneration = async (formats: string[], prompt?: string) => {
    if (!projectId) return;
    setProject((p:any) => ({...p, status: 'generating'}));
    const response = await apiClient.startGeneration(projectId, formats, prompt);
    if (response.success && response.data?.jobId) {
      setJobId(response.data.jobId);
      toast({ title: "Generation Started", description: "Your new assets are being created." });
    } else {
      toast({ title: "Generation Failed", description: response.error, variant: "destructive" });
      setProject((p:any) => ({...p, status: 'ready_for_review'})); // Revert status on failure
    }
  };

  const resetWorkflow = () => {
    // Navigate back to the main dashboard to start over
    window.location.href = '/dashboard';
  }

  // --- UI RENDERING ---

  const renderContent = () => {
    if (isLoading) {
      return <div className="space-y-4"><Skeleton className="h-12 w-full" /><Skeleton className="h-64 w-full" /></div>;
    }

    if (error) {
      return <div className="text-center text-destructive">{error}</div>;
    }

    if (!project) {
      return <div className="text-center">Project not found.</div>;
    }

    switch (project.status) {
      case 'processing':
      case 'uploading':
        return <ProcessingStatus step="analyzing" />;
      case 'ready_for_review':
        return <FormatSelection assets={project.assets || []} onFormatSelection={handleStartGeneration} onBack={resetWorkflow} editingRules={editingRules} />;
      case 'generating':
        return <ProcessingStatus step="generating" />;
      case 'completed':
        return <GeneratedAssets assets={generatedAssets} onStartNew={resetWorkflow} />;
      case 'failed':
        return <div className="text-center text-destructive">Project processing failed.</div>;
      default:
        return <div className="text-center">Unknown project status: {project.status}</div>;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <DashboardHeader />
      <main className="flex-1 p-6">
        <div className="container mx-auto">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}
