import { AdminHeader } from "@/components/admin/admin-header"
import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { UserGrowthChart } from "@/components/admin/analytics/user-growth-chart"
import { ProjectStatusChart } from "@/components/admin/analytics/project-status-chart"
import { GenerationByFormatChart } from "@/components/admin/analytics/generation-by-format-chart"

export default function AdminAnalyticsPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AdminHeader />

      <div className="flex flex-1">
        <AdminSidebar />

        <main className="flex-1 p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Analytics</h1>
              <p className="text-muted-foreground">Insights into your application's usage and performance.</p>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <UserGrowthChart />
              <ProjectStatusChart />
              <div className="lg:col-span-2">
                <GenerationByFormatChart />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
