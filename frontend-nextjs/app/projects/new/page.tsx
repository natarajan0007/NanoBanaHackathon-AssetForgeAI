'use client'

import { useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardHeader } from '@/components/dashboard/dashboard-header';
import { UploadZone } from '@/components/upload/upload-zone';
import { apiClient } from '@/lib/api-client';
import { useToast } from "@/hooks/use-toast";
import { Loader2 } from "lucide-react";

// This is the new entry point for creating a project.
// Its only job is to capture the project name and file, send them to the backend,
// and then redirect the user to the new project's dedicated page.

export default function NewProjectPage() {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { toast } = useToast();

  const handleUpload = async (projectName: string, files: File[]) => {
    setIsLoading(true);
    const response = await apiClient.uploadProject(projectName, files);

    if (response.success && response.data?.projectId) {
      toast({ title: "Project Created!", description: "Redirecting to your new project workspace..." });
      // Redirect to the new dynamic project page
      router.push(`/projects/${response.data.projectId}`);
    } else {
      toast({ title: "Upload Failed", description: response.error, variant: "destructive" });
      setIsLoading(false);
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      <DashboardHeader />
      <main className='container mx-auto px-4 py-8'>
        <div className='max-w-4xl mx-auto'>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center text-center h-96">
                <Loader2 className="h-12 w-12 animate-spin text-accent mb-4"/>
                <h2 className="text-xl font-semibold">Creating Project...</h2>
                <p className="text-muted-foreground">Please wait while we set up your workspace.</p>
            </div>
          ) : (
            <UploadZone onFileUpload={handleUpload} />
          )}
        </div>
      </main>
    </div>
  );
}
