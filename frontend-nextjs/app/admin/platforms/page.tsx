import { AdminHeader } from "@/components/admin/admin-header"
import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { PlatformManagement } from "@/components/admin/platforms/platform-management"

export default function AdminPlatformsPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AdminHeader />

      <div className="flex flex-1">
        <AdminSidebar />

        <main className="flex-1 p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Platform Management</h1>
              <p className="text-muted-foreground">Manage the platforms available for asset repurposing.</p>
            </div>
            <PlatformManagement />
          </div>
        </main>
      </div>
    </div>
  )
}