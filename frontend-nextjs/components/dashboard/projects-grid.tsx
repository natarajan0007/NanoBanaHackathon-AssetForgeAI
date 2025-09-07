'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { MoreHorizontal, Eye, Download, Trash2 } from 'lucide-react'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { apiClient } from '@/lib/api-client'
import { useApi } from '@/lib/hooks/use-api'
import { Skeleton } from '@/components/ui/skeleton'

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

// This interface matches the ProjectResponse schema from the backend
interface Project {
  id: string
  name: string
  status: string
  submitDate: string
  fileCounts: { [key: string]: number }
  assets: {
    id: string
    filename: string
    previewUrl: string
  }[]
}

export function ProjectsGrid() {
  const { data, loading, error, execute: fetchProjects } = useApi<{projects: Project[]}>();
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  useEffect(() => {
    fetchProjects(() => apiClient.getProjects(10, 0, statusFilter));
  }, [fetchProjects, statusFilter]);

  const handleProjectClick = (projectId: string) => {
    router.push(`/projects/${projectId}`);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
      case 'processing':
      case 'generating':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
      case 'ready_for_review':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
    }
  }

  const renderProjectCards = () => {
    if (loading) {
        return Array.from({ length: 4 }).map((_, i) => (
            <Card key={`skeleton-${i}`} className="overflow-hidden">
                <div className="aspect-video bg-muted"><Skeleton className="w-full h-full"/></div>
                <CardHeader className="pb-2"><Skeleton className="h-5 w-3/4"/></CardHeader>
                <CardContent className="pt-0"><Skeleton className="h-5 w-1/2"/></CardContent>
            </Card>
        ));
    }

    if (error) {
        return <p className="text-destructive col-span-full">Error fetching projects: {error}</p>;
    }

    if (!data?.projects || data.projects.length === 0) {
        return <p className="col-span-full">You haven't created any projects yet.</p>;
    }

    return data.projects.map((project) => {
        const totalFiles = Object.values(project.fileCounts).reduce((sum, count) => sum + count, 0);
        return (
            <Card key={project.id} className='overflow-hidden cursor-pointer hover:ring-2 hover:ring-accent transition-all' onClick={() => handleProjectClick(project.id)}>
              <div className='aspect-video bg-muted'>
                <img
                  src={project.assets.length > 0 ? `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${project.assets[0].previewUrl}` : '/placeholder.svg'}
                  alt={project.name}
                  className='w-full h-full object-cover'
                />
              </div>
              <CardHeader className='pb-2'>
                <div className='flex items-start justify-between'>
                  <div className='space-y-1'>
                    <CardTitle className='text-base'>{project.name}</CardTitle>
                    <CardDescription className='text-sm'>
                      Created {new Date(project.submitDate).toLocaleDateString()}
                    </CardDescription>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant='ghost' size='sm'>
                        <MoreHorizontal className='h-4 w-4' />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align='end'>
                      <DropdownMenuItem onClick={() => handleProjectClick(project.id)}>
                        <Eye className='mr-2 h-4 w-4' />
                        View Details
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Download className='mr-2 h-4 w-4' />
                        Download All
                      </DropdownMenuItem>
                      <DropdownMenuItem className='text-destructive'>
                        <Trash2 className='mr-2 h-4 w-4' />
                        Delete Project
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              <CardContent className='pt-0'>
                <div className='flex items-center justify-between'>
                  <Badge className={getStatusColor(project.status)}>
                    {project.status.replace('_', ' ').toUpperCase()}
                  </Badge>
                  <span className='text-sm text-muted-foreground'>{totalFiles} files</span>
                </div>
              </CardContent>
            </Card>
        )
    });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Projects</CardTitle>
        <CardDescription>Manage and track your asset transformation projects</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="all" onValueChange={(value) => setStatusFilter(value === 'all' ? null : value)}>
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="ready_for_review">Ready for Review</TabsTrigger>
            <TabsTrigger value="failed">Failed</TabsTrigger>
          </TabsList>
        </Tabs>
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-4'>
          {renderProjectCards()}
        </div>
      </CardContent>
    </Card>
  )
}

