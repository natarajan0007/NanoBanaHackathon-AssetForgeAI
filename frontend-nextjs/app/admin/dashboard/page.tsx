import { AdminHeader } from "@/components/admin/admin-header"
import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { AdminStats } from "@/components/admin/admin-stats"
import { RecentUsers } from "@/components/admin/recent-users"
import { SystemHealth } from "@/components/admin/system-health"

export default function AdminDashboardPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AdminHeader />

      <div className="flex flex-1">
        <AdminSidebar />

        <main className="flex-1 p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Admin Dashboard</h1>
              <p className="text-muted-foreground">Manage users, platforms, and system configuration</p>
            </div>

            <AdminStats />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RecentUsers />
              <SystemHealth />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
