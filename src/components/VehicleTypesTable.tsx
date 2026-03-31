import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { MoreHorizontal } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { EditVehicleTypeDialog } from "./EditVehicleTypeDialog";

const vehicleTypesData = [
  { name: "Refrigerated Truck", capacity: 30 },
  { name: "Flatbed Truck", capacity: 40 },
  { name: "Box Truck", capacity: 25 },
];

interface VehicleType {
  name: string;
  capacity: number;
}

export function VehicleTypesTable() {
  const [vehicleTypes, setVehicleTypes] = useState<VehicleType[]>(vehicleTypesData);
  const [editingVehicleType, setEditingVehicleType] = useState<VehicleType | null>(null);

  const handleEdit = (vehicleType: VehicleType) => {
    setEditingVehicleType(vehicleType);
  };

  const handleDelete = (vehicleTypeName: string) => {
    setVehicleTypes(vehicleTypes.filter(vt => vt.name !== vehicleTypeName));
  };

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Capacity (m³)</TableHead>
            <TableHead>
              <span className="sr-only">Actions</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {vehicleTypes.map((type) => (
            <TableRow key={type.name}>
              <TableCell className="font-medium">{type.name}</TableCell>
              <TableCell>{type.capacity}</TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button aria-haspopup="true" size="icon" variant="ghost">
                      <MoreHorizontal className="h-4 w-4" />
                      <span className="sr-only">Toggle menu</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Actions</DropdownMenuLabel>
                    <DropdownMenuItem onSelect={() => handleEdit(type)}>Edit</DropdownMenuItem>
                    <DropdownMenuItem onSelect={() => handleDelete(type.name)}>Delete</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <EditVehicleTypeDialog
        open={!!editingVehicleType}
        onOpenChange={(open) => !open && setEditingVehicleType(null)}
        vehicleType={editingVehicleType}
      />
    </>
  );
}
