import { AdminHeader } from "@/components/admin/admin-header"
import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { TextStyleManagement } from "@/components/admin/text-styles/text-style-management"

export default function AdminTextStylesPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AdminHeader />

      <div className="flex flex-1">
        <AdminSidebar />

        <main className="flex-1 p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Text Style Management</h1>
              <p className="text-muted-foreground">Create and manage sets of reusable text styles for overlays.</p>
            </div>
            <TextStyleManagement />
          </div>
        </main>
      </div>
    </div>
  )
}
