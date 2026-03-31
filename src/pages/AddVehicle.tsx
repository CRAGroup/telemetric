import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from "@/components/ui/form";
import ehicleSchema = z.object({
    make: z.string().min(1, "Make is required"),
    model_name: z.string().min(1, "Model is required"),
    body_type: z.string().min(1, "Body type is required"),
    registration_number: z.string().min(1, "Registration number is required"),
    chassis_number: z.string().min(1, "Chassis number is required"),
    engine_number: z.string().min(1, "Engine number is required"),
    engine_capacity: z.coerce.number().min(1, "Engine capacity is required"),
    max_load_weight: z.coerce.number().min(1, "Maximum load weight is required"),
    acquisition_odometer: z.coerce.number().min(0, "Odometer reading must be a positive number"),
    department: z.string().optional(),
    driver_id: z.string().optional(),
    logbook_details: z.string().optional(),
    spare_keys_location: z.string().optional(),
    usage_type: z.string().min(1, "Usage type is required"),
    vehicle_status: z.enum(["active", "idle", "under maintenance", "decommissioned"]).default("idle"),
    insurance_provider: z.string().optional(),
    insurance_policy_number: z.string().optional(),
    insurance_expiry: z.string().optional(),
    permit_details: z.string().optional(),
    fuel_type: z.string().min(1, "Fuel type is required"),
    tracking_device_id: z.string().optional(),
});

const AddVehicle = () => {
    const { toast } = useToast();
    
    // Fetch drivers for dropdown
    const { data: driversData } = useQuery({
        queryKey: ['drivers'],
        queryFn: async () => await apiClient.getDrivers(),
    });
    
    const drivers = driversData?.items || [];
    
    const form = useForm<z.infer<typeof vehicleSchema>>({
        resolver: zodResolver(vehicleSchema),
        defaultValues: {
            make: "",
            model_name: "",
            body_type: "",
            registration_number: "",
            chassis_number: "",
            engine_number: "",
            engine_capacity: 0,
            max_load_weight: 0,
            acquisition_odometer: 0,
            department: "",
            driver_id: "none",
            logbook_details: "",
            spare_keys_location: "",
            usage_type: "",
            vehicle_status: "idle",
            insurance_provider: "",
            insurance_policy_number: "",
            insurance_expiry: "",
            permit_details: "",
            fuel_type: "",
            tracking_device_id: "",
        },
    });

    const { isSubmitting } = form.formState;

    const onSubmit = async (values: z.infer<typeof vehicleSchema>) => {
        try {
            // Convert driver_id to number if provided (skip if "none")
            const payload = {
                ...values,
                driver_id: values.driver_id && values.driver_id !== "none" ? Number(values.driver_id) : null,
            };
            
            const data = await apiClient.createVehicle(payload);
            
            toast({
                title: "Vehicle added successfully",
                description: `Vehicle ${data.make} ${data.model_name} has been added.`,
            });
            form.reset();
        } catch (error: any) {
            toast({
                title: "Error adding vehicle",
                description: error.message || "Failed to add vehicle",
                variant: "destructive",
            });
        }
    };

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Add Vehicle</h1>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <FormField
                        control={form.control}
                        name="make"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Make</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., Toyota" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="model_name"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Model</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., Hilux" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="body_type"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Body Type</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., Pickup" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="registration_number"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Registration Number</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., KDA 123A" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="chassis_number"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Chassis Number</FormLabel>
                                <FormControl>
                                    <Input placeholder="Enter chassis number" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="engine_number"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Engine Number</FormLabel>
                                <FormControl>
                                    <Input placeholder="Enter engine number" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="engine_capacity"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Engine Capacity (cc)</FormLabel>
                                <FormControl>
                                    <Input type="number" placeholder="e.g., 2800" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="max_load_weight"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Maximum Load Weight (kg)</FormLabel>
                                <FormControl>
                                    <Input type="number" placeholder="e.g., 5000" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="acquisition_odometer"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Odometer at Acquisition</FormLabel>
                                <FormControl>
                                    <Input type="number" placeholder="e.g., 5000" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="department"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Department</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., Sales" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="driver_id"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Assign Driver (Optional)</FormLabel>
                                <Select onValueChange={field.onChange} value={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select a driver" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="none">No Driver</SelectItem>
                                        {drivers.map((driver: any) => (
                                            <SelectItem key={driver.id} value={String(driver.id)}>
                                                {driver.first_name} {driver.last_name} - {driver.license_number}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="logbook_details"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Logbook Details</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., Stored in safe" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="spare_keys_location"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Spare Keys Location</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., With fleet manager" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="usage_type"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Usage Type</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., Delivery truck" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="vehicle_status"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Vehicle Status</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select a status" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="active">Active</SelectItem>
                                        <SelectItem value="idle">Idle</SelectItem>
                                        <SelectItem value="under maintenance">Under Maintenance</SelectItem>
                                        <SelectItem value="decommissioned">Decommissioned</SelectItem>
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="insurance_provider"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Insurance Provider</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., Jubilee Insurance" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="insurance_policy_number"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Insurance Policy Number</FormLabel>
                                <FormControl>
                                    <Input placeholder="Enter policy number" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="insurance_expiry"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Insurance Expiry Date</FormLabel>
                                <FormControl>
                                    <Input type="date" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="permit_details"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Permit Details</FormLabel>
                                <FormControl>
                                    <Input placeholder="Enter permit details" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="fuel_type"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Fuel Type</FormLabel>
                                <FormControl>
                                    <Input placeholder="e.g., Diesel" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="tracking_device_id"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Tracking Device ID</FormLabel>
                                <FormControl>
                                    <Input placeholder="Enter tracking device ID" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <Button type="submit" className="md:col-span-2 lg:col-span-3" disabled={isSubmitting}>
                        {isSubmitting ? "Adding Vehicle..." : "Add Vehicle"}
                    </Button>
                </form>
            </Form>
        </div>
    );
};

export default AddVehicle;
