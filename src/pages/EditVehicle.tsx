import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { apiClient } from "@/lib/api-client";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

// NOTE: This schema matches the database schema exactly
const vehicleSchema = z.object({
    make: z.string().min(1, "Make is required"),
    model_name: z.string().min(1, "Model is required"),
    body_type: z.string().min(1, "Body type is required"),
    registration_number: z.string().min(1, "Registration number is required"),
    chassis_number: z.string().min(1, "Chassis number is required"),
    engine_number: z.string().min(1, "Engine number is required"),
    engine_capacity: z.coerce.number().min(1, "Engine capacity is required"),
    max_load_weight: z.coerce.number().min(1, "Maximum load weight is required"),
    acquisition_odometer: z.coerce.number().min(0, "Odometer reading must be a positive number"),
    current_odometer: z.coerce.number().min(0, "Current odometer reading must be a positive number").optional(),
    department: z.string().optional(),
    driver_id: z.string().optional(),
    logbook_details: z.string().optional(),
    spare_keys_location: z.string().optional(),
    usage_type: z.string().min(1, "Usage type is required"),
    vehicle_status: z.string().optional(),
    insurance_provider: z.string().optional(),
    insurance_policy_number: z.string().optional(),
    insurance_expiry: z.string().optional(),
    permit_details: z.string().optional(),
    fuel_type: z.string().min(1, "Fuel type is required"),
    tracking_device_id: z.string().optional(),
});

const EditVehicle = () => {
    const { id } = useParams<{ id: string }>();
    const { toast } = useToast();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const { data: vehicle, isLoading } = useQuery({
        queryKey: ["vehicle", id],
        queryFn: async () => {
            if (!id) throw new Error('Vehicle ID is required');
            return await apiClient.getVehicle(Number(id));
        },
    });
    
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
            current_odometer: 0,
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

    const mutation = useMutation({
        mutationFn: async (values: z.infer<typeof vehicleSchema>) => {
            if (!id) throw new Error('Vehicle ID is required');
            // Convert driver_id to number if provided (skip if "none")
            const payload = {
                ...values,
                driver_id: values.driver_id && values.driver_id !== "none" ? Number(values.driver_id) : null,
            };
            await apiClient.updateVehicle(Number(id), payload);
        },
        onSuccess: () => {
            toast({
                title: "Vehicle updated successfully",
            });
            queryClient.invalidateQueries({ queryKey: ["vehicles"] });
            navigate("/vehicles");
        },
        onError: (error: any) => {
            toast({
                title: "Error updating vehicle",
                description: error.message || "Failed to update vehicle",
                variant: "destructive",
            });
        },
    });

    const onSubmit = (values: z.infer<typeof vehicleSchema>) => {
        mutation.mutate(values);
    };

    // Populate the form with the vehicle data once it's loaded
    useEffect(() => {
        if (vehicle) {
            form.reset({
                make: vehicle.make || "",
                model_name: vehicle.model_name || vehicle.model || "",
                body_type: vehicle.body_type || "",
                registration_number: vehicle.registration_number || "",
                chassis_number: vehicle.chassis_number || vehicle.vin_number || "",
                engine_number: vehicle.engine_number || "",
                engine_capacity: vehicle.engine_capacity || 0,
                max_load_weight: vehicle.max_load_weight || 0,
                acquisition_odometer: vehicle.acquisition_odometer || vehicle.current_odometer || 0,
                current_odometer: vehicle.current_odometer || 0,
                department: vehicle.department || "",
                driver_id: vehicle.driver_id ? String(vehicle.driver_id) : "none",
                logbook_details: vehicle.logbook_details || "",
                spare_keys_location: vehicle.spare_keys_location || "",
                usage_type: vehicle.usage_type || "",
                vehicle_status: vehicle.vehicle_status || vehicle.status || "idle",
                insurance_provider: vehicle.insurance_provider || "",
                insurance_policy_number: vehicle.insurance_policy_number || "",
                insurance_expiry: vehicle.insurance_expiry || "",
                permit_details: vehicle.permit_details || "",
                fuel_type: vehicle.fuel_type || "",
                tracking_device_id: vehicle.tracking_device_id || vehicle.device_imei || "",
            });
        }
    }, [vehicle, form]);

    if (isLoading) {
        return <div>Loading vehicle data...</div>;
    }

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Edit Vehicle</h1>
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
                                    <Input type="number" placeholder="e.g., 3000" {...field} />
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
                        name="current_odometer"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Current Odometer Reading</FormLabel>
                                <FormControl>
                                    <Input type="number" placeholder="e.g., 15000" {...field} />
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
                        {isSubmitting ? "Updating Vehicle..." : "Update Vehicle"}
                    </Button>
                </form>
            </Form>
        </div>
    );
};

export default EditVehicle;
