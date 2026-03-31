'use client';

import { ColumnDef } from '@tanstack/react-table';
import { MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { useToast } from '@/components/ui/use-toast';
import Swal from 'sweetalert2';

export type Vehicle = any; // API vehicle type

const ActionsCell = ({ row }: { row: any }) => {
  const vehicle = row.original;
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const mutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.deleteVehicle(Number(id));
    },
    onSuccess: () => {
      toast({ title: 'Vehicle deleted successfully' });
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
    },
    onError: (error: any) => {
      toast({ title: 'Error deleting vehicle', description: error.message, variant: 'destructive' });
    },
  });

  const handleDelete = () => {
    Swal.fire({
      title: 'Are you sure?',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete it!',
    }).then((result) => {
      if (result.isConfirmed) {
        mutation.mutate(vehicle.id);
      }
    });
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="h-8 w-8 p-0">
          <span className="sr-only">Open menu</span>
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Actions</DropdownMenuLabel>
        <DropdownMenuItem asChild>
          <Link to={`/vehicles/edit/${vehicle.id}`}>Edit</Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleDelete} className="text-red-500">
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export const columns: ColumnDef<Vehicle>[] = [
  {
    accessorKey: 'make',
    header: 'Make',
  },
  {
    accessorKey: 'model_name',
    header: 'Model',
  },
  {
    accessorKey: 'registration_number',
    header: 'Registration',
  },
  {
    accessorKey: 'driver_name',
    header: 'Driver',
  },
  {
    accessorKey: 'current_odometer',
    header: 'Odometer',
  },
  {
    accessorKey: 'department',
    header: 'Department',
  },
  {
    accessorKey: 'fuel_type',
    header: 'Fuel Type',
  },
  {
    accessorKey: 'vehicle_status',
    header: 'Status',
    cell: ({ row }) => {
      const status = row.getValue('vehicle_status') as string;
      return (
        <Badge
          className={cn({
            'bg-green-500': status === 'active',
            'bg-yellow-500': status === 'idle',
            'bg-orange-500': status === 'under maintenance',
            'bg-red-500': status === 'decommissioned',
          })}
        >
          {status}
        </Badge>
      );
    },
  },
  {
    id: 'actions',
    cell: ActionsCell,
  },
];
