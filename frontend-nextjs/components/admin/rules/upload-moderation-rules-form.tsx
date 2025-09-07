'use client'

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { useEffect } from "react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { Skeleton } from "@/components/ui/skeleton"

const formSchema = z.object({
  allowedImageTypes: z.string().min(1, { message: "Please enter at least one type." }),
  maxFileSizeMb: z.coerce.number().int().positive(),
  nsfwAlertsActive: z.boolean(),
})

export function UploadModerationRulesForm() {
  const { toast } = useToast();
  const { data, loading, error, execute: fetchRules } = useApi<z.infer<typeof formSchema>>();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  useEffect(() => {
    fetchRules(() => apiClient.getUploadModerationRules());
  }, [fetchRules]);

  useEffect(() => {
    if (data) {
      form.reset({
        ...data,
        allowedImageTypes: data.allowedImageTypes.join(', '),
      });
    }
  }, [data, form]);

  const onSave = async (formData: z.infer<typeof formSchema>) => {
    const dataToSave = {
      ...formData,
      allowedImageTypes: formData.allowedImageTypes.split(',').map(s => s.trim()),
    }
    const response = await apiClient.updateUploadModerationRules(dataToSave);
    if (response.success) {
      toast({ title: "Upload moderation rules updated successfully" });
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" });
    }
  }

  if (loading) {
    return <Skeleton className="h-48 w-full" />
  }

  if (error) {
    return <p className="text-destructive">Error fetching upload moderation rules: {error}</p>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Content & Uploads</CardTitle>
        <CardDescription>Set rules for content moderation and file uploads.</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSave)} className="space-y-6">
            <FormField
              control={form.control}
              name="allowedImageTypes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Allowed Image Types</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g., jpeg, png, psd" {...field} />
                  </FormControl>
                  <FormDescription>Comma-separated list of allowed file extensions.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="maxFileSizeMb"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Max File Size (MB)</FormLabel>
                  <FormControl>
                    <Input type="number" placeholder="50" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="nsfwAlertsActive"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>NSFW Alerts</FormLabel>
                    <FormDescription>
                      Enable automatic alerts for potentially NSFW content.
                    </FormDescription>
                  </div>
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
