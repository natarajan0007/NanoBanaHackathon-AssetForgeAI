'use client'

import { useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MoreHorizontal } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { PlatformForm } from "./platform-form"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface PlatformsTableProps {
  data: any[];
  onDataChange: () => void;
}

export function PlatformsTable({ data, onDataChange }: PlatformsTableProps) {
  const { toast } = useToast();
  const [isCreateDialogOpen, setCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [selectedPlatform, setSelectedPlatform] = useState<any | null>(null)

  const handleEdit = (platform: any) => {
    setSelectedPlatform(platform)
    setEditDialogOpen(true)
  }

  const handleDelete = (platform: any) => {
    setSelectedPlatform(platform)
    setDeleteDialogOpen(true)
  }

  const handleSave = async (formData: any) => {
    const apiCall = selectedPlatform
      ? apiClient.updatePlatform(selectedPlatform.id, formData)
      : apiClient.createPlatform(formData)

    const response = await apiCall;

    if (response.success) {
      toast({ title: `Platform ${selectedPlatform ? 'updated' : 'created'} successfully` })
      onDataChange(); // Refresh the data in the parent component
      setEditDialogOpen(false)
      setCreateDialogOpen(false)
      setSelectedPlatform(null)
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" })
    }
  }

  const confirmDelete = async () => {
    if (!selectedPlatform) return;

    const response = await apiClient.deletePlatform(selectedPlatform.id);
    if (response.success) {
      toast({ title: "Platform deleted successfully" })
      onDataChange();
      setDeleteDialogOpen(false)
      setSelectedPlatform(null)
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" })
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => { setSelectedPlatform(null); setCreateDialogOpen(true); }}>Create Platform</Button>
      </div>
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((platform) => (
              <TableRow key={platform.id}>
                <TableCell className="font-medium">{platform.name}</TableCell>
                <TableCell>
                  <Badge variant={platform.is_active ? "default" : "outline"}>
                    {platform.is_active ? "Active" : "Inactive"}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => handleEdit(platform)}>Edit</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleDelete(platform)} className="text-destructive">Delete</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={isCreateDialogOpen || isEditDialogOpen} onOpenChange={(isOpen) => {
        if (!isOpen) {
          setCreateDialogOpen(false);
          setEditDialogOpen(false);
          setSelectedPlatform(null);
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedPlatform ? "Edit Platform" : "Create New Platform"}</DialogTitle>
          </DialogHeader>
          <PlatformForm 
            initialData={selectedPlatform} 
            onSave={handleSave} 
            onCancel={() => {
              setCreateDialogOpen(false);
              setEditDialogOpen(false);
              setSelectedPlatform(null);
            }} 
          />
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the platform
              <strong>{selectedPlatform?.name}</strong>.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete}>Continue</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
