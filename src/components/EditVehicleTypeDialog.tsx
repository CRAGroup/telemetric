import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { apiClient } from "@/lib/api-client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "./ui/textarea";
import { VehicleType } from "./vehicle-types-columns";

const vehicleTypeSchema = z.object({
    name: z.string().min(1, "Name is required"),
    description: z.string().optional(),
    status: z.enum(["active", "inactive"]).default("active"),
});

export const EditVehicleTypeDialog = ({ vehicleType }: { vehicleType: VehicleType }) => {
    const { toast } = useToast();
    const queryClient = useQueryClient();

    const form = useForm<z.infer<typeof vehicleTypeSchema>>({
        resolver: zodResolver(vehicleTypeSchema),
        defaultValues: {
            name: vehicleType.name,
            description: vehicleType.description,
            status: vehicleType.status,
        },
    });

    const { isSubmitting } = form.formState;

    const mutation = useMutation({
        mutationFn: async (values: z.infer<typeof vehicleTypeSchema>) => {
            await apiClient.updateVehicleType(Number(vehicleType.id), values);
        },
        onSuccess: () => {
            toast({
                title: "Vehicle type updated successfully",
            });
            queryClient.invalidateQueries({ queryKey: ["vehicle_types"] });
        },
        onError: (error: any) => {
            toast({
                title: "Error updating vehicle type",
                description: error.message,
                variant: "destructive",
            });
        },
    });

    const onSubmit = (values: z.infer<typeof vehicleTypeSchema>) => {
        mutation.mutate(values);
    };

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="ghost">Edit</Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Edit Vehicle Type</DialogTitle>
                    <DialogDescription>
                        Update the details of the vehicle type.
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Name</FormLabel>
                                    <FormControl>
                                        <Input placeholder="e.g., Sedan" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="description"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Description</FormLabel>
                                    <FormControl>
                                        <Textarea placeholder="e.g., A 4-door passenger car" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="status"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Status</FormLabel>
                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select a status" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="active">Active</SelectItem>
                                            <SelectItem value="inactive">Inactive</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <Button type="submit" disabled={isSubmitting}>
                            {isSubmitting ? "Updating..." : "Update Vehicle Type"}
                        </Button>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
};
