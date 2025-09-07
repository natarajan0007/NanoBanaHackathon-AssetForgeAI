'use client'

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Search, MoreHorizontal, UserPlus, Edit, Trash2, Shield } from "lucide-react"
import { apiClient } from "@/lib/api-client"
import { useApi } from "@/lib/hooks/use-api"
import { Skeleton } from "@/components/ui/skeleton"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { UserForm } from "./user-form"
import { useToast } from "@/hooks/use-toast"

// This interface matches the User schema from the backend API
interface User {
  id: string
  username: string
  email: string
  role: "user" | "admin"
  is_active: boolean
  created_at: string
  organization: {
    id: string
    name: string
  }
}

export function UserManagementTable() {
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState("")
  const { data: users, loading, error, execute: fetchUsers, setData: setUsers } = useApi<User[]>()
  const [isCreateDialogOpen, setCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setEditDialogOpen] = useState(false)
  const [isDeactivateDialogOpen, setDeactivateDialogOpen] = useState(false)
  const [isActivateDialogOpen, setActivateDialogOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  useEffect(() => {
    fetchUsers(() => apiClient.getUsers());
  }, [fetchUsers]);

  const filteredUsers = users?.filter(
    (user) =>
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const handleEdit = (user: User) => {
    setSelectedUser(user)
    setEditDialogOpen(true)
  }

  const handleDeactivate = (user: User) => {
    setSelectedUser(user)
    setDeactivateDialogOpen(true)
  }

  const handleActivate = (user: User) => {
    setSelectedUser(user)
    setActivateDialogOpen(true)
  }

  const handleSave = async (formData: any) => {
    const apiCall = selectedUser
      ? apiClient.updateUser(selectedUser.id, formData)
      : apiClient.createUser(formData)

    const response = await apiCall;

    if (response.success) {
      toast({ title: `User ${selectedUser ? 'updated' : 'created'} successfully` })
      fetchUsers(() => apiClient.getUsers()); // Refresh data
      setEditDialogOpen(false)
      setCreateDialogOpen(false)
      setSelectedUser(null)
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" })
    }
  }

  const confirmDeactivation = async () => {
    if (!selectedUser) return;

    const response = await apiClient.deactivateUser(selectedUser.id);
    if (response.success) {
      toast({ title: "User deactivated successfully" })
      // Fix: Make sure users is defined before mapping
      if (users) {
        setUsers(users.map(u => u.id === selectedUser.id ? { ...u, is_active: false } : u));
      }
      setDeactivateDialogOpen(false)
      setSelectedUser(null)
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" })
    }
  }

  const confirmActivation = async () => {
    if (!selectedUser) return;

    const response = await apiClient.activateUser(selectedUser.id);
    if (response.success) {
      toast({ title: "User activated successfully" })
      // Fix: Make sure users is defined before mapping
      if (users) {
        setUsers(users.map(u => u.id === selectedUser.id ? { ...u, is_active: true } : u));
      }
      setActivateDialogOpen(false)
      setSelectedUser(null)
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" })
    }
  }

  const renderTableBody = () => {
    if (loading) {
      return Array.from({ length: 5 }).map((_, i) => (
        <TableRow key={`skeleton-${i}`}>
          <TableCell><Skeleton className="h-8 w-32" /></TableCell>
          <TableCell><Skeleton className="h-8 w-24" /></TableCell>
          <TableCell><Skeleton className="h-8 w-24" /></TableCell>
          <TableCell><Skeleton className="h-8 w-12" /></TableCell>
        </TableRow>
      ));
    }

    if (error) {
      return <TableRow><TableCell colSpan={6} className="text-center text-destructive">Error: {error}</TableCell></TableRow>
    }

    if (!filteredUsers || filteredUsers.length === 0) {
      return <TableRow><TableCell colSpan={6} className="text-center">No users found.</TableCell></TableRow>
    }

    return filteredUsers.map((user) => (
      <TableRow key={user.id}>
        <TableCell>
          <div>
            <div className="font-medium">{user.username}</div>
            <div className="text-sm text-muted-foreground">{user.email}</div>
          </div>
        </TableCell>
        <TableCell>
          <Badge variant={user.is_active ? "default" : "destructive"}>
            {user.is_active ? "Active" : "Inactive"}
          </Badge>
        </TableCell>
        <TableCell>
          <div className="flex items-center space-x-1">
            {user.role === "admin" && <Shield className="h-3 w-3 text-accent" />}
            <Badge variant={user.role === "admin" ? "default" : "secondary"}>{user.role}</Badge>
          </div>
        </TableCell>
        <TableCell className="text-sm text-muted-foreground">
          {new Date(user.created_at).toLocaleDateString()}
        </TableCell>
        <TableCell className="text-sm text-muted-foreground">
          {user.organization.name}
        </TableCell>
        <TableCell>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleEdit(user)}>
                <Edit className="mr-2 h-4 w-4" />
                Edit User
              </DropdownMenuItem>
              {user.is_active ? (
                <DropdownMenuItem onClick={() => handleDeactivate(user)} className="text-destructive">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Deactivate User
                </DropdownMenuItem>
              ) : (
                <DropdownMenuItem onClick={() => handleActivate(user)}>
                  <Shield className="mr-2 h-4 w-4" />
                  Activate User
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </TableCell>
      </TableRow>
    ));
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Users ({users?.length || 0})</CardTitle>
          <Button onClick={() => { setSelectedUser(null); setCreateDialogOpen(true); }}>
            <UserPlus className="h-4 w-4 mr-2" />
            Add User
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center space-x-2 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by username or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8"
            />
          </div>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Date Joined</TableHead>
                <TableHead>Organization</TableHead>
                <TableHead className="w-[70px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {renderTableBody()}
            </TableBody>
          </Table>
        </div>
      </CardContent>

      {/* Create/Edit Dialog */}
      <Dialog open={isCreateDialogOpen || isEditDialogOpen} onOpenChange={(isOpen) => {
        if (!isOpen) {
          setCreateDialogOpen(false);
          setEditDialogOpen(false);
          setSelectedUser(null);
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedUser ? "Edit User" : "Create New User"}</DialogTitle>
          </DialogHeader>
          <UserForm
            initialData={selectedUser}
            onSave={handleSave}
            onCancel={() => {
              setCreateDialogOpen(false);
              setEditDialogOpen(false);
              setSelectedUser(null);
            }}
          />
        </DialogContent>
      </Dialog>

      {/* Deactivate Confirmation Dialog */}
      <AlertDialog open={isDeactivateDialogOpen} onOpenChange={setDeactivateDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure you want to deactivate this user?</AlertDialogTitle>
            <AlertDialogDescription>
              This will prevent the user <strong>{selectedUser?.username}</strong> from logging in. Their data will be preserved.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeactivation}>Deactivate</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Activate Confirmation Dialog */}
      <AlertDialog open={isActivateDialogOpen} onOpenChange={setActivateDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure you want to activate this user?</AlertDialogTitle>
            <AlertDialogDescription>
              The user <strong>{selectedUser?.username}</strong> will be able to log in again.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmActivation}>Activate</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  )
}