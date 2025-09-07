'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { LogOut, Settings, User, Shield } from 'lucide-react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface UserData {
  username: string
  email: string
  role: string
}

const getDisplayName = (user: UserData) => {
  if (!user?.username) return ""
  const email = user.username
  const namePart = email.split('@')[0]
  // Capitalize the first letter
  return namePart.charAt(0).toUpperCase() + namePart.slice(1)
}

const getDisplayInitial = (user: UserData) => {
  const displayName = getDisplayName(user)
  return displayName[0].toUpperCase()
}

export function DashboardHeader() {
  const [user, setUser] = useState<UserData | null>(null)
  const router = useRouter()

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    router.push('/login')
  }

  if (!user) return null

  return (
    <header className='border-b border-border bg-card'>
      <div className='px-6 py-4'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center space-x-4'>
            <Link href="/dashboard" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <Shield className='h-6 w-6 text-accent' />
              <h1 className='text-xl font-bold text-foreground'>AssetForge AI</h1>
            </Link>
            <div className='hidden md:block'>
              <p className='text-sm text-muted-foreground'>Welcome back, {getDisplayName(user)}!</p>
            </div>
          </div>

          <div className='flex items-center space-x-4'>
            

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant='ghost' className='relative h-10 w-10 rounded-full'>
                  <Avatar className='h-10 w-10'>
                    <AvatarFallback className='bg-accent text-accent-foreground'>
                      {getDisplayInitial(user)}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className='w-56' align='end'>
                <div className='flex items-center justify-start gap-2 p-2'>
                  <div className='flex flex-col space-y-1 leading-none'>
                    <p className='font-medium'>
                      {getDisplayName(user)}
                    </p>
                    <p className='text-xs text-muted-foreground'>{user.email}</p>
                  </div>
                </div>
                <DropdownMenuSeparator />
                
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className='mr-2 h-4 w-4' />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  )
}