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
} from "@/components/ui/form"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { useEffect } from "react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import { Skeleton } from "@/components/ui/skeleton"

const formSchema = z.object({
  editingEnabled: z.boolean(),
  croppingEnabled: z.boolean(),
  saturationEnabled: z.boolean(),
  addTextOrLogoEnabled: z.boolean(),
  allowedLogoSources: z.string(), // JSON string
})

export function ManualEditingRulesForm() {
  const { toast } = useToast();
  const { data, loading, error, execute: fetchRules } = useApi<z.infer<typeof formSchema>>();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  useEffect(() => {
    fetchRules(() => apiClient.getManualEditingRules());
  }, [fetchRules]);

  useEffect(() => {
    if (data) {
      form.reset({
        ...data,
        allowedLogoSources: data.allowedLogoSources ? JSON.stringify(data.allowedLogoSources, null, 2) : ''
      });
    }
  }, [data, form]);

  const onSave = async (formData: z.infer<typeof formSchema>) => {
    try {
      const dataToSave = {
        ...formData,
        allowedLogoSources: formData.allowedLogoSources ? JSON.parse(formData.allowedLogoSources) : {},
      }
      const response = await apiClient.updateManualEditingRules(dataToSave);
      if (response.success) {
        toast({ title: "Manual editing rules updated successfully" });
      } else {
        toast({ title: "Error", description: response.error, variant: "destructive" });
      }
    } catch (e) {
      toast({ title: "Invalid JSON", description: "Please check the format of the Allowed Logo Sources JSON.", variant: "destructive" });
    }
  }

  if (loading) {
    return <Skeleton className="h-64 w-full" />
  }

  if (error) {
    return <p className="text-destructive">Error fetching manual editing rules: {error}</p>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Manual Editing</CardTitle>
        <CardDescription>Configure the manual editing capabilities available to users.</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSave)} className="space-y-6">
            <FormField
              control={form.control}
              name="editingEnabled"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                  <div className="space-y-0.5">
                    <FormLabel>Enable Editing</FormLabel>
                  </div>
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="croppingEnabled"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                  <div className="space-y-0.5">
                    <FormLabel>Enable Cropping</FormLabel>
                  </div>
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="saturationEnabled"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                  <div className="space-y-0.5">
                    <FormLabel>Enable Saturation</FormLabel>
                  </div>
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="addTextOrLogoEnabled"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                  <div className="space-y-0.5">
                    <FormLabel>Enable Text/Logo</FormLabel>
                  </div>
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="allowedLogoSources"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Allowed Logo Sources (JSON)</FormLabel>
                  <FormControl>
                    <Textarea placeholder='{
  "types": ["jpeg", "png"],
  "maxSizeMb": 5
}' {...field} rows={5} />
                  </FormControl>
                  <FormDescription>Define the rules for user-uploaded logos.</FormDescription>
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
