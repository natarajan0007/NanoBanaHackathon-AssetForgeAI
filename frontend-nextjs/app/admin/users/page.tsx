import { AdminHeader } from "@/components/admin/admin-header"
import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { UserManagementTable } from "@/components/admin/user-management-table"

export default function AdminUsersPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AdminHeader />

      <div className="flex flex-1">
        <AdminSidebar />

        <main className="flex-1 p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-foreground">User Management</h1>
              <p className="text-muted-foreground">Manage user accounts and permissions</p>
            </div>

            <UserManagementTable />
          </div>
        </main>
      </div>
    </div>
  )
}
