import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import {
  FileText,
  Download,
  TrendingUp,
  BarChart3,
  PieChart,
  Loader2,
} from "lucide-react";

const Reports = () => {
  const { toast } = useToast();
  const [selectedPeriod, setSelectedPeriod] = useState("this_month");
  const [generatedReports, setGeneratedReports] = useState<any[]>([]);

  const { data: templatesData } = useQuery({
    queryKey: ["report-templates"],
    queryFn: () => apiClient.getReportTemplates(),
  });

  const { data: vehicles } = useQuery({
    queryKey: ["vehicles-list"],
    queryFn: () => apiClient.getVehicles({ page_size: 200 }),
  });

  const generateMutation = useMutation({
    mutationFn: (reportType: string) => {
      const now = new Date();
      const start = new Date();
      if (selectedPeriod === "this_week") start.setDate(now.getDate() - 7);
      else if (selectedPeriod === "this_month") start.setMonth(now.getMonth() - 1);
      else if (selectedPeriod === "last_month") { start.setMonth(now.getMonth() - 2); now.setMonth(now.getMonth() - 1); }
      else if (selectedPeriod === "this_quarter") start.setMonth(now.getMonth() - 3);
      else start.setMonth(now.getMonth() - 1);

      return apiClient.generateReport({
        report_type: reportType,
        format: "csv",
        start: start.toISOString(),
        end: now.toISOString(),
        title: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`,
      });
    },
    onSuccess: (data, reportType) => {
      const newReport = {
        id: data.id,
        name: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`,
        type: reportType,
        status: "ready",
        generatedDate: new Date().toLocaleDateString(),
        period: selectedPeriod.replace("_", " "),
      };
      setGeneratedReports((prev) => [newReport, ...prev]);
      toast({ title: "Report generated successfully" });
    },
    onError: (e: any) => toast({ title: "Error generating report", description: e.message, variant: "destructive" }),
  });

  const downloadMutation = useMutation({
    mutationFn: async (reportId: string) => {
      const blob = await apiClient.downloadReport(reportId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${reportId}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    },
    onError: (e: any) => toast({ title: "Download failed", description: e.message, variant: "destructive" }),
  });

  const templates = templatesData?.templates || [];

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "fleet": return <BarChart3 className="w-4 h-4" />;
      case "fuel": return <PieChart className="w-4 h-4" />;
      case "cost": return <TrendingUp className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reports & Analytics</h1>
          <p className="text-muted-foreground">Generate and download fleet performance reports</p>
        </div>
        <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Time Period" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="this_week">This Week</SelectItem>
            <SelectItem value="this_month">This Month</SelectItem>
            <SelectItem value="last_month">Last Month</SelectItem>
            <SelectItem value="this_quarter">This Quarter</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-blue-500" />
              <div>
                <p className="text-sm font-medium">Generated</p>
                <p className="text-2xl font-bold">{generatedReports.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4 text-green-500" />
              <div>
                <p className="text-sm font-medium">Vehicles</p>
                <p className="text-2xl font-bold">{vehicles?.total || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-orange-500" />
              <div>
                <p className="text-sm font-medium">Templates</p>
                <p className="text-2xl font-bold">{templates.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Download className="h-4 w-4 text-purple-500" />
              <div>
                <p className="text-sm font-medium">Downloads</p>
                <p className="text-2xl font-bold">{generatedReports.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Reports</CardTitle></CardHeader>
        <CardContent>
          <Tabs defaultValue="templates">
            <TabsList>
              <TabsTrigger value="templates">Templates</TabsTrigger>
              <TabsTrigger value="recent">Generated ({generatedReports.length})</TabsTrigger>
            </TabsList>

            <TabsContent value="templates" className="mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {templates.map((template) => (
                  <Card key={template.key} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-3 mb-3">
                        {getTypeIcon(template.key)}
                        <h3 className="font-semibold">{template.name}</h3>
                      </div>
                      <p className="text-sm text-muted-foreground mb-4">
                        Generate {template.name.toLowerCase()} analysis for {selectedPeriod.replace("_", " ")}
                      </p>
                      <Button
                        size="sm"
                        className="w-full"
                        onClick={() => generateMutation.mutate(template.key)}
                        disabled={generateMutation.isPending}
                      >
                        {generateMutation.isPending && generateMutation.variables === template.key ? (
                          <><Loader2 className="w-3 h-3 mr-2 animate-spin" />Generating...</>
                        ) : (
                          "Generate Report"
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="recent" className="mt-4">
              {generatedReports.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-30" />
                  <p>No reports generated yet. Use the Templates tab to generate one.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {generatedReports.map((report) => (
                    <div key={report.id} className="border rounded-lg p-4 flex items-center justify-between">
                      <div className="flex items-start space-x-3">
                        {getTypeIcon(report.type)}
                        <div>
                          <h3 className="font-semibold">{report.name}</h3>
                          <div className="flex items-center space-x-3 text-xs text-muted-foreground mt-1">
                            <span>Period: {report.period}</span>
                            <span>Generated: {report.generatedDate}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-green-100 text-green-800">{report.status}</Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => downloadMutation.mutate(report.id)}
                          disabled={downloadMutation.isPending}
                        >
                          {downloadMutation.isPending ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <Download className="w-3 h-3" />
                          )}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;
