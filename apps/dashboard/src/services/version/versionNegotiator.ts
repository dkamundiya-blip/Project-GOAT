/**
 * Project GOAT v1.0 — Version Compatibility & Negotiation Engine
 */

export interface VersionInfo {
  dashboardVersion: string;
  backendVersion: string;
  schemaVersion: string;
  protocolVersion: string;
}

export interface VersionVerificationResult {
  isCompatible: boolean;
  message: string;
  details: VersionInfo;
}

export class VersionNegotiator {
  private readonly SUPPORTED_BACKEND_VERSION = '0.9.1';
  private readonly SUPPORTED_PROTOCOL_VERSION = '1.0';

  verifyCompatibility(backendInfo: Partial<VersionInfo>): VersionVerificationResult {
    const details: VersionInfo = {
      dashboardVersion: '1.0.0',
      backendVersion: backendInfo.backendVersion || '0.9.1',
      schemaVersion: backendInfo.schemaVersion || '1.0.0',
      protocolVersion: backendInfo.protocolVersion || '1.0',
    };

    const isBackendMatch = details.backendVersion === this.SUPPORTED_BACKEND_VERSION;
    const isProtocolMatch = details.protocolVersion === this.SUPPORTED_PROTOCOL_VERSION;

    if (!isBackendMatch) {
      return {
        isCompatible: false,
        message: `Incompatible backend version ${details.backendVersion}. Required: ${this.SUPPORTED_BACKEND_VERSION}`,
        details,
      };
    }

    if (!isProtocolMatch) {
      return {
        isCompatible: false,
        message: `Incompatible protocol version ${details.protocolVersion}. Required: ${this.SUPPORTED_PROTOCOL_VERSION}`,
        details,
      };
    }

    return {
      isCompatible: true,
      message: 'Version negotiation successful. Dashboard and backend fully compatible.',
      details,
    };
  }
}

export const versionNegotiator = new VersionNegotiator();
