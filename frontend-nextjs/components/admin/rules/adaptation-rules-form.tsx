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
  focalPointLogic: z.enum(["face-centric", "product-centric", "center"]),
  // layoutGuidance is a JSON object, we'll handle it as a string for now
  // In a real app, this would be a more complex JSON editor
  layoutGuidance: z.string().optional(),
})

export function AdaptationRulesForm() {
  const { toast } = useToast();
  const { data, loading, error, execute: fetchRules } = useApi<z.infer<typeof formSchema>>();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  useEffect(() => {
    fetchRules(() => apiClient.getAdaptationRules());
  }, [fetchRules]);

  useEffect(() => {
    if (data) {
      form.reset({
        ...data,
        layoutGuidance: data.layoutGuidance ? JSON.stringify(data.layoutGuidance, null, 2) : ''
      });
    }
  }, [data, form]);

  const onSave = async (formData: z.infer<typeof formSchema>) => {
    const dataToSave = {
      ...formData,
      layoutGuidance: formData.layoutGuidance ? JSON.parse(formData.layoutGuidance) : null,
    }
    const response = await apiClient.updateAdaptationRules(dataToSave);
    if (response.success) {
      toast({ title: "Adaptation rules updated successfully" });
    } else {
      toast({ title: "Error", description: response.error, variant: "destructive" });
    }
  }

  if (loading) {
    return <Skeleton className="h-48 w-full" />
  }

  if (error) {
    return <p className="text-destructive">Error fetching adaptation rules: {error}</p>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Image Adaptation</CardTitle>
        <CardDescription>Configure how the AI adapts images to different formats.</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSave)} className="space-y-6">
            <FormField
              control={form.control}
              name="focalPointLogic"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Focal Point Logic</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a logic" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="face-centric">Face Centric</SelectItem>
                      <SelectItem value="product-centric">Product Centric</SelectItem>
                      <SelectItem value="center">Center</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            {/* We are omitting layoutGuidance for now as it requires a more complex UI */}
            <div className="flex justify-end">
              <Button type="submit">Save Changes</Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
