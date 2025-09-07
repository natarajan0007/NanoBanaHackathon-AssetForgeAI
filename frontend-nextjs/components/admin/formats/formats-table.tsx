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
import { FormatForm } from "./format-form"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface FormatsTableProps {
  data: any[];
  onDataChange: () => void; // Callback to refresh data
}

export function FormatsTable({ data, onDataChange }: FormatsTableProps) {
  const { toast } = useToast();
  const [isCreateDialogOpen, setCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<any | null>(null)

  const handleEdit = (format: any) => {
    setSelectedFormat(format)
    setEditDialogOpen(true)
  }

  const handleDelete = (format: any) => {
    setSelectedFormat(format)
    setDeleteDialogOpen(true)
  }

  const handleSave = async (formData: any) => {
    const apiCall = selectedFormat
      ? apiClient.updateAdminFormat(selectedFormat.id, formData)
      : apiClient.createAdminFormat(formData)

    const response = await apiCall;

    if (response.success) {
      toast({ title: `Format ${selectedFormat ? 'updated' : 'created'} successfully` })
      onDataChange(); // Refresh the data in the parent component
      setEditDialogOpen(false)
      setCreateDialogOpen(false)
      setSelectedFormat(null)
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" })
    }
  }

  const confirmDelete = async () => {
    if (!selectedFormat) return;

    const response = await apiClient.deleteAdminFormat(selectedFormat.id);
    if (response.success) {
      toast({ title: "Format deleted successfully" })
      onDataChange();
      setDeleteDialogOpen(false)
      setSelectedFormat(null)
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" })
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => { setSelectedFormat(null); setCreateDialogOpen(true); }}>Create Format</Button>
      </div>
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Dimensions</TableHead>
              <TableHead>Platform</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((format) => (
              <TableRow key={format.id}>
                <TableCell className="font-medium">{format.name}</TableCell>
                <TableCell>{format.type}</TableCell>
                <TableCell>{`${format.width} x ${format.height}`}</TableCell>
                <TableCell>{format.platformId || "N/A"}</TableCell>
                <TableCell>
                  <Badge variant={format.is_active ? "default" : "outline"}>
                    {format.is_active ? "Active" : "Inactive"}
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
                      <DropdownMenuItem onClick={() => handleEdit(format)}>Edit</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleDelete(format)} className="text-destructive">Delete</DropdownMenuItem>
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
          setSelectedFormat(null);
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedFormat ? "Edit Format" : "Create New Format"}</DialogTitle>
          </DialogHeader>
          <FormatForm 
            initialData={selectedFormat} 
            onSave={handleSave} 
            onCancel={() => {
              setCreateDialogOpen(false);
              setEditDialogOpen(false);
              setSelectedFormat(null);
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
              This action cannot be undone. This will permanently delete the format
              <strong>{selectedFormat?.name}</strong>.
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
