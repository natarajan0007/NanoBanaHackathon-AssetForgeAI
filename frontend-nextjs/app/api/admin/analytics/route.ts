import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const period = searchParams.get("period") || "30d"

    // Mock analytics data
    const analytics = {
      overview: {
        totalUsers: 2847,
        activeUsers: 1923,
        assetsProcessed: 18392,
        aiGenerations: 156284,
        storageUsed: "2.4 TB",
        apiCalls: 892341,
      },
      growth: {
        usersGrowth: 12.5,
        assetsGrowth: 23.1,
        generationsGrowth: 18.7,
        revenueGrowth: 15.3,
      },
      usage: {
        topPlatforms: [
          { name: "Instagram", usage: 45.2, count: 69847 },
          { name: "Facebook", usage: 28.7, count: 44521 },
          { name: "Twitter", usage: 16.8, count: 26089 },
          { name: "LinkedIn", usage: 9.3, count: 14427 },
        ],
        topFormats: [
          { name: "Instagram Post", usage: 32.1, count: 49823 },
          { name: "Instagram Story", usage: 18.9, count: 29341 },
          { name: "Facebook Post", usage: 15.7, count: 24389 },
          { name: "Twitter Post", usage: 12.4, count: 19256 },
        ],
      },
      performance: {
        averageProcessingTime: "2.3s",
        successRate: 98.7,
        errorRate: 1.3,
        uptime: 99.9,
      },
      timeline: generateTimelineData(period),
    }

    return NextResponse.json({
      success: true,
      analytics,
      period,
    })
  } catch (error) {
    console.error("Analytics fetch error:", error)
    return NextResponse.json({ error: "Failed to fetch analytics" }, { status: 500 })
  }
}

function generateTimelineData(period: string) {
  const days = period === "7d" ? 7 : period === "30d" ? 30 : 90
  const data = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)

    data.push({
      date: date.toISOString().split("T")[0],
      users: Math.floor(Math.random() * 100) + 50,
      assets: Math.floor(Math.random() * 500) + 200,
      generations: Math.floor(Math.random() * 2000) + 1000,
      apiCalls: Math.floor(Math.random() * 10000) + 5000,
    })
  }

  return data
}
