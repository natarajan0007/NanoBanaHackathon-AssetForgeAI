import { AdminHeader } from "@/components/admin/admin-header"
import { AdminSidebar } from "@/components/admin/admin-sidebar"
import { AdaptationRulesForm } from "@/components/admin/rules/adaptation-rules-form"
import { AiBehaviorRulesForm } from "@/components/admin/rules/ai-behavior-rules-form"
import { UploadModerationRulesForm } from "@/components/admin/rules/upload-moderation-rules-form"
import { ManualEditingRulesForm } from "@/components/admin/rules/manual-editing-rules-form"

export default function AdminRulesPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AdminHeader />

      <div className="flex flex-1">
        <AdminSidebar />

        <main className="flex-1 p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-foreground">Application Rules</h1>
              <p className="text-muted-foreground">Configure the core behavior of the application and AI</p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-6">
                <AdaptationRulesForm />
                <UploadModerationRulesForm />
              </div>
              <div className="space-y-6">
                <AiBehaviorRulesForm />
                <ManualEditingRulesForm />
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  )
}
