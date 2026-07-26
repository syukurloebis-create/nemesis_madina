import { BaseArtifact } from './BaseArtifact.js';  // ✅ Correct

/**
 * Architecture fingerprint - checksum-based ABI detection
 */
export interface ArchitectureFingerprint extends BaseArtifact {
  /** ABI version */
  abiVersion: string;
  
  /** Contract signatures hash */
  contracts: string;
  
  /** SPI signatures hash */
  spi: string;
  
  /** Manifest schema hash */
  manifest: string;
  
  /** Enum definitions hash */
  enums: string;
}