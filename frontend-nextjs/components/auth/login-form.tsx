'use client'

import type React from 'react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useRouter } from 'next/navigation'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

export function LoginForm() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // 1. Call the login endpoint
      const loginResponse = await apiClient.login({ username, password })

      if (!loginResponse.success || !loginResponse.data?.accessToken) {
        throw new Error(loginResponse.error || "Invalid credentials")
      }

      // 2. Store the token
      const { accessToken } = loginResponse.data
      localStorage.setItem("token", accessToken)

      // 3. Fetch user data with the new token
      const userResponse = await apiClient.getMe()

      if (!userResponse.success || !userResponse.data) {
        throw new Error(userResponse.error || "Failed to fetch user data")
      }

      // 4. Store user data and redirect
      const user = userResponse.data
      localStorage.setItem("user", JSON.stringify(user))

      toast({
        title: "Welcome back!",
        description: "You have been successfully signed in.",
      })

      if (user.role === "admin") {
        router.push("/admin/dashboard")
      } else {
        router.push("/dashboard")
      }

    } catch (error) {
      // Display the actual error message from the API
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred."
      toast({
        title: "Login Failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className='space-y-4'>
      <div className='space-y-2'>
        <Label htmlFor='username'>Username</Label>
        <Input
          id='username'
          placeholder='Enter your username'
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>

      <div className='space-y-2'>
        <Label htmlFor='password'>Password</Label>
        <Input
          id='password'
          type='password'
          placeholder='Enter your password'
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>

      <Button type='submit' className='w-full' disabled={isLoading}>
        {isLoading ? 'Signing in...' : 'Sign In'}
      </Button>
    </form>
  )
}
