"use client"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Users, Settings, Palette, FileImage, BarChart3, Shield, Home, Layers } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"

const sidebarItems = [
  {
    title: "Dashboard",
    href: "/admin/dashboard",
    icon: Home,
  },
  {
    title: "User Management",
    href: "/admin/users",
    icon: Users,
  },
  {
    title: "Platform Management",
    href: "/admin/platforms",
    icon: Layers,
  },
  
  {
    title: "Format Management",
    href: "/admin/formats",
    icon: FileImage,
  },
  {
    title: "Text Styles",
    href: "/admin/text-styles",
    icon: Palette,
  },
  {
    title: "Application Rules",
    href: "/admin/rules",
    icon: Settings,
  },
  {
    title: "Analytics",
    href: "/admin/analytics",
    icon: BarChart3,
  },
  {
    title: "System Health",
    href: "/admin/system",
    icon: Shield,
  },
]

export function AdminSidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-sidebar border-r border-sidebar-border">
      <div className="p-4">
        <nav className="space-y-2">
          {sidebarItems.map((item) => (
            <Link key={item.href} href={item.href}>
              <Button
                variant={pathname === item.href ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start",
                  pathname === item.href && "bg-sidebar-accent text-sidebar-accent-foreground",
                )}
              >
                <item.icon className="mr-2 h-4 w-4" />
                {item.title}
              </Button>
            </Link>
          ))}
        </nav>
      </div>
    </div>
  )
}
