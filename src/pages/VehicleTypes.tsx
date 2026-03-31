import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { columns } from "@/components/vehicle-types-columns";
import { DataTable } from "@/components/vehicles-data-table";
import { Button } from "@/components/ui/button";
import { PlusCircle } from "lucide-react";
import { AddVehicleTypeDialog } from "@/components/AddVehicleTypeDialog";

const VehicleTypes = () => {
  const { data: vehicleTypes, isLoading, isError } = useQuery({
    queryKey: ["vehicle_types"],
    queryFn: async () => {
      const response = await apiClient.getVehicleTypes();
      return response.items;
    },
  });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return <div>Error loading vehicle types.</div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Vehicle Types</h1>
        <AddVehicleTypeDialog />
      </div>
      <DataTable columns={columns} data={vehicleTypes || []} />
    </div>
  );
};

export default VehicleTypes;
