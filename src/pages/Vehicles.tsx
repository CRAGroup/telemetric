import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator, DropdownMenuCheckboxItem } from "@/components/ui/dropdown-menu";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useToast } from "@/components/ui/use-toast";
import Swal from "sweetalert2";
import {
  Plus,
  Search,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Settings2,
  MoreHorizontal,
  Pencil,
  Trash2,
  SlidersHorizontal,
  Truck,
} from "lucide-react";

const PAGE_SIZE = 50;

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  idle: "bg-yellow-100 text-yellow-800",
  "under maintenance": "bg-orange-100 text-orange-800",
  maintenance: "bg-orange-100 text-orange-800",
  decommissioned: "bg-red-100 text-red-800",
  inactive: "bg-gray-100 text-gray-800",
};

const Vehicles = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [tab, setTab] = useState<"all" | "assigned" | "unassigned" | "archived">("all");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState<string[]>([]);

  const { data: vehiclesResponse, isLoading } = useQuery({
    queryKey: ["vehicles", page],
    queryFn: () => apiClient.getVehicles({ page, page_size: PAGE_SIZE }),
    staleTime: 5 * 60 * 1000,
  });

  const { data: vehicleTypesResponse } = useQuery({
    queryKey: ["vehicle_types"],
    queryFn: () => apiClient.getVehicleTypes({ page_size: 100 }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.deleteVehicle(id),
    onSuccess: () => {
      toast({ title: "Vehicle deleted successfully" });
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
    },
    onError: (e: any) =>
      toast({ title: "Error deleting vehicle", description: e.message, variant: "destructive" }),
  });

  const handleDelete = (vehicle: any) => {
    Swal.fire({
      title: "Delete Vehicle?",
      text: `Remove ${vehicle.registration_number} from the fleet?`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#ef4444",
      cancelButtonColor: "#6b7280",
      confirmButtonText: "Yes, delete",
    }).then((r) => { if (r.isConfirmed) deleteMutation.mutate(vehicle.id); });
  };

  const allVehicles: any[] = vehiclesResponse?.items || [];
  const total = vehiclesResponse?.total || 0;
  const vehicleTypes: any[] = vehicleTypesResponse?.items || [];

  // Client-side filtering on top of server data
  const filtered = useMemo(() => {
    let list = allVehicles;

    // Tab filter
    if (tab === "assigned") list = list.filter((v) => v.driver_id);
    else if (tab === "unassigned") list = list.filter((v) => !v.driver_id);
    else if (tab === "archived") list = list.filter((v) => v.vehicle_status === "decommissioned" || v.status === "inactive");

    // Search
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (v) =>
          v.registration_number?.toLowerCase().includes(q) ||
          v.make?.toLowerCase().includes(q) ||
          v.model_name?.toLowerCase().includes(q) ||
          v.model?.toLowerCase().includes(q) ||
          v.driver_name?.toLowerCase().includes(q) ||
          v.department?.toLowerCase().includes(q)
      );
    }

    // Status filter
    if (statusFilter.length > 0) {
      list = list.filter((v) =>
        statusFilter.includes(v.vehicle_status || v.status)
      );
    }

    // Type filter
    if (typeFilter.length > 0) {
      list = list.filter((v) =>
        typeFilter.includes(String(v.vehicle_type_id))
      );
    }

    return list;
  }, [allVehicles, tab, search, statusFilter, typeFilter]);

  const tabCounts = useMemo(() => ({
    all: allVehicles.length,
    assigned: allVehicles.filter((v) => v.driver_id).length,
    unassigned: allVehicles.filter((v) => !v.driver_id).length,
    archived: allVehicles.filter((v) => v.vehicle_status === "decommissioned" || v.status === "inactive").length,
  }), [allVehicles]);

  const TABS = [
    { key: "all", label: "All" },
    { key: "assigned", label: "Assigned" },
    { key: "unassigned", label: "Unassigned" },
    { key: "archived", label: "Archived" },
  ] as const;

  const STATUSES = ["active", "idle", "under maintenance", "decommissioned"];

  const toggleStatus = (s: string) =>
    setStatusFilter((prev) => prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]);

  const toggleType = (id: string) =>
    setTypeFilter((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);

  const clearFilters = () => { setStatusFilter([]); setTypeFilter([]); setSearch(""); };
  const hasFilters = statusFilter.length > 0 || typeFilter.length > 0 || search.trim();

  // Pagination display
  const start = (page - 1) * PAGE_SIZE + 1;
  const end = Math.min(page * PAGE_SIZE, total);
  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <div className="flex items-center justify-between px-6 py-4 border-b">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">Vehicles</h1>
          {hasFilters && (
            <Button variant="ghost" size="sm" className="text-xs text-muted-foreground h-6 px-2" onClick={clearFilters}>
              Clear filters
            </Button>
          )}
        </div>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="h-8 w-8 p-0">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => navigate("/vehicle-types")}>Manage Vehicle Types</DropdownMenuItem>
              <DropdownMenuItem onClick={() => queryClient.invalidateQueries({ queryKey: ["vehicles"] })}>Refresh</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button asChild size="sm" className="h-8 gap-1">
            <Link to="/vehicles/add">
              <Plus className="h-4 w-4" />
              Add Vehicle
            </Link>
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-0 px-6 border-b">
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => { setTab(key); setPage(1); }}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              tab === key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {label}
            {tabCounts[key] > 0 && (
              <span className={`ml-1.5 text-xs px-1.5 py-0.5 rounded-full ${
                tab === key ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
              }`}>
                {tabCounts[key]}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Filter bar */}
      <div className="flex items-center justify-between px-6 py-3 gap-3 border-b bg-muted/20">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              placeholder="Search"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="pl-8 h-8 w-44 text-sm"
            />
          </div>

          {/* Vehicle Type filter */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className={`h-8 text-sm gap-1 ${typeFilter.length > 0 ? "border-primary text-primary" : ""}`}>
                Vehicle Type
                {typeFilter.length > 0 && <span className="bg-primary text-primary-foreground rounded-full text-xs px-1.5">{typeFilter.length}</span>}
                <ChevronDown className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-48">
              {vehicleTypes.length === 0 ? (
                <DropdownMenuItem disabled>No types configured</DropdownMenuItem>
              ) : (
                vehicleTypes.map((vt) => (
                  <DropdownMenuCheckboxItem
                    key={vt.id}
                    checked={typeFilter.includes(String(vt.id))}
                    onCheckedChange={() => toggleType(String(vt.id))}
                  >
                    {vt.name}
                  </DropdownMenuCheckboxItem>
                ))
              )}
              {typeFilter.length > 0 && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => setTypeFilter([])} className="text-muted-foreground text-xs">
                    Clear
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Vehicle Status filter */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className={`h-8 text-sm gap-1 ${statusFilter.length > 0 ? "border-primary text-primary" : ""}`}>
                Vehicle Status
                {statusFilter.length > 0 && <span className="bg-primary text-primary-foreground rounded-full text-xs px-1.5">{statusFilter.length}</span>}
                <ChevronDown className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-48">
              {STATUSES.map((s) => (
                <DropdownMenuCheckboxItem
                  key={s}
                  checked={statusFilter.includes(s)}
                  onCheckedChange={() => toggleStatus(s)}
                  className="capitalize"
                >
                  {s}
                </DropdownMenuCheckboxItem>
              ))}
              {statusFilter.length > 0 && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => setStatusFilter([])} className="text-muted-foreground text-xs">
                    Clear
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* More filters */}
          <Button variant="outline" size="sm" className="h-8 text-sm gap-1">
            <SlidersHorizontal className="h-3.5 w-3.5" />
            Filters
          </Button>
        </div>

        {/* Pagination counter + settings */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground shrink-0">
          {total > 0 && (
            <span>{start}–{end} of {total}</span>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
            <Settings2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
              <p className="mt-2 text-muted-foreground text-sm">Loading vehicles...</p>
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <Truck className="h-12 w-12 text-muted-foreground/30 mb-4" />
            <p className="font-medium text-muted-foreground">No vehicles found</p>
            {hasFilters ? (
              <Button variant="link" size="sm" onClick={clearFilters}>Clear filters</Button>
            ) : (
              <Button asChild size="sm" className="mt-3">
                <Link to="/vehicles/add"><Plus className="h-4 w-4 mr-1" />Add Vehicle</Link>
              </Button>
            )}
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/40 hover:bg-muted/40">
                <TableHead className="w-10 pl-6">
                  <input type="checkbox" className="rounded border-gray-300" />
                </TableHead>
                <TableHead>Registration</TableHead>
                <TableHead>Make / Model</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Driver</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Fuel</TableHead>
                <TableHead>Odometer</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-10 pr-6" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((vehicle) => {
                const status = vehicle.vehicle_status || vehicle.status || "idle";
                const typeName = vehicleTypes.find((t) => t.id === vehicle.vehicle_type_id)?.name;
                return (
                  <TableRow key={vehicle.id} className="group hover:bg-muted/30">
                    <TableCell className="pl-6">
                      <input type="checkbox" className="rounded border-gray-300" />
                    </TableCell>
                    <TableCell>
                      <Link
                        to={`/vehicles/edit/${vehicle.id}`}
                        className="font-medium text-primary hover:underline"
                      >
                        {vehicle.registration_number}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{vehicle.make}</div>
                      <div className="text-xs text-muted-foreground">{vehicle.model_name || vehicle.model}</div>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-muted-foreground">{typeName || "—"}</span>
                    </TableCell>
                    <TableCell>
                      {vehicle.driver_name ? (
                        <span className="text-sm">{vehicle.driver_name}</span>
                      ) : (
                        <span className="text-xs text-muted-foreground italic">Unassigned</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-muted-foreground">{vehicle.department || "—"}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-muted-foreground capitalize">{vehicle.fuel_type || "—"}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm text-muted-foreground">
                        {vehicle.current_odometer != null
                          ? `${Number(vehicle.current_odometer).toLocaleString()} km`
                          : "—"}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge className={`text-xs capitalize ${STATUS_COLORS[status] || "bg-gray-100 text-gray-800"}`}>
                        {status}
                      </Badge>
                    </TableCell>
                    <TableCell className="pr-6">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => navigate(`/vehicles/edit/${vehicle.id}`)}>
                            <Pencil className="h-3.5 w-3.5 mr-2" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive"
                            onClick={() => handleDelete(vehicle)}
                          >
                            <Trash2 className="h-3.5 w-3.5 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </div>

      {/* Bottom pagination bar */}
      {!isLoading && filtered.length > 0 && (
        <div className="flex items-center justify-between px-6 py-3 border-t text-sm text-muted-foreground">
          <span>{filtered.length} vehicle{filtered.length !== 1 ? "s" : ""} shown</span>
          <div className="flex items-center gap-1">
            <Button variant="outline" size="sm" className="h-7" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              <ChevronLeft className="h-3.5 w-3.5 mr-1" />Previous
            </Button>
            <span className="px-3 text-xs">Page {page} of {totalPages || 1}</span>
            <Button variant="outline" size="sm" className="h-7" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              Next<ChevronRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Vehicles;
