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
import { TextStyleForm } from "./text-style-form"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface TextStylesTableProps {
  data: any[];
  onDataChange: () => void;
}

export function TextStylesTable({ data, onDataChange }: TextStylesTableProps) {
  const { toast } = useToast();
  const [isCreateDialogOpen, setCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [selectedStyle, setSelectedStyle] = useState<any | null>(null)

  const handleEdit = (style: any) => {
    setSelectedStyle(style)
    setEditDialogOpen(true)
  }

  const handleDelete = (style: any) => {
    setSelectedStyle(style)
    setDeleteDialogOpen(true)
  }

  const handleSave = async (formData: any) => {
    const apiCall = selectedStyle
      ? apiClient.updateTextStyleSet(selectedStyle.id, formData)
      : apiClient.createTextStyleSet(formData)

    const response = await apiCall;

    if (response.success) {
      toast({ title: `Text Style Set ${selectedStyle ? 'updated' : 'created'} successfully` })
      onDataChange();
      setEditDialogOpen(false)
      setCreateDialogOpen(false)
      setSelectedStyle(null)
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" })
    }
  }

  const confirmDelete = async () => {
    if (!selectedStyle) return;

    const response = await apiClient.deleteTextStyleSet(selectedStyle.id);
    if (response.success) {
      toast({ title: "Text Style Set deleted successfully" })
      onDataChange();
      setDeleteDialogOpen(false)
      setSelectedStyle(null)
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" })
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => { setSelectedStyle(null); setCreateDialogOpen(true); }}>Create Style Set</Button>
      </div>
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Styles Preview</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((style) => (
              <TableRow key={style.id}>
                <TableCell className="font-medium">{style.name}</TableCell>
                <TableCell>
                  <pre className="text-xs bg-muted p-2 rounded-md">{JSON.stringify(style.styles, null, 2)}</pre>
                </TableCell>
                <TableCell>
                  <Badge variant={style.is_active ? "default" : "outline"}>
                    {style.is_active ? "Active" : "Inactive"}
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
                      <DropdownMenuItem onClick={() => handleEdit(style)}>Edit</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleDelete(style)} className="text-destructive">Delete</DropdownMenuItem>
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
          setSelectedStyle(null);
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedStyle ? "Edit Text Style Set" : "Create New Text Style Set"}</DialogTitle>
          </DialogHeader>
          <TextStyleForm 
            initialData={selectedStyle} 
            onSave={handleSave} 
            onCancel={() => {
              setCreateDialogOpen(false);
              setEditDialogOpen(false);
              setSelectedStyle(null);
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
              This action cannot be undone. This will permanently delete the style set
              <strong>{selectedStyle?.name}</strong>.
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
