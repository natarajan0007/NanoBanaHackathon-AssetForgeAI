import { ConfiguredSettings } from "@/components/dashboard/configured-settings";
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { ProjectsGrid } from "@/components/dashboard/projects-grid"
import { QuickActions } from "@/components/dashboard/quick-actions"
import { RecentActivity } from "@/components/dashboard/recent-activity"

export default function DashboardPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <DashboardHeader />

      <main className="flex-1 p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main content area */}
          <div className="lg:col-span-2 space-y-8">
            <QuickActions />
            <ProjectsGrid />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <ConfiguredSettings />
            <RecentActivity />
          </div>
        </div>
      </main>
    </div>
  )
}
