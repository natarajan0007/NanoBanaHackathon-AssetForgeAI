'use client'

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
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
import { Textarea } from "@/components/ui/textarea"

const formSchema = z.object({
  name: z.string().min(2, { message: "Name must be at least 2 characters." }),
  styles: z.string().refine((val) => {
    try {
      JSON.parse(val);
      return true;
    } catch (e) {
      return false;
    }
  }, { message: "Invalid JSON format." }),
})

interface TextStyleFormProps {
  initialData?: any;
  onSave: (data: any) => void;
  onCancel: () => void;
}

export function TextStyleForm({ initialData, onSave, onCancel }: TextStyleFormProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: initialData?.name || '',
      styles: initialData?.styles ? JSON.stringify(initialData.styles, null, 2) : `{
  "title": {
    "fontFamily": "Inter, sans-serif",
    "fontSize": 48,
    "fontWeight": "bold",
    "color": "#FFFFFF"
  },
  "subtitle": {
    "fontFamily": "Inter, sans-serif",
    "fontSize": 24,
    "fontWeight": "normal",
    "color": "#E0E0E0"
  }
}`,
    },
  })

  const handleSubmit = (formData: z.infer<typeof formSchema>) => {
    try {
      const parsedStyles = JSON.parse(formData.styles);
      onSave({ name: formData.name, styles: parsedStyles });
    } catch (e) {
      form.setError("styles", { type: "manual", message: "Invalid JSON format." });
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Style Set Name</FormLabel>
              <FormControl>
                <Input placeholder="e.g., Modern Dark" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="styles"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Styles (JSON)</FormLabel>
              <FormControl>
                <Textarea placeholder='Enter JSON for styles' {...field} rows={15} />
              </FormControl>
              <FormDescription>
                Define different text styles like 'title', 'subtitle', etc.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="flex justify-end space-x-2">
          <Button type="button" variant="ghost" onClick={onCancel}>Cancel</Button>
          <Button type="submit">Save</Button>
        </div>
      </form>
    </Form>
  )
}
