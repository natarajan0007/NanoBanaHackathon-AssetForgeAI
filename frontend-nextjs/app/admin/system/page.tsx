import { AdminHeader } from "@/components/admin/admin-header"
import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { SystemHealthCard } from "@/components/admin/system/system-health-card"

export default function AdminSystemPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AdminHeader />

      <div className="flex flex-1">
        <AdminSidebar />

        <main className="flex-1 p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-foreground">System Health</h1>
              <p className="text-muted-foreground">Check the status of your application's core services.</p>
            </div>
            <SystemHealthCard />
          </div>
        </main>
      </div>
    </div>
  )
}
