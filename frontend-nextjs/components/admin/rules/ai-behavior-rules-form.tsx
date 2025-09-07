'use client'

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useEffect } from "react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { Skeleton } from "@/components/ui/skeleton"

const formSchema = z.object({
  adaptationStrategy: z.enum(["crop", "extend"]),
  imageQuality: z.enum(["high", "medium", "low"]),
})

export function AiBehaviorRulesForm() {
  const { toast } = useToast();
  const { data, loading, error, execute: fetchRules } = useApi<z.infer<typeof formSchema>>();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  useEffect(() => {
    fetchRules(() => apiClient.getAiBehaviorRules());
  }, [fetchRules]);

  useEffect(() => {
    if (data) {
      form.reset(data);
    }
  }, [data, form]);

  const onSave = async (formData: z.infer<typeof formSchema>) => {
    const response = await apiClient.updateAiBehaviorRules(formData);
    if (response.success) {
      toast({ title: "AI behavior rules updated successfully" });
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" });
    }
  }

  if (loading) {
    return <Skeleton className="h-48 w-full" />
  }

  if (error) {
    return <p className="text-destructive">Error fetching AI behavior rules: {error}</p>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Behavior</CardTitle>
        <CardDescription>Control the overall AI strategy and output quality.</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSave)} className="space-y-6">
            <FormField
              control={form.control}
              name="adaptationStrategy"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Adaptation Strategy</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a strategy" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="crop">Smart Crop</SelectItem>
                      <SelectItem value="extend">Extend Background</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="imageQuality"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Image Quality</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a quality" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="flex justify-end">
              <Button type="submit">Save Changes</Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
