import { apiGet } from "./client";
import type { DnsResult, ExplainResult, SslResult, WhoisResult } from "../types/security";

function urlParam(url: string): string {
  return new URLSearchParams({ url }).toString();
}

export async function fetchWhois(url: string): Promise<WhoisResult> {
  return apiGet<WhoisResult>(`/whois?${urlParam(url)}`);
}

export async function fetchSsl(url: string): Promise<SslResult> {
  return apiGet<SslResult>(`/ssl?${urlParam(url)}`);
}

export async function fetchDns(url: string): Promise<DnsResult> {
  return apiGet<DnsResult>(`/dns?${urlParam(url)}`);
}

export async function fetchExplain(url: string): Promise<ExplainResult> {
  return apiGet<ExplainResult>(`/explain?${urlParam(url)}`);
}
