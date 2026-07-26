import { ProviderDescriptor } from '@nemesis/contracts-provider';
import { ProviderProvenance, BuildMetadata } from './ProviderProvenance.js';

/**
 * Provider manifest - build/deployment artifact
 * Contains governance metadata (provenance, signature, etc.)
 * NOT part of runtime ABI
 */
export interface ProviderManifest {
  descriptor: ProviderDescriptor;
  provenance: ProviderProvenance;
  buildMetadata: BuildMetadata;
  signature?: string;
  signatureAlgorithm?: 'SHA256' | 'SHA384' | 'SHA512' | 'ECDSA' | 'RSA-PSS';
}