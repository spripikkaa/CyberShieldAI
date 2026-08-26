import type { PredictionLabel } from "../types/scan";

export function getSecurityRecommendation(
  prediction: PredictionLabel,
  confidence: number,
): string {
  const confidencePercent = Math.round(confidence * 100);

  if (prediction === "Phishing") {
    if (confidence >= 0.85) {
      return `High-risk phishing detected (${confidencePercent}% confidence). Do not enter credentials, download files, or share personal information on this site. Block the URL, report it to your security team, and warn others who may have received the link.`;
    }
    if (confidence >= 0.65) {
      return `This URL shows strong phishing indicators (${confidencePercent}% confidence). Avoid interacting with the page until it has been verified by your security team. Use official channels to access the service instead of this link.`;
    }
    return `Suspicious patterns were found (${confidencePercent}% confidence). Treat this link as potentially malicious: verify the sender, inspect the domain carefully, and do not submit sensitive data unless you can confirm legitimacy through a trusted source.`;
  }

  if (confidence >= 0.85) {
    return `This URL appears legitimate (${confidencePercent}% confidence). Standard browsing precautions still apply: confirm the domain matches the service you expect, keep your browser updated, and avoid entering credentials on unfamiliar pages.`;
  }
  if (confidence >= 0.65) {
    return `No major phishing signals were detected (${confidencePercent}% confidence), but some uncertainty remains. Proceed carefully, double-check the URL spelling, and prefer navigating directly to known websites when handling sensitive information.`;
  }
  return `The scan did not flag this URL as phishing (${confidencePercent}% confidence), but confidence is moderate. Verify the site through official bookmarks or search results before sharing passwords, payment details, or personal data.`;
}

export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}
