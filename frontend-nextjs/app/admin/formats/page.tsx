import { AdminHeader } from "@/components/admin/admin-header"
import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { FormatManagement } from "@/components/admin/formats/format-management"

export default function AdminFormatsPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AdminHeader />

      <div className="flex flex-1">
        <AdminSidebar />

        <main className="flex-1 p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Format Management</h1>
              <p className="text-muted-foreground">Define the output formats for asset generation</p>
            </div>
            <FormatManagement />
          </div>
        </main>
      </div>
    </div>
  )
}
