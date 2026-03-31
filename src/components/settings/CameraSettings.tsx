import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { useToast } from "@/components/ui/use-toast";
import { Camera, Video, Brain, Cloud, HardDrive, AlertTriangle, Eye, Activity } from "lucide-react";
import { Separator } from "@/components/ui/separator";

export function CameraSettings() {
  const { toast } = useToast();
  
  const [settings, setSettings] = useState({
    // Camera enabled
    cameraEnabled: true,
    
    // Video quality
    resolution: "1080p",
    bitrate: 2000,
    frameRate: 30,
    
    // Upload settings
    uploadMode: "on-event",
    uploadQuality: "high",
    
    // AI Detection
    aiEnabled: true,
    driverDrowsiness: true,
    laneDeparture: true,
    distractedDriving: true,
    collisionWarning: true,
    speedingAlert: true,
    harshBraking: false,
    
    // Storage
    storageDuration: 30,
    cloudProvider: "s3",
    localBackup: true,
    
    // Advanced
    nightVision: true,
    audioRecording: false,
    gpsOverlay: true,
    timestampOverlay: true,
  });

  const handleSave = () => {
    // Save to backend
    toast({
      title: "Camera settings saved",
      description: "Your camera and video settings have been updated successfully.",
    });
  };

  const handleToggle = (key: keyof typeof settings) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key as keyof typeof prev]
    }));
  };

  const handleSelectChange = (key: keyof typeof settings, value: string) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="space-y-6">
      {/* Camera Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Camera className="h-5 w-5" />
              <CardTitle>Camera System</CardTitle>
            </div>
            <Switch
              checked={settings.cameraEnabled}
              onCheckedChange={() => handleToggle("cameraEnabled")}
            />
          </div>
          <CardDescription>
            Enable or disable the onboard camera system for all vehicles
          </CardDescription>
        </CardHeader>
      </Card>

      {settings.cameraEnabled && (
        <>
          {/* Video Quality Settings */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Video className="h-5 w-5" />
                <CardTitle>Video Quality</CardTitle>
              </div>
              <CardDescription>
                Configure video resolution and recording quality
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Video Resolution</Label>
                <Select
                  value={settings.resolution}
                  onValueChange={(value) => handleSelectChange("resolution", value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="720p">720p (HD) - 1280x720</SelectItem>
                    <SelectItem value="1080p">1080p (Full HD) - 1920x1080</SelectItem>
                    <SelectItem value="1440p">1440p (2K) - 2560x1440</SelectItem>
                    <SelectItem value="2160p">2160p (4K) - 3840x2160</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Higher resolution provides better quality but uses more storage
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Video Bitrate</Label>
                  <span className="text-sm text-muted-foreground">{settings.bitrate} kbps</span>
                </div>
                <Slider
                  value={[settings.bitrate]}
                  onValueChange={(value) => setSettings(prev => ({ ...prev, bitrate: value[0] }))}
                  min={500}
                  max={8000}
                  step={500}
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground">
                  Recommended: 2000-4000 kbps for 1080p
                </p>
              </div>

              <div className="space-y-2">
                <Label>Frame Rate</Label>
                <Select
                  value={settings.frameRate.toString()}
                  onValueChange={(value) => setSettings(prev => ({ ...prev, frameRate: parseInt(value) }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="15">15 FPS (Low)</SelectItem>
                    <SelectItem value="24">24 FPS (Standard)</SelectItem>
                    <SelectItem value="30">30 FPS (Recommended)</SelectItem>
                    <SelectItem value="60">60 FPS (High)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Upload Settings */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                <CardTitle>Upload Settings</CardTitle>
              </div>
              <CardDescription>
                Configure when and how videos are uploaded to the cloud
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Upload Mode</Label>
                <Select
                  value={settings.uploadMode}
                  onValueChange={(value) => handleSelectChange("uploadMode", value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="realtime">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Real-time</span>
                        <span className="text-xs text-muted-foreground">Continuous streaming (high bandwidth)</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="on-event">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">On Event</span>
                        <span className="text-xs text-muted-foreground">Upload when AI detects incidents (recommended)</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="periodic">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Periodic</span>
                        <span className="text-xs text-muted-foreground">Upload at scheduled intervals</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="manual">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Manual</span>
                        <span className="text-xs text-muted-foreground">Upload only when requested</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {settings.uploadMode === "periodic" && (
                <div className="space-y-2">
                  <Label>Upload Interval</Label>
                  <Select defaultValue="hourly">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="15min">Every 15 minutes</SelectItem>
                      <SelectItem value="30min">Every 30 minutes</SelectItem>
                      <SelectItem value="hourly">Every hour</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div className="space-y-2">
                <Label>Upload Quality</Label>
                <Select
                  value={settings.uploadQuality}
                  onValueChange={(value) => handleSelectChange("uploadQuality", value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low (Compressed)</SelectItem>
                    <SelectItem value="medium">Medium (Balanced)</SelectItem>
                    <SelectItem value="high">High (Original Quality)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* AI Detection Rules */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                <CardTitle>AI Detection Rules</CardTitle>
              </div>
              <CardDescription>
                Configure AI-powered safety and monitoring features
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Eye className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <Label htmlFor="ai-enabled">Enable AI Detection</Label>
                    <p className="text-sm text-muted-foreground">
                      Master switch for all AI features
                    </p>
                  </div>
                </div>
                <Switch
                  id="ai-enabled"
                  checked={settings.aiEnabled}
                  onCheckedChange={() => handleToggle("aiEnabled")}
                />
              </div>

              {settings.aiEnabled && (
                <>
                  <Separator />
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="drowsiness">Driver Drowsiness Detection</Label>
                        <p className="text-sm text-muted-foreground">
                          Detect signs of fatigue and drowsiness
                        </p>
                      </div>
                      <Switch
                        id="drowsiness"
                        checked={settings.driverDrowsiness}
                        onCheckedChange={() => handleToggle("driverDrowsiness")}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="lane-departure">Lane Departure Warning</Label>
                        <p className="text-sm text-muted-foreground">
                          Alert when vehicle drifts from lane
                        </p>
                      </div>
                      <Switch
                        id="lane-departure"
                        checked={settings.laneDeparture}
                        onCheckedChange={() => handleToggle("laneDeparture")}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="distracted">Distracted Driving Detection</Label>
                        <p className="text-sm text-muted-foreground">
                          Detect phone use, eating, or other distractions
                        </p>
                      </div>
                      <Switch
                        id="distracted"
                        checked={settings.distractedDriving}
                        onCheckedChange={() => handleToggle("distractedDriving")}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="collision">Collision Warning</Label>
                        <p className="text-sm text-muted-foreground">
                          Forward collision and obstacle detection
                        </p>
                      </div>
                      <Switch
                        id="collision"
                        checked={settings.collisionWarning}
                        onCheckedChange={() => handleToggle("collisionWarning")}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="speeding">Speeding Alert</Label>
                        <p className="text-sm text-muted-foreground">
                          Alert when exceeding speed limits
                        </p>
                      </div>
                      <Switch
                        id="speeding"
                        checked={settings.speedingAlert}
                        onCheckedChange={() => handleToggle("speedingAlert")}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="harsh-braking">Harsh Braking Detection</Label>
                        <p className="text-sm text-muted-foreground">
                          Detect sudden or aggressive braking
                        </p>
                      </div>
                      <Switch
                        id="harsh-braking"
                        checked={settings.harshBraking}
                        onCheckedChange={() => handleToggle("harshBraking")}
                      />
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Storage Settings */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <HardDrive className="h-5 w-5" />
                <CardTitle>Storage Settings</CardTitle>
              </div>
              <CardDescription>
                Configure video storage duration and location
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Storage Duration</Label>
                <Select
                  value={settings.storageDuration.toString()}
                  onValueChange={(value) => setSettings(prev => ({ ...prev, storageDuration: parseInt(value) }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7">7 Days</SelectItem>
                    <SelectItem value="14">14 Days</SelectItem>
                    <SelectItem value="30">30 Days (Recommended)</SelectItem>
                    <SelectItem value="60">60 Days</SelectItem>
                    <SelectItem value="90">90 Days</SelectItem>
                    <SelectItem value="180">180 Days</SelectItem>
                    <SelectItem value="365">1 Year</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Videos older than this will be automatically deleted
                </p>
              </div>

              <div className="space-y-2">
                <Label>Cloud Storage Provider</Label>
                <Select
                  value={settings.cloudProvider}
                  onValueChange={(value) => handleSelectChange("cloudProvider", value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="s3">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Amazon S3</span>
                        <span className="text-xs text-muted-foreground">Reliable, scalable cloud storage</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="wasabi">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Wasabi</span>
                        <span className="text-xs text-muted-foreground">Cost-effective S3-compatible storage</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="minio">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">MinIO</span>
                        <span className="text-xs text-muted-foreground">Self-hosted object storage</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="azure">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Azure Blob Storage</span>
                        <span className="text-xs text-muted-foreground">Microsoft cloud storage</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="gcs">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Google Cloud Storage</span>
                        <span className="text-xs text-muted-foreground">Google's object storage</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="local-backup">Local Backup</Label>
                  <p className="text-sm text-muted-foreground">
                    Keep a copy on vehicle's local storage
                  </p>
                </div>
                <Switch
                  id="local-backup"
                  checked={settings.localBackup}
                  onCheckedChange={() => handleToggle("localBackup")}
                />
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <div className="flex items-start gap-3">
                  <Cloud className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Estimated Storage Cost</p>
                    <p className="text-xs text-muted-foreground">
                      Based on 10 vehicles, {settings.resolution}, {settings.storageDuration} days retention
                    </p>
                    <p className="text-lg font-bold text-primary">~$45/month</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Advanced Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
              <CardDescription>
                Additional camera and recording options
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="night-vision">Night Vision Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Enhanced recording in low light conditions
                  </p>
                </div>
                <Switch
                  id="night-vision"
                  checked={settings.nightVision}
                  onCheckedChange={() => handleToggle("nightVision")}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="audio">Audio Recording</Label>
                  <p className="text-sm text-muted-foreground">
                    Record audio along with video
                  </p>
                </div>
                <Switch
                  id="audio"
                  checked={settings.audioRecording}
                  onCheckedChange={() => handleToggle("audioRecording")}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="gps-overlay">GPS Overlay</Label>
                  <p className="text-sm text-muted-foreground">
                    Show location and speed on video
                  </p>
                </div>
                <Switch
                  id="gps-overlay"
                  checked={settings.gpsOverlay}
                  onCheckedChange={() => handleToggle("gpsOverlay")}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="timestamp">Timestamp Overlay</Label>
                  <p className="text-sm text-muted-foreground">
                    Display date and time on video
                  </p>
                </div>
                <Switch
                  id="timestamp"
                  checked={settings.timestampOverlay}
                  onCheckedChange={() => handleToggle("timestampOverlay")}
                />
              </div>
            </CardContent>
          </Card>

          {/* Warning Card */}
          <Card className="border-warning">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-warning mt-0.5" />
                <div className="space-y-1">
                  <p className="text-sm font-medium">Important Notes</p>
                  <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
                    <li>Higher quality settings require more bandwidth and storage</li>
                    <li>AI features require compatible camera hardware</li>
                    <li>Real-time streaming may impact vehicle connectivity</li>
                    <li>Ensure compliance with local privacy laws when recording</li>
                    <li>Regular maintenance of camera equipment is recommended</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-3">
            <Button variant="outline">Test Camera</Button>
            <Button onClick={handleSave}>Save Settings</Button>
          </div>
        </>
      )}
    </div>
  );
}
