import { MapOverview } from "@/components/MapOverview";
import { TruckCapacity } from "@/components/TruckCapacity";
import { DriverChat } from "@/components/DriverChat";
import { TrackingDetails } from "@/components/TrackingDetails";
import { CargoPhotoReports } from "@/components/CargoPhotoReports";

const Tracking = () => {
  return (
    <main className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
      <div className="lg:col-span-2 flex flex-col gap-6">
        <div className="h-[45vh] min-h-[400px]">
          <MapOverview />
        </div>
        <TrackingDetails />
        <CargoPhotoReports />
      </div>
      <div className="lg:col-span-1 flex flex-col gap-6">
        <TruckCapacity />
        <DriverChat />
      </div>
    </main>
  );
};

export default Tracking;
