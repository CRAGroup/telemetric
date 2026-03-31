import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useAdminSettings() {
  const queryClient = useQueryClient();

  const { data: settings, isLoading: loading, error } = useQuery({
    queryKey: ['admin-settings'],
    queryFn: () => apiClient.getCompanySettings(),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: 1,
  });

  const updateMutation = useMutation({
    mutationFn: (updates: any) => apiClient.updateSettings(updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-settings'] });
    },
  });

  const updateSettings = async (updates: any) => {
    return updateMutation.mutateAsync(updates);
  };

  const uploadLogo = async (_file: File): Promise<string> => {
    // Logo upload requires file storage - not yet implemented
    throw new Error('Logo upload requires file storage configuration');
  };

  return {
    settings,
    loading,
    error: error?.message || null,
    updateSettings,
    uploadLogo,
    refetch: () => queryClient.invalidateQueries({ queryKey: ['admin-settings'] }),
  };
}
