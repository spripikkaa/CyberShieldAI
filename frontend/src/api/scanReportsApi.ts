import { apiGet } from "./client";
import type { ScanReport } from "../types/security";

export async function fetchScanReports(
  userId: string,
  limit = 50,
): Promise<ScanReport[]> {
  const params = new URLSearchParams({
    user_id: userId,
    limit: String(limit),
  });
  return apiGet<ScanReport[]>(`/scan-reports?${params.toString()}`);
}
